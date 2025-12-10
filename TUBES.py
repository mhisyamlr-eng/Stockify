"""
Inventory app (Streamlit) - Stockify Pro (Enhanced)
Features:
- Styled UI with CSS variables matching provided palette
- Image upload / camera capture per item, image preview
- Add / Edit / Delete item
- Inline quick actions for qty +/-
- Export / Import CSV (images saved to ./images and base64 stored in CSV)
- Persist to local file (data/inventory.csv)
- Mobile-first elements: camera input, large buttons
- Placeholder for barcode scanning integration (commented)

How to run:
    pip install streamlit pandas pillow
    streamlit run inventory_app_streamlit.py

Note: this is a self-contained single-file app intended for demo and local use.
For production: use a proper database, background sync, and barcode scanning service.
"""

import streamlit as st
import pandas as pd
import os
import io
import base64
from PIL import Image
from datetime import datetime

# ---------------------------
# Config & Paths
# ---------------------------
DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
DATA_FILE = os.path.join(DATA_DIR, "inventory.csv")
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(page_title="Stockify Pro — Inventory", layout="wide")

# ---------------------------
# Theme tokens (CSS)
# ---------------------------
THEME_CSS = """
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
  --shadow: rgba(11,102,255,0.08);
}

/* page */
.app-bg{ background: var(--bg); padding: 18px 22px; }
.container{ max-width: 1200px; margin: 0 auto; }
.header{ display:flex; align-items:center; gap:16px; }
.brand{ font-weight:700; font-size:20px; color:var(--primary); }

.card{ background:var(--card-bg); border-radius:12px; border:1px solid #E8EEF8; padding:16px; box-shadow: 0 6px 18px var(--shadow); }
.btn-primary{ background:var(--primary); color:white; padding:8px 14px; border-radius:10px; border:none; cursor:pointer; }
.btn-primary:hover{ background:var(--primary-600); }
.small{ font-size:13px; color:var(--text-muted); }
.item-card{ display:flex; gap:12px; align-items:center; padding:10px; border-radius:10px; }
.thumbnail{ width:84px; height:84px; object-fit:cover; border-radius:8px; border:1px solid #E8EEF8; }
.badge-warning{ background:var(--warning); color:white; padding:4px 8px; border-radius:8px; font-weight:600; }
.chips{ display:flex; gap:8px; align-items:center; }
.quick-action{ border:none; background:transparent; cursor:pointer; }

/* responsive */
@media (max-width:600px){
  .container{ padding: 0 8px; }
  .thumbnail{ width:68px; height:68px }
}
"""

# inject CSS
st.markdown(f"<style>{THEME_CSS}</style>", unsafe_allow_html=True)

# ---------------------------
# Helpers: persistence + images
# ---------------------------

def load_inventory():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # ensure columns
            expected = ["id","name","qty","category","location","notes","image_path","created_at"]
            for c in expected:
                if c not in df.columns:
                    df[c] = ""
            return df
        except Exception as e:
            st.error(f"Gagal membaca data: {e}")
            return pd.DataFrame(columns=["id","name","qty","category","location","notes","image_path","created_at"])
    else:
        return pd.DataFrame(columns=["id","name","qty","category","location","notes","image_path","created_at"])


def save_inventory(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False)


def save_image_file(image_bytes, filename=None):
    """Save bytes to images folder and return relative path"""
    if image_bytes is None:
        return ""
    if filename is None:
        filename = f"img_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
    path = os.path.join(IMAGES_DIR, filename)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return path


def pil_to_bytes(img: Image.Image, fmt='PNG'):
    b = io.BytesIO()
    img.save(b, format=fmt)
    return b.getvalue()


def image_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        return ""

# ---------------------------
# Streamlit Session state
# ---------------------------
if "inventory_df" not in st.session_state:
    st.session_state.inventory_df = load_inventory()

# utility ID generator
def next_id():
    df = st.session_state.inventory_df
    if df.empty:
        return 1
    else:
        try:
            return int(df["id"].max()) + 1
        except Exception:
            return len(df) + 1

