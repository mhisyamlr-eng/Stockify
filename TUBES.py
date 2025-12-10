# Stockify Pro - Shopee Style Edition ❤️🧡
# Full UI redesign inspired by Shopee color & layout

import streamlit as st
import pandas as pd
import altair as alt
import io

st.set_page_config(page_title="Stockify Pro - Shopee Style", layout="wide", page_icon="🛒")

# =============================================================
# 🔥 SHOPEE THEME — COLORS, FONTS, CARDS, ICONS, GRADIENT HEADER
# =============================================================
CUSTOM_CSS = """
<style>
:root{
    --shopee-orange: #FF5722;
    --shopee-orange-dark: #E64A19;
    --shopee-orange-light: #FFF1EB;
    --shopee-gray: #F5F5F5;
    --card-shadow: 0 6px 20px rgba(0,0,0,0.08);
}

/* GLOBAL */
.stApp {
    background-color: var(--shopee-gray);
    font-family: "Inter", sans-serif;
}

/* HEADER SHOPEE */
header {
    background: linear-gradient(90deg, #FF5722, #FF7043);
    padding: 25px;
    border-radius: 0 0 18px 18px;
    margin-bottom: 20px;
    color: white !important;
}
header h1 {
    color: white !important;
    font-weight: 700;
    letter-spacing: 1px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #fff !important;
    border-right: 1px solid #eee;
    padding: 10px;
}

/* SHOPEE BUTTONS */
button[kind="primary"] {
    background-color: var(--shopee-orange) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 8px 14px;
    font-weight: 600;
}

button[kind="primary"]:hover {
    background-color: var(--shopee-orange-dark) !important;
}

/* METRIC CARDS */
div[data-testid="stMetric"] {
    background: white !important;
    padding: 18px !important;
    border-radius: 18px !important;
    box-shadow: var(--card-shadow) !important;
    border: none !important;
}

/* FORM CARD */
.stForm {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: var(--card-shadow);
}

/* TABLE */
div[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #ddd;
    background: white;
}

/* CATEGORY BADGE */
.badge {
    background: var(--shopee-orange-light);
    color: var(--shopee-orange-dark);
    padding: 6px 12px;
    border-radius: 50px;
    font-weight: 600;
}

/* CATEGORY ICON GRID (Shopee style) */
.category-card {
    width: 130px;
    height: 130px;
    text-align: center;
    background: white;
    border-radius: 16px;
    box-shadow: var(--card-shadow);
    padding: 12px;
    display: inline-block;
    margin: 10px;
}

.category-card:hover {
    transform: scale(1.04);
    transition: 0.2s;
}

/* HEADERS */
h1, h2, h3 {
    color: var(--shopee-orange-dark);
    font-weight: 700;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================
# 📦 DATABASE INITIALIZATION
# =============================================================
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(
        [
            {"id": 1, "name": "Mouse Wireless", "qty": 10, "category": "Elektronik", "location": "Rak A", "notes": ""},
            {"id": 2, "name": "Kaos Polos L", "qty": 25, "category": "Pakaian", "location": "Rak B", "notes": ""},
            {"id": 3, "name": "Botol Minum 600ml", "qty": 8, "category": "Rumah Tangga", "location": "Rak C", "notes": "BPA Free"},
        ],
        columns=["id", "name", "qty", "category", "location", "notes"]
    )

inv = st.session_state.inventory

# =============================================================
# 🔧 HELPER FUNCTIONS
# =============================================================
def next_id():
    return int(inv["id"].max()) + 1 if not inv.empty else 1

def add_item(name, qty, cat=None, loc=None, notes=None):
    new = pd.DataFrame([{
        "id": next_id(), "name": name, "qty": int(qty),
        "category": cat, "location": loc, "notes": notes
    }])
    st.session_state.inventory = pd.concat([inv, new], ignore_index=True)

def search_items(q):
    q = q.lower()
    return inv[inv.apply(lambda r: q in str(r).lower(), axis=1)]

def low_stock(threshold=5):
    return inv[inv["qty"] <= threshold]

def badge(df):
    df2 = df.copy()
    df2["category"] = df2["category"].apply(
        lambda c: f"<span class='badge'>{c}</span>"
    )
    return df2.to_html(escape=False, index=False)

# =============================================================
# 🧭 SIDEBAR MENU
# =============================================================
st.sidebar.title("🛍 Stockify Pro (Shopee Style)")
page = st.sidebar.radio("Menu", ["Dashboard", "Tambah Barang", "Daftar Barang"])

threshold = st.sidebar.number_input("Ambang Stok Rendah", min_value=0, value=5)

# =============================================================
# 🏠 DASHBOARD SHOPEE STYLE
# =============================================================
if page == "Dashboard":

    st.markdown("<header><h1>🛒 Stockify Dashboard</h1></header>", unsafe_allow_html=True)
    st.write("Pantau stok dengan tampilan cerah ala Shopee ✨")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Item", len(inv))
    col2.metric("Total Kuantitas", int(inv["qty"].sum()))
    col3.metric("Stok Rendah", len(low_stock(threshold)))

    # Category grid (Shopee style)
    st.subheader("Kategori (Shopee Grid)")
    categories = sorted(inv["category"].dropna().unique())
    category_html = ""
    for c in categories:
        category_html += f"""
        <div class='category-card'>
            <img src='https://cdn-icons-png.flaticon.com/512/3081/3081559.png' width='48'>
            <div style='margin-top:10px;font-weight:600'>{c}</div>
        </div>
        """
    st.markdown(category_html, unsafe_allow_html=True)

    # Chart
    st.subheader("Chart Stok per Kategori")
    chart_data = inv.groupby("category")["qty"].sum().reset_index()
    chart = alt.Chart(chart_data).mark_bar(color="#FF5722").encode(
        x="category",
        y="qty",
        tooltip=["category", "qty"]
    )
    st.altair_chart(chart, use_container_width=True)

    # Low stock list
    st.subheader("⚠ Stok Rendah")
    low = low_stock(threshold)
    if low.empty:
        st.success("Semua stok aman! 🎉")
    else:
        st.markdown(badge(low), unsafe_allow_html=True)

# =============================================================
# ➕ TAMBAH BARANG
# =============================================================
elif page == "Tambah Barang":

    st.markdown("<header><h1>➕ Tambah Barang</h1></header>", unsafe_allow_html=True)

    with st.form("add_form"):
        name = st.text_input("Nama Barang")
        qty = st.number_input("Jumlah", min_value=0, step=1)
        cat = st.text_input("Kategori")
        loc = st.text_input("Lokasi")
        notes = st.text_area("Catatan")

        submit = st.form_submit_button("Tambah Barang")

    if submit:
        if name == "":
            st.error("Nama tidak boleh kosong!")
        else:
            add_item(name, qty, cat, loc, notes)
            st.success("Barang berhasil ditambahkan! 🎉")
            st.experimental_rerun()

# =============================================================
# 📋 DAFTAR BARANG — Shopee Table
# =============================================================
elif page == "Daftar Barang":

    st.markdown("<header><h1>📦 Daftar Barang</h1></header>", unsafe_allow_html=True)

    q = st.text_input("Cari barang...")
    data = search_items(q) if q else inv

    st.markdown(badge(data), unsafe_allow_html=True)

    # Inline editor
    st.subheader("Edit Tabel")
    edited = st.data_editor(inv, use_container_width=True, num_rows="dynamic")
    if st.button("Simpan Perubahan", type="primary"):
        edited["qty"] = edited["qty"].astype(int)
        st.session_state.inventory = edited
        st.success("Perubahan berhasil disimpan!")
        st.experimental_rerun()
