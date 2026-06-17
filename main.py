import os
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import psycopg
from psycopg.rows import dict_row
from datetime import date, datetime
import json

app = FastAPI(title="Tailor Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB_CONFIG = {
#     "host": "localhost",
#     "database": "tailor_db",
#     "user": "postgres",
#     "password": "password",
#     "port": 5432
# }

DATABASE_URL = os.getenv("DATABASE_URL")

result = urlparse(DATABASE_URL)

DB_CONFIG = {
    "host": result.hostname,
    "database": result.path[1:],
    "user": result.username,
    "password": result.password,
    "port": result.port
}

def get_conn():
    return psycopg.connect(
        host=DB_CONFIG["host"],
        dbname=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"],
        row_factory=dict_row
    )

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS item_prices (
            id SERIAL PRIMARY KEY,
            item_name VARCHAR(100) UNIQUE NOT NULL,
            price DECIMAL(10,2) NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            phone VARCHAR(20),
            address TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            customer_name VARCHAR(200),
            phone VARCHAR(20),
            address TEXT,
            order_date DATE DEFAULT CURRENT_DATE,
            delivery_date DATE,
            status VARCHAR(50) DEFAULT 'Incomplete',
            total_amount DECIMAL(10,2) DEFAULT 0,
            advance_paid DECIMAL(10,2) DEFAULT 0,
            remaining_amount DECIMAL(10,2) DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
            item_type VARCHAR(100) NOT NULL,
            quantity INTEGER DEFAULT 1,
            unit_price DECIMAL(10,2) DEFAULT 0,
            total_price DECIMAL(10,2) DEFAULT 0,
            measurements JSONB DEFAULT '{}'
        )
    """)
    
    # Default items for women's wear
    default_items = [
        ("Kurti", 500),
        ("Blouse", 300),
        ("Salwar", 400),
        ("Dupatta", 200),
        ("Lehenga", 1500),
        ("Saree Blouse", 350),
        ("Anarkali", 800),
        ("Palazzo", 450),
        ("Sharara", 600),
        ("Gown", 1200),
        ("Crop Top", 300),
        ("Jacket", 700),
        ("Churidar", 350),
        ("Pant", 400),
        ("Skirt", 350),
    ]
    
    for item_name, price in default_items:
        cur.execute("""
            INSERT INTO item_prices (item_name, price)
            VALUES (%s, %s)
            ON CONFLICT (item_name) DO NOTHING
        """, (item_name, price))
    
    conn.commit()
    cur.close()
    conn.close()

# ─── Models ───────────────────────────────────────────────────────────────────

class ItemPrice(BaseModel):
    item_name: str
    price: float

class OrderItemIn(BaseModel):
    item_type: str
    quantity: int = 1
    unit_price: Optional[float] = None
    measurements: Optional[dict] = {}

class OrderIn(BaseModel):
    customer_name: str
    phone: Optional[str] = ""
    address: Optional[str] = ""
    delivery_date: Optional[str] = None
    advance_paid: float = 0
    notes: Optional[str] = ""
    items: List[OrderItemIn] = []

class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    delivery_date: Optional[str] = None
    status: Optional[str] = None
    advance_paid: Optional[float] = None
    notes: Optional[str] = None

# ─── Item Prices ──────────────────────────────────────────────────────────────

@app.get("/prices")
def get_prices():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM item_prices ORDER BY item_name")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in rows]

@app.post("/prices")
def add_or_update_price(data: ItemPrice):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO item_prices (item_name, price)
        VALUES (%s, %s)
        ON CONFLICT (item_name) DO UPDATE SET price = EXCLUDED.price, updated_at = NOW()
        RETURNING *
    """, (data.item_name, data.price))
    row = cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return dict(row)

# ─── Orders ───────────────────────────────────────────────────────────────────

@app.get("/orders")
def get_orders(status: Optional[str] = None):
    conn = get_conn()
    cur = conn.cursor()
    if status:
        cur.execute("SELECT * FROM orders WHERE status = %s ORDER BY created_at DESC", (status,))
    else:
        cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in rows]

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cur.fetchone()
    if not order:
        raise HTTPException(404, "Order not found")
    cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
    items = cur.fetchall()
    cur.close(); conn.close()
    result = dict(order)
    result["items"] = [dict(i) for i in items]
    return result