# CRUD functions (always operate on session_state)
def add_item(name, qty, category, location, notes, image_bytes=None):
    df = st.session_state.inventory_df
    _id = next_id()
    image_path = ""
    if image_bytes:
        image_path = save_image_file(image_bytes)
    new = {
        "id": _id,
        "name": name,
        "qty": int(qty),
        "category": category or "",
        "location": location or "",
        "notes": notes or "",
        "image_path": image_path,
        "created_at": datetime.now().isoformat()
    }
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    st.session_state.inventory_df = df
    save_inventory(df)
    return _id


def update_item(item_id, **kwargs):
    df = st.session_state.inventory_df
    idx = df.index[df["id"] == item_id].tolist()
    if not idx:
        return False
    i = idx[0]
    for k, v in kwargs.items():
        if k == "image_bytes" and v is not None:
            path = save_image_file(v)
            df.at[i, "image_path"] = path
        elif k in df.columns:
            df.at[i, k] = v
    st.session_state.inventory_df = df
    save_inventory(df)
    return True


def delete_item(item_id):
    df = st.session_state.inventory_df
    df = df[df["id"] != item_id].reset_index(drop=True)
    st.session_state.inventory_df = df
    save_inventory(df)
    return True

# quick in-place qty adjust
def adjust_qty(item_id, delta):
    df = st.session_state.inventory_df
    idx = df.index[df["id"] == item_id].tolist()
    if not idx:
        return False
    i = idx[0]
    new_qty = int(df.at[i, "qty"]) + int(delta)
    if new_qty < 0:
        new_qty = 0
    df.at[i, "qty"] = new_qty
    st.session_state.inventory_df = df
    save_inventory(df)
    return True

# ---------------------------
# UI - Layout
# ---------------------------

