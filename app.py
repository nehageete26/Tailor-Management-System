import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta
import json

import os

API = os.getenv("API_URL")

st.set_page_config(
    page_title="✂️ Tailor Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main { background-color: #faf7f4; }
.stApp { background-color: #faf7f4; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2d1b69 0%, #11998e 100%);
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 15px;
    padding: 6px 0;
    cursor: pointer;
}

/* Metric cards */
.metric-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 4px solid #11998e;
    margin-bottom: 16px;
}
.metric-card.purple { border-left-color: #2d1b69; }
.metric-card.orange { border-left-color: #f7971e; }
.metric-card.red    { border-left-color: #e74c3c; }

.metric-label {
    font-size: 12px; color: #888; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.8px;
}
.metric-value {
    font-size: 28px; font-weight: 700; color: #1a1a2e;
    font-family: 'Playfair Display', serif;
}

/* Page title */
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 32px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px;
}
.page-subtitle { font-size: 14px; color: #888; margin-bottom: 24px; }

/* Status badges */
.badge-complete   { background: #d4edda; color: #155724; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-incomplete { background: #fff3cd; color: #856404; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }

/* Section headers */
.section-header {
    font-size: 18px; font-weight: 600; color: #1a1a2e;
    border-bottom: 2px solid #11998e;
    padding-bottom: 8px; margin-bottom: 16px;
}

/* Buttons */
.stButton > button { border-radius: 10px; font-weight: 600; border: none; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #2d1b69, #11998e); color: white; }

div[data-testid="stForm"] {
    background: white; padding: 24px;
    border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.order-card {
    background: white; border-radius: 12px; padding: 16px 20px;
    margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    border-left: 4px solid #11998e;
}
.order-card.incomplete { border-left-color: #f7971e; }
</style>
""", unsafe_allow_html=True)

# ─── Helper ───────────────────────────────────────────────────────────────────
def api_get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=5)
        return r.json()
    except:
        st.error("⚠️ Cannot connect to API server. Please start main.py first.")
        return None

def api_post(path, data):
    try:
        r = requests.post(f"{API}{path}", json=data, timeout=10)
        return r.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def api_put(path, data):
    try:
        r = requests.put(f"{API}{path}", json=data, timeout=10)
        return r.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def api_delete(path):
    try:
        r = requests.delete(f"{API}{path}", timeout=5)
        return r.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# ─── Measurement fields per item type ─────────────────────────────────────────
def render_measurements(item_type, i):
    """Returns measurement dict for a given item type."""
    meas = {}

    # Items that need UPPER BODY measurements (NO hip for pure tops/blouses)
    upper_body_items = ["Kurti", "Anarkali", "Gown", "Crop Top", "Jacket", "Saree Blouse"]
    # Blouse is a top — hip not needed
    blouse_items = ["Blouse"]
    # Bottom wear
    lower_body_items = ["Salwar", "Churidar", "Pant", "Palazzo", "Sharara", "Skirt"]
    # Lehenga needs both top + bottom
    lehenga_items = ["Lehenga"]

    if item_type in upper_body_items:
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            meas["bust"]         = st.text_input("Bust",          key=f"bust_{i}")
            meas["waist"]        = st.text_input("Waist",         key=f"waist_{i}")
            meas["hip"]          = st.text_input("Hip",           key=f"hip_{i}")
        with mc2:
            meas["shoulder"]     = st.text_input("Shoulder",      key=f"shldr_{i}")
            meas["sleeve_length"]= st.text_input("Sleeve Length", key=f"slv_{i}")
            meas["length"]       = st.text_input("Length",        key=f"len_{i}")
        with mc3:
            meas["neck"]         = st.text_input("Neck",          key=f"neck_{i}")
            meas["fitting_style"]= st.selectbox("Fitting Style",  ["Regular", "Slim", "Loose", "A-line"], key=f"fit_{i}")
            meas["sleeve_style"] = st.selectbox("Sleeve Style",   ["Full", "Half", "Sleeveless", "3/4th"], key=f"slvstyle_{i}")

    elif item_type in blouse_items:
        # Blouse: bust/waist/shoulder/sleeve/length/neck — NO hip
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            meas["bust"]         = st.text_input("Bust",          key=f"bust_{i}")
            meas["waist"]        = st.text_input("Waist",         key=f"waist_{i}")
        with mc2:
            meas["shoulder"]     = st.text_input("Shoulder",      key=f"shldr_{i}")
            meas["sleeve_length"]= st.text_input("Sleeve Length", key=f"slv_{i}")
            meas["length"]       = st.text_input("Length",        key=f"len_{i}")
        with mc3:
            meas["neck"]         = st.text_input("Neck",          key=f"neck_{i}")
            meas["fitting_style"]= st.selectbox("Fitting Style",  ["Regular", "Slim", "Loose", "A-line"], key=f"fit_{i}")
            meas["sleeve_style"] = st.selectbox("Sleeve Style",   ["Full", "Half", "Sleeveless", "3/4th"], key=f"slvstyle_{i}")

    elif item_type in lower_body_items:
        mc1, mc2 = st.columns(2)
        with mc1:
            meas["waist"]  = st.text_input("Waist",  key=f"waist_{i}")
            meas["hip"]    = st.text_input("Hip",    key=f"hip_{i}")
            meas["length"] = st.text_input("Length", key=f"len_{i}")
        with mc2:
            meas["ankle"]  = st.text_input("Ankle",  key=f"ankle_{i}")
            meas["thigh"]  = st.text_input("Thigh",  key=f"thigh_{i}")
            meas["notes"]  = st.text_input("Notes",  key=f"mnotes_{i}")

    elif item_type in lehenga_items:
        # Lehenga: top (choli) + bottom (skirt)
        st.markdown("**Choli (Top)**")
        mc1, mc2 = st.columns(2)
        with mc1:
            meas["bust"]         = st.text_input("Bust",          key=f"bust_{i}")
            meas["waist"]        = st.text_input("Waist",         key=f"waist_{i}")
            meas["shoulder"]     = st.text_input("Shoulder",      key=f"shldr_{i}")
        with mc2:
            meas["sleeve_length"]= st.text_input("Sleeve Length", key=f"slv_{i}")
            meas["length"]       = st.text_input("Choli Length",  key=f"len_{i}")
            meas["neck"]         = st.text_input("Neck",          key=f"neck_{i}")
        st.markdown("**Skirt (Bottom)**")
        mc3, mc4 = st.columns(2)
        with mc3:
            meas["hip"]          = st.text_input("Hip",           key=f"hip_{i}")
            meas["skirt_length"] = st.text_input("Skirt Length",  key=f"sklen_{i}")
        with mc4:
            meas["fitting_style"]= st.selectbox("Fitting Style",  ["Regular", "Flared", "A-line"], key=f"fit_{i}")

    elif item_type in ["Dupatta"]:
        meas["length"] = st.text_input("Length", key=f"len_{i}")
        meas["width"]  = st.text_input("Width",  key=f"width_{i}")

    else:
        # Generic fallback
        mc1, mc2 = st.columns(2)
        with mc1:
            meas["bust"]   = st.text_input("Bust/Chest", key=f"bust_{i}")
            meas["waist"]  = st.text_input("Waist",      key=f"waist_{i}")
            meas["length"] = st.text_input("Length",     key=f"len_{i}")
        with mc2:
            meas["hip"]    = st.text_input("Hip",        key=f"hip_{i}")
            meas["notes"]  = st.text_input("Notes",      key=f"mnotes_{i}")

    return meas

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✂️ StichTrack")
    st.markdown("---")
    page = st.radio("Navigation", [
        "📊 Dashboard",
        "➕ New Order",
        "📋 All Orders",
        "🔍 Order Details",
        "✏️ Update Order",
        "💰 Item Prices",
    ])
    st.markdown("---")
    st.markdown("**Quick Stats**")
    dash = api_get("/dashboard")
    if dash:
        st.metric("Total Orders", dash["total_orders"])
        st.metric("Today's Delivery", dash["today_delivery"])

# ─── Pages ────────────────────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Overview of your tailoring business</div>', unsafe_allow_html=True)

    dash = api_get("/dashboard")
    if dash:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Total Orders</div>
                <div class="metric-value">{dash['total_orders']}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card purple">
                <div class="metric-label">Completed</div>
                <div class="metric-value">{dash['complete']}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card orange">
                <div class="metric-label">Incomplete</div>
                <div class="metric-value">{dash['incomplete']}</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="metric-card red">
                <div class="metric-label">Today's Delivery</div>
                <div class="metric-value">{dash['today_delivery']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value">₹{dash['total_revenue']:,.0f}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card orange">
                <div class="metric-label">Total Advance Received</div>
                <div class="metric-value">₹{dash['total_advance']:,.0f}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card red">
                <div class="metric-label">Pending Payments</div>
                <div class="metric-value">₹{dash['pending_amount']:,.0f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">📈 Weekly Orders & Revenue</div>', unsafe_allow_html=True)
            if dash["weekly_data"]:
                df = pd.DataFrame(dash["weekly_data"])
                df["revenue"] = df["revenue"].astype(float)
                st.bar_chart(df.set_index("date")["revenue"])
            else:
                st.info("No data for this week yet.")

        with col2:
            st.markdown('<div class="section-header">🏆 Top Items Ordered</div>', unsafe_allow_html=True)
            if dash["top_items"]:
                df_items = pd.DataFrame(dash["top_items"])
                st.bar_chart(df_items.set_index("item_type")["count"])
            else:
                st.info("No items data yet.")

        st.markdown("---")
        st.markdown('<div class="section-header">📋 Recent Orders</div>', unsafe_allow_html=True)
        orders = api_get("/orders")
        if orders:
            recent = orders[:10]
            for o in recent:
                status_badge = (
                    '<span class="badge-complete">✅ Complete</span>'
                    if o["status"] == "Complete"
                    else '<span class="badge-incomplete">🔄 Incomplete</span>'
                )
                card_class = "" if o["status"] == "Complete" else "incomplete"
                st.markdown(f"""<div class="order-card {card_class}">
                    <b>#{o['id']} — {o['customer_name']}</b> &nbsp;|&nbsp; 📞 {o.get('phone','')} &nbsp;|&nbsp;
                    🗓️ Delivery: {o.get('delivery_date','—')} &nbsp;|&nbsp;
                    ₹{float(o['total_amount']):,.0f} total &nbsp;|&nbsp;
                    ₹{float(o['remaining_amount']):,.0f} remaining &nbsp;|&nbsp;
                    {status_badge}
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ New Order":
    st.markdown('<div class="page-title">New Order</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Add a new customer order</div>', unsafe_allow_html=True)

    prices_data = api_get("/prices")
    price_map   = {p["item_name"]: float(p["price"]) for p in prices_data} if prices_data else {}
    item_names  = list(price_map.keys())

    # ── FIX 3: Item selection OUTSIDE the form so price auto-updates ──────────
    st.markdown('<div class="section-header">👗 Items Ordered</div>', unsafe_allow_html=True)
    num_items = st.number_input("How many item types?", min_value=1, max_value=10, value=1, key="num_items_select")

    # Collect item selections + prices OUTSIDE form
    item_selections = []
    total_preview   = 0

    for i in range(int(num_items)):
        st.markdown(f"**Item {i+1}**")
        c1, c2, c3 = st.columns([3, 1, 2])
        with c1:
            item_type = st.selectbox(f"Item Type", item_names, key=f"item_{i}")
        with c2:
            qty = st.number_input("Qty", min_value=1, value=1, key=f"qty_{i}")
        with c3:
            # Price auto-updates because this is outside the form and item_type drives default
            default_price = price_map.get(item_type, 0)
            unit_price = st.number_input(
                f"Price (₹)",
                min_value=0.0,
                value=float(default_price),
                key=f"price_{i}_{item_type}"   # key changes with item_type → forces re-render with new default
            )
        subtotal     = qty * unit_price
        total_preview += subtotal
        st.caption(f"Subtotal: ₹{subtotal:,.0f}")

        # Measurements (outside form — dynamic per item type)
        with st.expander(f"📏 Measurements for {item_type} {i+1}"):
            meas = render_measurements(item_type, i)

        item_selections.append({
            "item_type":    item_type,
            "quantity":     int(qty),
            "unit_price":   unit_price,
            "measurements": meas
        })

    st.markdown(f"### Total Amount: ₹{total_preview:,.0f}")
    st.markdown("---")

    # ── Customer details + payment in the form (submit-gated) ────────────────
    with st.form("new_order_form"):
        st.markdown('<div class="section-header">👤 Customer Details</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            cust_name = st.text_input("Customer Name *", placeholder="Full name")
            phone     = st.text_input("Phone Number",    placeholder="9876543210")
        with c2:
            address   = st.text_area("Address", placeholder="Full address", height=100)

        c1, c2 = st.columns(2)
        with c1:
            order_date    = st.date_input("Order Date",    value=date.today())
        with c2:
            delivery_date = st.date_input("Delivery Date", value=date.today() + timedelta(days=7))

        st.markdown("---")
        st.markdown('<div class="section-header">💳 Payment Details</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Amount", f"₹{total_preview:,.0f}")
        with c2:
            advance = st.number_input("Advance Paid (₹)", min_value=0.0, value=0.0, step=50.0)
        with c3:
            st.metric("Remaining", f"₹{total_preview - advance:,.0f}")

        notes = st.text_area("Special Notes / Instructions", placeholder="Any special requirements...")

        submitted = st.form_submit_button("💾 Save Order", type="primary", use_container_width=True)

    # ── FIX 1: Validation — must have customer name AND at least one item ─────
    if submitted:
        errors = []
        if not cust_name.strip():
            errors.append("Customer name is required.")
        if not item_selections:
            errors.append("Please add at least one item before saving.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            payload = {
                "customer_name": cust_name.strip(),
                "phone":         phone,
                "address":       address,
                "delivery_date": str(delivery_date),
                "advance_paid":  advance,
                "notes":         notes,
                "items":         item_selections
            }
            result = api_post("/orders", payload)
            if result and "id" in result:
                st.success(f"✅ Order #{result['id']} created for {cust_name}!")
                st.info(
                    f"**Total: ₹{float(result['total_amount']):,.0f}** | "
                    f"Advance: ₹{float(result['advance_paid']):,.0f} | "
                    f"Remaining: ₹{float(result['remaining_amount']):,.0f}"
                )

# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 All Orders":
    st.markdown('<div class="page-title">All Orders</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">View and filter all customer orders</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        filter_status = st.selectbox("Filter by Status", ["All", "Complete", "Incomplete"])
    with c2:
        search_name = st.text_input("Search by Name", placeholder="Customer name...")
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        show_today = st.checkbox("Today's Deliveries Only")

    status_param = None if filter_status == "All" else filter_status
    orders = api_get(f"/orders{'?status=' + status_param if status_param else ''}")

    if orders:
        if search_name:
            orders = [o for o in orders if search_name.lower() in o["customer_name"].lower()]
        if show_today:
            today  = str(date.today())
            orders = [o for o in orders if o.get("delivery_date") == today]

        st.markdown(f"**{len(orders)} orders found**")
        if orders:
            df = pd.DataFrame(orders)[[
                "id", "customer_name", "phone", "order_date", "delivery_date",
                "status", "total_amount", "advance_paid", "remaining_amount"
            ]]
            df.columns = ["ID", "Customer", "Phone", "Order Date", "Delivery Date",
                          "Status", "Total (₹)", "Advance (₹)", "Remaining (₹)"]
            df["Total (₹)"]     = df["Total (₹)"].apply(lambda x: f"₹{float(x):,.0f}")
            df["Advance (₹)"]   = df["Advance (₹)"].apply(lambda x: f"₹{float(x):,.0f}")
            df["Remaining (₹)"] = df["Remaining (₹)"].apply(lambda x: f"₹{float(x):,.0f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No orders match the filter.")
    else:
        st.info("No orders found.")

# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Order Details":
    st.markdown('<div class="page-title">Order Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">View complete details of an order</div>', unsafe_allow_html=True)

    order_id = st.number_input("Enter Order ID", min_value=1, step=1)
    if st.button("🔍 Fetch Order", type="primary"):
        order = api_get(f"/orders/{order_id}")
        if order:
            st.success(f"Order #{order['id']} — {order['customer_name']}")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Customer:** {order['customer_name']}")
                st.markdown(f"**Phone:**    {order.get('phone', '—')}")
                st.markdown(f"**Address:**  {order.get('address', '—')}")
            with c2:
                st.markdown(f"**Order Date:**    {order.get('order_date', '—')}")
                st.markdown(f"**Delivery Date:** {order.get('delivery_date', '—')}")
                badge = "✅ Complete" if order["status"] == "Complete" else "🔄 Incomplete"
                st.markdown(f"**Status:** {badge}")
            with c3:
                st.metric("Total Amount", f"₹{float(order['total_amount']):,.0f}")
                st.metric("Advance Paid", f"₹{float(order['advance_paid']):,.0f}")
                st.metric("Remaining",    f"₹{float(order['remaining_amount']):,.0f}")

            if order.get("notes"):
                st.info(f"📝 Notes: {order['notes']}")

            st.markdown("---")
            st.markdown("**Items Ordered:**")
            if order.get("items"):
                for it in order["items"]:
                    with st.expander(f"👗 {it['item_type']} × {it['quantity']} — ₹{float(it['total_price']):,.0f}"):
                        st.markdown(f"Unit Price: ₹{float(it['unit_price']):,.0f}")
                        if it.get("measurements"):
                            m = it["measurements"]
                            if isinstance(m, str):
                                m = json.loads(m)
                            if m:
                                mdf = pd.DataFrame([{"Measurement": k, "Value": v} for k, v in m.items() if v])
                                if not mdf.empty:
                                    st.dataframe(mdf, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Update Order":
    st.markdown('<div class="page-title">Update Order</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Update status, payment, or delivery date</div>', unsafe_allow_html=True)

    order_id = st.number_input("Enter Order ID to Update", min_value=1, step=1)
    if st.button("🔍 Load Order"):
        st.session_state["loaded_order"] = api_get(f"/orders/{order_id}")

    if "loaded_order" in st.session_state and st.session_state["loaded_order"]:
        o = st.session_state["loaded_order"]
        st.info(f"Editing Order #{o['id']} — {o['customer_name']}")

        with st.form("update_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_status   = st.selectbox("Status", ["Incomplete", "Complete"],
                                            index=0 if o["status"] == "Incomplete" else 1)
                new_delivery = st.date_input("Delivery Date",
                                             value=date.fromisoformat(o["delivery_date"]) if o.get("delivery_date") else date.today())
            with c2:
                new_advance = st.number_input("Advance Paid (₹)",
                                              value=float(o["advance_paid"]), min_value=0.0, step=50.0)
                st.metric("Remaining (auto)", f"₹{float(o['total_amount']) - new_advance:,.0f}")

            new_phone   = st.text_input("Phone",   value=o.get("phone", ""))
            new_address = st.text_area("Address",  value=o.get("address", ""))

            update_btn = st.form_submit_button("💾 Update Order", type="primary", use_container_width=True)
            delete_btn = st.form_submit_button("🗑️ Delete Order", use_container_width=True)

        if update_btn:
            result = api_put(f"/orders/{o['id']}", {
                "status":        new_status,
                "delivery_date": str(new_delivery),
                "advance_paid":  new_advance,
                "phone":         new_phone,
                "address":       new_address
            })
            if result:
                st.success("✅ Order updated successfully!")
                st.metric("New Remaining", f"₹{float(result['remaining_amount']):,.0f}")
                del st.session_state["loaded_order"]

        if delete_btn:
            api_delete(f"/orders/{o['id']}")
            st.success("🗑️ Order deleted.")
            del st.session_state["loaded_order"]

# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 Item Prices":
    st.markdown('<div class="page-title">Item Prices</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Manage pricing for all garment types</div>', unsafe_allow_html=True)

    prices = api_get("/prices")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="section-header">📋 Current Prices</div>', unsafe_allow_html=True)
        if prices:
            df = pd.DataFrame(prices)[["item_name", "price", "updated_at"]]
            df.columns = ["Item", "Price (₹)", "Last Updated"]
            df["Price (₹)"] = df["Price (₹)"].apply(lambda x: f"₹{float(x):,.0f}")
            st.dataframe(df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown('<div class="section-header">✏️ Add / Update Price</div>', unsafe_allow_html=True)
        with st.form("price_form"):
            item_names_existing = [p["item_name"] for p in prices] if prices else []
            price_mode = st.radio("Mode", ["Update Existing", "Add New Item"])
            if price_mode == "Update Existing" and item_names_existing:
                selected_item = st.selectbox("Select Item", item_names_existing)
            else:
                selected_item = st.text_input("New Item Name", placeholder="e.g. Jacket")
            new_price = st.number_input("Price (₹)", min_value=0.0, step=50.0)
            save_btn  = st.form_submit_button("💾 Save Price", type="primary", use_container_width=True)

        if save_btn and selected_item:
            result = api_post("/prices", {"item_name": selected_item, "price": new_price})
            if result:
                st.success(f"✅ Price updated: {selected_item} → ₹{new_price:,.0f}")
                st.rerun()
