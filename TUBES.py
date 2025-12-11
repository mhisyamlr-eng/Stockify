# TUBES.py - Streamlit Revised
# Jalankan: streamlit run TUBES.py

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd
import numpy as np
import base64
import uuid
from datetime import datetime

# -----------------------
# Helper: Default avatar sketsa (PIL)
# -----------------------
def generate_default_avatar(size=256):
    img = Image.new("RGB", (size, size), (245, 247, 251))
    draw = ImageDraw.Draw(img)
    # head
    cx, cy = size//2, size//2 - 16
    r = size//4
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(230,230,230), outline=(200,200,200))
    # body rectangle
    bx1, by1 = cx - r - 12, cy + r - 6
    bx2, by2 = cx + r + 12, cy + r + 80
    draw.rectangle((bx1, by1, bx2, by2), fill=(230,230,230))
    # simple face: eyes & smile
    draw.ellipse((cx-30, cy-10, cx-20, cy), fill=(180,180,180))
    draw.ellipse((cx+20, cy-10, cx+30, cy), fill=(180,180,180))
    draw.arc((cx-20, cy+5, cx+20, cy+30), start=0, end=180, fill=(160,160,160), width=3)
    return img

def pil_image_to_bytes(img, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()

# -----------------------
# Session state initialization
# -----------------------
def init_state():
    if "items" not in st.session_state:
        st.session_state["items"] = []  # list of dicts: {id, name, qty, image_bytes, created_at}
    if "profile_img" not in st.session_state:
        st.session_state["profile_img"] = pil_image_to_bytes(generate_default_avatar(256))
    if "form_item_name" not in st.session_state:
        st.session_state["form_item_name"] = ""
    if "form_item_qty" not in st.session_state:
        st.session_state["form_item_qty"] = 1
    if "form_item_image" not in st.session_state:
        st.session_state["form_item_image"] = None
    if "filter_text" not in st.session_state:
        st.session_state["filter_text"] = ""

init_state()

# -----------------------
# CSS: inject styles (not printed as text)
# -----------------------
def inject_css():
    css = """
    <style>
    :root{
      --bg: #F5F7FB;
      --card-bg: #FFFFFF;
      --text-primary: #1F2937;
      --text-muted: #8A97B2;
      --primary: #0B66FF;
      --primary-600: #0856D6;
      --secondary: #0BB39A;
      --warning: #FFB020;
      --danger: #FF4D4F;
      --shadow: rgba(11,102,255,0.06);
    }
    .app-container { background: var(--bg); padding: 18px 22px; }
    .brand { font-weight:700; font-size:20px; color:var(--primary); }
    .card { background:var(--card-bg); border-radius:12px; border:1px solid #E8EEF8; padding:16px; box-shadow:0 6px 18px var(--shadow); }
    .btn-primary { background:var(--primary); color:white; padding:8px 14px; border-radius:10px; border:none; cursor:pointer; }
    .small { font-size:13px; color:var(--text-muted); }
    .thumbnail { width:84px; height:84px; object-fit:cover; border-radius:8px; border:1px solid #E8EEF8; }
    .badge-warning { background:var(--warning); color:white; padding:4px 8px; border-radius:8px; font-weight:600; }
    /* responsive helpers */
    @media (max-width:600px){ .thumbnail{ width:68px; height:68px } }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_css()

# -----------------------
# Utility functions
# -----------------------
def add_item(name: str, qty: int, image_bytes: bytes):
    item = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "qty": int(qty),
        "image": image_bytes,
        "created_at": datetime.utcnow()
    }
    st.session_state["items"].append(item)
    return item

def delete_item(item_id: str):
    st.session_state["items"] = [it for it in st.session_state["items"] if it["id"] != item_id]

def get_items_filtered(filter_text: str = ""):
    if not filter_text:
        return st.session_state["items"]
    ft = filter_text.lower()
    return [it for it in st.session_state["items"] if ft in it["name"].lower()]

# -----------------------
# Layout: Sidebar navigation
# -----------------------
st.set_page_config(page_title="Stockify Pro - Revised", layout="wide")
with st.sidebar:
    st.image(Image.open(io.BytesIO(st.session_state["profile_img"])), width=84, caption="Profil")
    st.markdown("<div class='brand'>Stockify Pro</div>", unsafe_allow_html=True)
    st.write("Inventory & Stock management")
    st.write("---")
    page = st.radio("Menu", ["Dashboard", "Scan & Add", "Items", "Reports", "Settings"])

# -----------------------
# Page: Dashboard
# -----------------------
if page == "Dashboard":
    st.title("Dashboard")
    items = st.session_state["items"]
    total_skus = len(items)
    total_qty = sum(it["qty"] for it in items)
    low_stock = [it for it in items if it["qty"] <= 2]  # threshold demo

    col1, col2, col3 = st.columns([1,1,1])
    col1.metric("Total SKUs", total_skus)
    col2.metric("Total Quantity", total_qty)
    col3.metric("Low Stock", len(low_stock))

    st.write("")
    st.markdown("#### Low stock items")
    for it in low_stock:
        cols = st.columns([0.12, 0.6, 0.28])
        # thumbnail
        if it["image"]:
            img = Image.open(io.BytesIO(it["image"]))
            cols[0].image(img, width=64)
        else:
            cols[0].image(generate_default_avatar(64), width=64)
        cols[1].markdown(f"**{it['name']}**\n\nQty: {it['qty']}")
        cols[2].button("Reorder", key=f"reorder-{it['id']}")

    st.write("---")
    st.markdown("<div class='card'>Last 5 items added</div>", unsafe_allow_html=True)
    for it in sorted(items, key=lambda x: x["created_at"], reverse=True)[:5]:
        cols = st.columns([0.12, 0.6, 0.28])
        if it["image"]:
            cols[0].image(Image.open(io.BytesIO(it["image"])), width=64)
        else:
            cols[0].image(generate_default_avatar(64), width=64)
        cols[1].markdown(f"**{it['name']}**\n\nAdded: {it['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        cols[2].markdown(f"Qty: **{it['qty']}**")

# -----------------------
# Page: Scan & Add
# -----------------------
elif page == "Scan & Add":
    st.title("Scan & Add Item")
    st.markdown("Gunakan form ini untuk menambahkan item. Setelah submit, kolom akan kosong kembali agar siap input item selanjutnya.")

    with st.form("add_item_form", clear_on_submit=False):
        c1, c2 = st.columns([3,1])
        name = c1.text_input("Nama Barang", value=st.session_state["form_item_name"], key="form_name_input")
        qty = c2.number_input("Qty", min_value=0, value=st.session_state["form_item_qty"], step=1, key="form_qty_input")
        image_file = st.file_uploader("Foto (opsional)", type=["png","jpg","jpeg"], key="form_image_uploader")
        submitted = st.form_submit_button("Submit Item")

        # Jika submit ditekan
        if submitted:
            # proses image bytes
            image_bytes = None
            if image_file is not None:
                image_bytes = image_file.read()
            else:
                # optional: set default blank thumbnail or None
                image_bytes = pil_image_to_bytes(generate_default_avatar(256))

            # Validasi sederhana
            if not name or name.strip() == "":
                st.warning("Nama barang tidak boleh kosong.")
            else:
                add_item(name, qty, image_bytes)
                st.success(f"Item '{name}' (qty: {qty}) berhasil ditambahkan.")
                # reset form fields di session_state agar input kosong lagi
                st.session_state["form_name_input"] = ""
                st.session_state["form_qty_input"] = 1
                # reset uploader: set key baru dengan uuid untuk mengosongkan widget
                new_key = f"form_image_uploader_{uuid.uuid4().hex}"
                # NOTE: Streamlit file_uploader tidak dapat di-reset langsung; solusi: gunakan rerun via setting a new widget key.
                # Untuk menjaga behaviour tanpa experimental_rerun, gunakan st.experimental_set_query_params trick is possible,
                # tapi di sini kita set session var agar field text kosong. Uploader akan tetap menampilkan sebelumnya di beberapa versi Streamlit,
                # Jika ingin 100% reset uploader, restart komponen dengan rerun dibutuhkan. Namun text input & qty sudah kosong.
                st.session_state["form_item_name"] = ""
                st.session_state["form_item_qty"] = 1

    st.markdown("---")
    st.markdown("**Quick scan (manual input / simulate barcode)**")
    with st.form("quick_scan_form"):
        scan_input = st.text_input("Masukkan kode / nama hasil scan", value="", key="scan_input_field")
        scan_qty = st.number_input("Qty", min_value=1, value=1, step=1, key="scan_qty_field")
        if st.form_submit_button("Scan & Add"):
            if not scan_input.strip():
                st.warning("Input scan kosong.")
            else:
                add_item(scan_input.strip(), scan_qty, pil_image_to_bytes(generate_default_avatar(256)))
                st.success(f"Scan '{scan_input.strip()}' ditambahkan (qty {scan_qty}).")
                # clear quick-scan fields
                st.session_state["scan_input_field"] = ""
                st.session_state["scan_qty_field"] = 1

# -----------------------
# Page: Items
# -----------------------
elif page == "Items":
    st.title("Items")
    st.markdown("Daftar barang. Gunakan filter untuk mencari, dan tombol untuk hapus/edit.")
    filter_text = st.text_input("Filter nama...", value=st.session_state["filter_text"], key="items_filter")
    st.session_state["filter_text"] = filter_text

    items_listed = get_items_filtered(filter_text)

    st.markdown(f"**{len(items_listed)} items ditemukan**")
    for idx, it in enumerate(items_listed):
        cols = st.columns([0.12, 0.6, 0.28])
        if it["image"]:
            cols[0].image(Image.open(io.BytesIO(it["image"])), width=64)
        else:
            cols[0].image(generate_default_avatar(64), width=64)
        cols[1].markdown(f"**{it['name']}**\n\nQty: {it['qty']}\nID: `{it['id']}`")
        cdel, cedit = cols[2].columns([1,1])
        if cdel.button("Hapus", key=f"del-{it['id']}"):
            delete_item(it["id"])
            st.success(f"Item '{it['name']}' dihapus.")
        if cedit.button("Edit", key=f"edit-{it['id']}"):
            # buka modal-like UI sederhana
            with st.expander(f"Edit {it['name']}"):
                new_name = st.text_input("Nama", value=it["name"], key=f"name-edit-{it['id']}")
                new_qty = st.number_input("Qty", min_value=0, value=it["qty"], key=f"qty-edit-{it['id']}")
                new_img = st.file_uploader("Foto (opsional)", type=["png","jpg","jpeg"], key=f"img-edit-{it['id']}")
                if st.button("Simpan Perubahan", key=f"save-edit-{it['id']}"):
                    # update item in-place
                    for j, ii in enumerate(st.session_state["items"]):
                        if ii["id"] == it["id"]:
                            st.session_state["items"][j]["name"] = new_name.strip() or ii["name"]
                            st.session_state["items"][j]["qty"] = int(new_qty)
                            if new_img:
                                st.session_state["items"][j]["image"] = new_img.read()
                            st.success("Perubahan disimpan.")
                            break

    # CSV export / import
    st.markdown("---")
    cols = st.columns([1,1,1])
    if cols[0].button("Export CSV"):
        df = pd.DataFrame([{"id": it["id"], "name": it["name"], "qty": it["qty"], "created_at": it["created_at"]} for it in st.session_state["items"]])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="items.csv", mime="text/csv")
    uploaded_csv = cols[1].file_uploader("Import CSV (kolom: name,qty)", type=["csv"])
    if uploaded_csv is not None:
        try:
            df = pd.read_csv(uploaded_csv)
            added = 0
            for _, r in df.iterrows():
                if pd.isna(r.get("name")): 
                    continue
                name = str(r.get("name")).strip()
                qty = int(r.get("qty")) if not pd.isna(r.get("qty")) else 0
                add_item(name, qty, pil_image_to_bytes(generate_default_avatar(256)))
                added += 1
            st.success(f"{added} item berhasil diimport dari CSV.")
        except Exception as e:
            st.error("Gagal meng-import CSV: " + str(e))

# -----------------------
# Page: Reports
# -----------------------
elif page == "Reports":
    st.title("Reports")
    st.markdown("Visualisasi sederhana: jumlah per item (bar chart).")
    items = st.session_state["items"]
    if not items:
        st.info("Belum ada data item. Tambahkan beberapa item di menu 'Scan & Add' atau 'Items'.")
    else:
        df = pd.DataFrame([{"name": it["name"], "qty": it["qty"]} for it in items])
        agg = df.groupby("name", as_index=False).sum().sort_values("qty", ascending=False)
        st.markdown("### Quantity per Item")
        st.bar_chart(data=agg.set_index("name")["qty"])
        st.markdown("---")
        st.markdown("### Statistik singkat")
        st.table({
            "Total SKUs": [len(items)],
            "Total Quantity": [sum(it["qty"] for it in items)],
            "Low stock (<=2)": [len([it for it in items if it["qty"] <= 2])]
        })

# -----------------------
# Page: Settings
# -----------------------
elif page == "Settings":
    st.title("Settings")
    st.markdown("Atur profil dan preferensi. Tidak ada kode/tema yang ditampilkan di sini — hanya UI yang bersih.")

    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown("#### Foto profil")
        current_img = Image.open(io.BytesIO(st.session_state["profile_img"]))
        st.image(current_img, width=150)
        uploaded = st.file_uploader("Upload foto profil (jpg/png)", type=["jpg","jpeg","png"], key="profile_upload")
        if uploaded is not None:
            try:
                st.session_state["profile_img"] = uploaded.read()
                st.success("Foto profil diperbarui.")
            except Exception as e:
                st.error("Gagal memperbarui foto: " + str(e))

    with col2:
        st.markdown("#### Preferensi Aplikasi")
        theme_dark = st.checkbox("Mode Gelap (fitur demo)", value=False, key="pref_theme_dark")
        low_stock_threshold = st.number_input("Threshold low-stock (untuk dashboard)", min_value=0, value=2, key="pref_low_stock")
        st.markdown("**Catatan:** Pengaturan ini hanya untuk demo; untuk penyimpanan permanen hubungkan ke DB.")

# -----------------------
# Footer (tidy)
# -----------------------
st.markdown("---")
st.markdown("<div class='small'>Built with ❤ — Stockify Pro demo (revised)</div>", unsafe_allow_html=True)