st.markdown('<div class="app-bg"><div class="container">', unsafe_allow_html=True)
col1, col2 = st.columns([1,3])
with col1:
    st.markdown('<div class="card" style="text-align:left">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:12px"><img src="data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 48 48\" width=\"36\" height=\"36\"><rect width=\"48\" height=\"48\" fill=\"%230B66FF\" rx=\"8\"/></svg>" style="border-radius:8px"/> <div style="line-height:1"><div class="brand">Stockify Pro</div><div class="small">Inventory & Stock management</div></div></div>', unsafe_allow_html=True)
    st.markdown('<hr/>', unsafe_allow_html=True)

    page = st.radio("Menu", ["Dashboard","Scan & Add","Items","Reports","Settings"], index=0)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if page == "Dashboard":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin:0">Dashboard</h3>', unsafe_allow_html=True)
        df = st.session_state.inventory_df
        total_skus = len(df)
        total_qty = int(df['qty'].sum()) if not df.empty else 0
        low_stock = df[df['qty'] <= 2] if not df.empty else pd.DataFrame()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total SKUs", total_skus)
        c2.metric("Total Quantity", total_qty)
        c3.metric("Low Stock", len(low_stock))
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        # quick action widgets
        ra, rb, rc = st.columns([2,1,1])
        with ra:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<b>Low stock items</b>', unsafe_allow_html=True)
            for _, r in low_stock.iterrows():
                img_html = ''
                if r.get('image_path'):
                    rel = r['image_path']
                    if os.path.exists(rel):
                        b64 = base64.b64encode(open(rel,'rb').read()).decode()
                        img_html = f'<img src="data:image/png;base64,{b64}" style="width:36px;height:36px;border-radius:6px;object-fit:cover;margin-right:8px;" />'
                st.markdown(f'<div style="display:flex;align-items:center;gap:12px;padding:6px 0">{img_html}<div><b>{r["name"]}</b><div class="small">Qty: {r["qty"]}</div></div><div style="margin-left:auto"><span class="badge-warning">Reorder</span></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with rb:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<b>Quick actions</b>', unsafe_allow_html=True)
            if st.button('Import CSV'):
                uploaded = st.file_uploader('Choose CSV', type=['csv'], key='import_csv')
                if uploaded:
                    newdf = pd.read_csv(uploaded)
                    st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, newdf], ignore_index=True)
                    save_inventory(st.session_state.inventory_df)
                    st.success('Imported')
            if st.button('Export CSV'):
                csv = st.session_state.inventory_df.to_csv(index=False).encode('utf-8')
                st.download_button('Download CSV', data=csv, file_name='inventory_export.csv')
            st.markdown('</div>', unsafe_allow_html=True)
        with rc:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<b>Scan</b>', unsafe_allow_html=True)
            st.markdown('<div class="small">Quick open camera for mobile</div>', unsafe_allow_html=True)
            cam = st.button('Open Camera')
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif page == "Scan & Add":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin:0">Scan & Add Item</h3>', unsafe_allow_html=True)
        st.markdown('<div class="small">Gunakan kamera untuk foto barang atau upload foto. (Placeholder untuk barcode scanning)</div>', unsafe_allow_html=True)
        with st.form('add_form'):
            cols = st.columns([2,1])
            with cols[0]:
                name = st.text_input('Nama Barang')
                category = st.text_input('Kategori')
                location = st.text_input('Lokasi')
                notes = st.text_area('Catatan')
            with cols[1]:
                qty = st.number_input('Kuantitas', min_value=0, value=1, step=1)
                st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
                img_camera = st.camera_input('Ambil foto (kamera)')
                img_file = st.file_uploader('Atau upload gambar', type=['png','jpg','jpeg'])
            submitted = st.form_submit_button('Tambah Barang')
            if submitted:
                image_bytes = None
                if img_file is not None:
                    image_bytes = img_file.read()
                elif img_camera is not None:
                    image_bytes = img_camera.read()
                item_id = add_item(name, qty, category, location, notes, image_bytes)
                st.success(f'Barang {name} ditambahkan (ID {item_id})')
        st.markdown('</div>', unsafe_allow_html=True)

    elif page == "Items":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin:0">Items</h3>', unsafe_allow_html=True)
        df = st.session_state.inventory_df
        q = st.text_input('Cari (nama, kategori, lokasi)', key='search')
        if q:
            mask = df['name'].astype(str).str.contains(q, case=False) | df['category'].astype(str).str.contains(q, case=False) | df['location'].astype(str).str.contains(q, case=False)
            df_view = df[mask]
        else:
            df_view = df
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        # list items as cards
        for _, row in df_view.sort_values(by='name').iterrows():
            id_ = row['id']
            name = row['name']
            qty = int(row['qty']) if row['qty'] != '' else 0
            cat = row['category']
            loc = row['location']
            img_html = ''
            if row['image_path'] and os.path.exists(row['image_path']):
                b64 = base64.b64encode(open(row['image_path'],'rb').read()).decode()
                img_html = f'<img class="thumbnail" src="data:image/png;base64,{b64}"/>'
            else:
                # placeholder
                svg = '<svg width="84" height="84" xmlns="http://www.w3.org/2000/svg"><rect width="84" height="84" rx="8" fill="#F0F4FF"/></svg>'
                img_html = f'<div style="width:84px;height:84px;border-radius:8px;background:#F0F4FF;display:flex;align-items:center;justify-content:center">📦</div>'
            st.markdown(f'<div class="card item-card"><div>{img_html}</div><div style="flex:1"><b style="color:var(--text-primary)">{name}</b><div class="small">{cat} • {loc}</div></div><div style="display:flex;align-items:center;gap:8px"><div style="text-align:center"><div style="font-weight:700">{qty}</div><div class="small">in stock</div></div><div style="display:flex;flex-direction:column;gap:6px;margin-left:8px">', unsafe_allow_html=True)
            # quick action buttons
            c1, c2, c3 = st.columns([1,1,1])
            # because we are inside loop, use unique keys
            if st.button('＋', key=f'add_{id_}'):
                adjust_qty(id_, 1)
                st.experimental_rerun()
            if st.button('−', key=f'rem_{id_}'):
                adjust_qty(id_, -1)
                st.experimental_rerun()
            if st.button('Detail', key=f'det_{id_}'):
                # open detail modal (simple implementation: show below)
                st.markdown('<hr/>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<h4>{name} — Detail</h4>', unsafe_allow_html=True)
                cols = st.columns([2,1])
                with cols[0]:
                    st.text_input('Nama', value=name, key=f'edit_name_{id_}')
                    st.text_input('Kategori', value=cat, key=f'edit_cat_{id_}')
                    st.text_input('Lokasi', value=loc, key=f'edit_loc_{id_}')
                    st.text_area('Notes', value=row['notes'], key=f'edit_notes_{id_}')
                with cols[1]:
                    if row['image_path'] and os.path.exists(row['image_path']):
                        st.image(row['image_path'], width=220)
                    else:
                        st.info('Tidak ada gambar')
                    img_new = st.file_uploader('Ganti / Unggah gambar', key=f'upd_img_{id_}')
                    new_qty = st.number_input('Qty', min_value=0, value=qty, key=f'edit_qty_{id_}')
                    if st.button('Simpan perubahan', key=f'save_{id_}'):
                        img_bytes = img_new.read() if img_new else None
                        update_item(id_, name=st.session_state.get(f'edit_name_{id_}'), qty=new_qty, category=st.session_state.get(f'edit_cat_{id_}'), location=st.session_state.get(f'edit_loc_{id_}'), notes=st.session_state.get(f'edit_notes_{id_}'), image_bytes=img_bytes)
                        st.success('Tersimpan')
                        st.experimental_rerun()
                    if st.button('Hapus barang', key=f'del_{id_}'):
                        delete_item(id_)
                        st.success('Terhapus')
                        st.experimental_rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div></div></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    elif page == "Reports":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Reports & Export</h3>', unsafe_allow_html=True)
        df = st.session_state.inventory_df
        st.markdown('<div class="small">Export daftar barang (CSV) atau gambar per item.</div>', unsafe_allow_html=True)
        if st.button('Export CSV'):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button('Download CSV', data=csv, file_name='inventory_export.csv')
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        # export zipped images (simple approach: provide link per image)
        for _, r in df.iterrows():
            if r['image_path'] and os.path.exists(r['image_path']):
                st.markdown(f"- {r['name']} — <a href='file://{os.path.abspath(r['image_path'])}' target='_blank'>image</a>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:  # Settings
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Settings</h3>', unsafe_allow_html=True)
        st.markdown('<div class="small">Theme tokens and tailwind snippet are embedded in the app header; copy them to your project.</div>', unsafe_allow_html=True)
        st.markdown('<details><summary>Theme tokens (CSS)</summary><pre>'+THEME_CSS+'</pre></details>', unsafe_allow_html=True)
        tailwind_snippet = "module.exports = { theme: { extend: { colors: { primary: {100: '#E6F0FF',500: '#0B66FF',600: '#0856D6'}, secondary: {500: '#0BB39A',600: '#089675'}, warning: '#FFB020', danger: '#FF4D4F', surface: {100: '#FFFFFF', 200: '#F5F7FB'}, muted: {400: '#8A97B2',600: '#4A5568'} }, boxShadow: { 'soft-primary': '0 6px 18px rgba(11,102,255,0.08)' } } } }"
        st.code(tailwind_snippet, language='javascript')
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# footer
st.markdown('<div style="text-align:center;padding:12px;color:var(--text-muted)">Built with ❤ — Stockify Pro demo</div>', unsafe_allow_html=True)

# ---------------------------
# Notes & TODOs visible inside app
# ---------------------------

st.info('''
Tips & Next steps:
- For barcode scanning integrate a JS barcode reader or server-side library (e.g. QuaggaJS for browser; pyzbar for server processing).
- For offline-first mobile use PWA + local DB (IndexedDB) + background sync to server.
- For production persist to SQL DB and store images in object storage (S3).
''')
