# ✂️ Tailor Management System

<div align="center">

**A full-stack business management solution built for modern tailoring shops**
Streamline orders, track payments, manage measurements and many more that too all in one place.

</div>

---

## 📌 Overview

The **Tailor Management System** is a desktop-ready web application designed specifically for women's wear tailoring businesses. It replaces paper registers and Excel sheets with a clean, fast, and reliable digital workflow that is from taking a new order to tracking final delivery and payment.

Built with a **FastAPI** REST backend, **Streamlit** UI frontend, and **PostgreSQL** database, the system handles everything a tailor shop needs day-to-day.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📊 **Dashboard** | Live stats — total orders, revenue, pending payments, weekly chart, top items |
| ➕ **New Order** | Add customer details, select multiple garment types, enter measurements |
| 💰 **Auto Pricing** | Prices auto-fill from database when an item is selected |
| 📏 **Measurements** | Dynamic measurement fields (bust, waist, hip, sleeve, length etc.) per garment |
| 💳 **Payment Tracking** | Enter advance → remaining balance calculated and stored automatically |
| 📋 **Order Management** | Filter by status, search by name, view today's deliveries |
| ✏️ **Order Updates** | Edit status, payment, delivery date — all synced to database in real time |
| 🏷️ **Price Management** | Add new garment types or update prices anytime from the UI |

---

## 🗂️ Project Structure

```
tailor-management-system/
│
├── main.py            # FastAPI backend — REST API + DB initialization
├── app.py             # Streamlit frontend — all UI pages
├── requirements.txt   # Python dependencies
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **Backend** | FastAPI + Uvicorn |
| **Database** | PostgreSQL |
| **DB Driver** | psycopg2 |
| **Data Handling** | Pandas |
| **Validation** | Pydantic v2 |

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- pip

---

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/tailor-management-system.git
cd tailor-management-system
```

### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL Database

Open **pgAdmin** or **psql** and run:

```sql
CREATE DATABASE tailor_db;
```

> Default DB credentials used in the app:
>
> | Field | Value |
> |---|---|
> | Host | `localhost` |
> | Database | `tailor_db` |
> | User | `postgres` |
> | Password | `your_password` |
> | Port | `5432` |
>
> To change these, edit `DB_CONFIG` in `main.py`.

All tables and default item prices are **created automatically** on first run — no manual SQL needed.

---

### 5. Run the Backend

```bash
python main.py
```

- API: `http://localhost:8000`
- Interactive API Docs: `http://localhost:8000/docs`

---

### 6. Run the Frontend

Open a **second terminal** (with the virtual environment activated):

```bash
streamlit run app.py or python -m streamlit run app.py
```

- App: `http://localhost:8501`

---

## Step-by-Step Deployment

1. Create a Railway Project


Go to railway.app → New Project → Deploy from GitHub


2. Deploy FastAPI Backend


Select your repo → Railway auto-detects Python
Settings → Start Command:


  uvicorn main:app --host 0.0.0.0 --port $PORT


Add PostgreSQL: + New → Database → PostgreSQL
Variables → New Variable:


  DATABASE_URL = ${{Postgres.DATABASE_URL}}


Settings → Networking → Generate Domain → copy the URL


3. Deploy Streamlit Frontend


Same project → + New → GitHub Repo → same repo
Settings → Start Command:


  streamlit run app.py --server.port $PORT --server.address 0.0.0.0


Variables → New Variable:


  API_URL = https://<your-fastapi-domain>.up.railway.app


Settings → Networking → Generate Domain


Environment Variables Summary

ServiceVariableValueFastAPIDATABASE_URL${{Postgres.DATABASE_URL}}StreamlitAPI_URLFastAPI public domain URL


⚠️ Deploy FastAPI first, get its public URL, then set it as API_URL in the Streamlit service.

---

## 🗄️ Database Schema

### `orders`
| Column | Type | Description |
|---|---|---|
| id | SERIAL | Primary key |
| customer_name | VARCHAR | Customer full name |
| phone | VARCHAR | Contact number |
| address | TEXT | Full address |
| order_date | DATE | Date order was placed |
| delivery_date | DATE | Expected delivery date |
| status | VARCHAR | `Complete` or `Incomplete` |
| total_amount | DECIMAL | Auto-calculated from items |
| advance_paid | DECIMAL | Upfront payment received |
| remaining_amount | DECIMAL | Auto-calculated balance |
| notes | TEXT | Special instructions |

### `order_items`
| Column | Type | Description |
|---|---|---|
| id | SERIAL | Primary key |
| order_id | INTEGER | FK → orders |
| item_type | VARCHAR | Garment type (e.g. Kurti) |
| quantity | INTEGER | Number of pieces |
| unit_price | DECIMAL | Price per piece |
| total_price | DECIMAL | qty × unit_price |
| measurements | JSONB | All measurements as JSON |

### `item_prices`
| Column | Type | Description |
|---|---|---|
| id | SERIAL | Primary key |
| item_name | VARCHAR | Garment name (unique) |
| price | DECIMAL | Default price per piece |
| updated_at | TIMESTAMP | Last modified time |

---

## 🧵 Default Items & Pricing

Loaded automatically on first startup. All editable from the app.

| Garment | Default Price |
|---|---|
| Kurti | ₹500 |
| Blouse | ₹300 |
| Salwar | ₹400 |
| Lehenga | ₹1,500 |
| Saree Blouse | ₹350 |
| Anarkali | ₹800 |
| Gown | ₹1,200 |
| Palazzo | ₹450 |
| Sharara | ₹600 |
| Crop Top | ₹300 |
| Jacket | ₹700 |
| Churidar | ₹350 |
| Pant | ₹400 |
| Skirt | ₹350 |
| Dupatta | ₹200 |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dashboard` | Aggregated stats for dashboard |
| `GET` | `/orders` | All orders (filter with `?status=Complete`) |
| `GET` | `/orders/{id}` | Single order with all items |
| `POST` | `/orders` | Create a new order |
| `PUT` | `/orders/{id}` | Update order details or status |
| `DELETE` | `/orders/{id}` | Delete an order |
| `GET` | `/prices` | All garment prices |
| `POST` | `/prices` | Add or update a garment price |

Full Swagger docs available at `http://localhost:8000/docs` when the server is running.

---

## 🚀 Recommended Workflow

1. Go to **💰 Item Prices** → set your garment rates
2. Use **➕ New Order** to register a customer — add items, enter measurements, record advance payment
3. Monitor all work on **📋 All Orders** — filter by status or check today's deliveries
4. When an order is ready or payment is received → **✏️ Update Order** to mark complete and record final payment
5. Check **📊 Dashboard** daily for a full business overview

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch — `git checkout -b feature/your-feature`
3. Commit your changes — `git commit -m "Add: your feature description"`
4. Push to your branch — `git push origin feature/your-feature`
5. Open a Pull Request

Please open an issue first for major changes so we can discuss the approach.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it.

---

<div align="center">
Built with ❤️ to help small tailoring businesses go digital and thus no more paper registers.
</div>