@app.post("/orders")
def create_order(data: OrderIn):
    conn = get_conn()
    cur = conn.cursor()
    
    # Fetch prices for auto-fill
    cur.execute("SELECT item_name, price FROM item_prices")
    price_map = {r["item_name"]: float(r["price"]) for r in cur.fetchall()}
    
    total = 0
    processed_items = []
    for item in data.items:
        unit_price = item.unit_price if item.unit_price is not None else price_map.get(item.item_type, 0)
        item_total = unit_price * item.quantity
        total += item_total
        processed_items.append({
            "item_type": item.item_type,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "total_price": item_total,
            "measurements": item.measurements or {}
        })
    
    remaining = total - data.advance_paid
    
    cur.execute("""
        INSERT INTO orders (customer_name, phone, address, delivery_date, total_amount, advance_paid, remaining_amount, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """, (data.customer_name, data.phone, data.address, data.delivery_date,
          total, data.advance_paid, remaining, data.notes))
    order = dict(cur.fetchone())
    order_id = order["id"]
    
    for item in processed_items:
        cur.execute("""
            INSERT INTO order_items (order_id, item_type, quantity, unit_price, total_price, measurements)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order_id, item["item_type"], item["quantity"], item["unit_price"],
              item["total_price"], json.dumps(item["measurements"])))
    
    conn.commit()
    cur.close(); conn.close()
    order["items"] = processed_items
    return order

@app.put("/orders/{order_id}")
def update_order(order_id: int, data: OrderUpdate):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cur.fetchone()
    if not order:
        raise HTTPException(404, "Order not found")
    order = dict(order)
    
    updates = {k: v for k, v in data.dict().items() if v is not None}
    if "advance_paid" in updates:
        updates["remaining_amount"] = float(order["total_amount"]) - updates["advance_paid"]
    
    if updates:
        set_clause = ", ".join(f"{k} = %s" for k in updates)
        values = list(updates.values()) + [order_id]
        cur.execute(f"UPDATE orders SET {set_clause}, updated_at = NOW() WHERE id = %s RETURNING *", values)
        order = dict(cur.fetchone())
    
    conn.commit(); cur.close(); conn.close()
    return order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit(); cur.close(); conn.close()
    return {"message": "Order deleted"}

# ─── Dashboard Stats ──────────────────────────────────────────────────────────

@app.get("/dashboard")
def get_dashboard():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as total FROM orders")
    total = cur.fetchone()["total"]
    
    cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE status = 'Complete'")
    complete = cur.fetchone()["cnt"]
    
    cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE status = 'Incomplete'")
    incomplete = cur.fetchone()["cnt"]
    
    cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE delivery_date = CURRENT_DATE")
    today_delivery = cur.fetchone()["cnt"]
    
    cur.execute("SELECT COALESCE(SUM(total_amount),0) as total FROM orders")
    total_revenue = cur.fetchone()["total"]
    
    cur.execute("SELECT COALESCE(SUM(remaining_amount),0) as total FROM orders WHERE remaining_amount > 0")
    pending_amount = cur.fetchone()["total"]
    
    cur.execute("SELECT COALESCE(SUM(advance_paid),0) as total FROM orders")
    total_advance = cur.fetchone()["total"]
    
    cur.execute("""
        SELECT item_type, SUM(quantity) as count
        FROM order_items GROUP BY item_type ORDER BY count DESC LIMIT 5
    """)
    top_items = [dict(r) for r in cur.fetchall()]
    
    cur.execute("""
        SELECT order_date::text as date, COUNT(*) as orders, SUM(total_amount) as revenue
        FROM orders
        WHERE order_date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY order_date ORDER BY order_date
    """)
    weekly = [dict(r) for r in cur.fetchall()]
    
    cur.close(); conn.close()
    return {
        "total_orders": total,
        "complete": complete,
        "incomplete": incomplete,
        "today_delivery": today_delivery,
        "total_revenue": float(total_revenue),
        "pending_amount": float(pending_amount),
        "total_advance": float(total_advance),
        "top_items": top_items,
        "weekly_data": weekly
    }

@app.on_event("startup")
def startup():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
