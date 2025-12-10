# TUBES - Stockify Pro (Enhanced Tokopedia-like UI)
# Developed from user's original TUBES.py. :contentReference[oaicite:1]{index=1}

import streamlit as st
import pandas as pd
import altair as alt
import io
import base64

st.set_page_config(page_title="Stockify Pro", layout="wide", page_icon="📦")

# ------------------------------
#  Custom CSS / Tokopedia-ish UI
# ------------------------------
CUSTOM_CSS = """
<style>
:root{
  --tp-green: #03AC0E;
  --tp-green-light: #E7F9E9;
  --tp-green-dark: #02850B;
  --tp-gray: #F5F6F7;
}

/* App background */
body, .stApp {
  background-color: var(--tp-gray);
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: white;
  padding: 16px;
  border-right: 1px solid #EEE;
  border-radius: 0 12px 12px 0;
}

/* Page container padding */
.block-container {
  padding-top: 1rem;
  padding-left: 1rem;
  padding-right: 1rem;
}

/* Cards for metrics */
div[data-testid="stMetric"] {
  background: white !important;
  padding: 18px !important;
  border-radius: 12px !important;
  box-shadow: 0 6px 18px rgba(3,172,14,0.06) !important;
  border: 1px solid #EFEFEF !important;
}

/* Buttons */
button[kind="primary"] {
  background-color: var(--tp-green) !important;
  color: white !important;
  border-radius: 10px !important;
  padding: 8px 12px !important;
}
button[kind="secondary"] {
  border-radius: 10px !important;
}

/* Form card */
.stForm {
  background: white;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #EEE;
}

/* Table visuals */
div[data-testid="stDataFrame"] {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #DDD;
  background: white;
  padding: 8px;
}

/* Badge style in HTML */
.badge {
  display:inline-block;
  padding:4px 8px;
  border-radius:10px;
  font-weight:600;
}

/* Headings color */
h1, h2, h3 {
  color: var(--tp-green-dark);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ------------------------------
#  Initialization / Database
# ------------------------------
if "inventory" not in st.session_state:
    # default empty dataframe with sample seed rows for UX demo
    st.session_state.inventory = pd.DataFrame(
        [
            {"id": 1, "name": "Kabel USB Type-C", "qty": 20, "category": "Aksesoris", "location": "Gudang A", "notes": "Fast charging"},
            {"id": 2, "name": "Power Bank 10000mAh", "qty": 5, "category": "Aksesoris", "location": "Gudang B", "notes": ""},
            {"id": 3, "name": "T-shirt Polos L", "qty": 50, "category": "Pakaian", "location": "Toko", "notes": "Cotton"},
        ],
        columns=["id", "name", "qty", "category", "location", "notes"],
    )

inv = st.session_state.inventory

# ------------------------------
#  Helper functions (robust)
# ------------------------------
def next_id():
    if inv.empty:
        return 1
    # ensure integers
    try:
        return int(inv["id"].astype(int).max()) + 1
    except Exception:
        return len(inv) + 1

def add_item(name, qty, category=None, location=None, notes=None):
    new_row = {
        "id": next_id(),
        "name": str(name),
        "qty": int(qty),
        "category": category if category else None,
        "location": location if location else None,
        "notes": notes if notes else None,
    }
    st.session_state.inventory = pd.concat([inv, pd.DataFrame([new_row])], ignore_index=True)

def update_item(item_id, qty=None, name=None, category=None, location=None, notes=None):
    idx = inv.index[inv["id"] == item_id].tolist()
    if not idx:
        return False
    i = idx[0]
    if qty is not None:
        st.session_state.inventory.at[i, "qty"] = int(qty)
    if name is not None:
        st.session_state.inventory.at[i, "name"] = name
    if category is not None:
        st.session_state.inventory.at[i, "category"] = category
    if location is not None:
        st.session_state.inventory.at[i, "location"] = location
    if notes is not None:
        st.session_state.inventory.at[i, "notes"] = notes
    return True

def delete_item(item_id):
    st.session_state.inventory = inv[inv["id"] != item_id]

def search_items(query):
    if not query:
        return inv
    q = str(query).lower()
    mask = inv.apply(
        lambda r: q in str(r["name"]).lower()
        or q in str(r.get("category", "")).lower()
        or q in str(r.get("notes", "")).lower()
        or q in str(r.get("location", "")).lower(),
        axis=1,
    )
    return inv[mask]

def low_stock(threshold=5):
    # treat missing qty as 0
    df = inv.copy()
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(0).astype(int)
    return df[df["qty"] <= int(threshold)]

def total_items():
    return len(inv)

def total_quantity():
    return int(pd.to_numeric(inv["qty"], errors="coerce").fillna(0).sum()) if not inv.empty else 0

def df_with_badges(df):
    # create a copy for HTML rendering with category badges
    df2 = df.copy()
    def cat_badge(c):
        if pd.isna(c) or c == "":
            return "<span class='badge' style='background:#F0F0F0;color:#333'>-</span>"
        # color intensity based on length -> but keep green palette
        return f"<span class='badge' style='background: #E7F9E9; color:#02850B;'>{c}</span>"
    df2["category_html"] = df2["category"].apply(cat_badge)
    # prepare quantity colored if low
    df2["qty_html"] = df2["qty"].apply(lambda x: f"<b style='color:{'#D9534F' if int(x)<=st.session_state.get('threshold',5) else '#111'}'>{int(x)}</b>")
    # build HTML table with chosen columns
    html = "<table style='width:100%;border-collapse:collapse'>"
    # header
    html += "<thead><tr>"
    for col in ["id","name","qty","category","location","notes"]:
        html += f"<th style='text-align:left;padding:8px;border-bottom:1px solid #EEE'>{col.capitalize()}</th>"
    html += "</tr></thead><tbody>"
    for _, r in df2.iterrows():
        html += "<tr>"
        html += f"<td style='padding:8px;border-bottom:1px solid #FAFAFA'>{r['id']}</td>"
        html += f"<td style='padding:8px;border-bottom:1px solid #FAFAFA'>{r['name']}</td>"
        html += f"<td style='padding:8px;border-bottom:1px solid #FAFAFA'>{r['qty_html']}</td>"
        html += f"<td style='padding:8px;border-bottom:1px solid #FAFAFA'>{r['category_html']}</td>"
        html += f"<td style='padding:8px;border-bottom:1px solid #FAFAFA'>{r.get('location','') or '-'}</td>"
        html += f"<td style='padding:8px;border-bottom:1px solid #FAFAFA'>{r.get('notes','') or '-'}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html

# ------------------------------
#  Sidebar / Navigation
# ------------------------------
st.sidebar.title("Stockify Pro")
page = st.sidebar.radio("Menu", ["Dashboard", "Tambah Barang", "Daftar Barang", "Import/Export"])

# threshold stored to session for badge rendering
threshold = st.sidebar.number_input("Ambang Stok Rendah (≤)", min_value=0, value=5, key="threshold")
st.sidebar.markdown("---")
st.sidebar.caption("Aplikasi Inventaris | Tanpa File Eksternal (session-only)")

# ------------------------------
#  PAGE: DASHBOARD
# ------------------------------
if page == "Dashboard":
    st.title("📊 Dashboard Inventaris")

    # Metrics as cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 📦 Total Item")
        st.metric(label="", value=total_items())
    with c2:
        st.markdown("### 📊 Total Kuantitas")
        st.metric(label="", value=total_quantity())
    with c3:
        st.markdown("### ⚠ Stok Rendah")
        st.metric(label="", value=len(low_stock(threshold)))

    st.subheader("Distribusi Kategori")
    if not inv.empty and inv["category"].notna().any():
        chart_data = inv.groupby("category", as_index=False)["qty"].sum()
        # build altair bar to control color
        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X("category:N", sort="-y", title="Kategori"),
                y=alt.Y("qty:Q", title="Total Kuantitas"),
                tooltip=["category", "qty"]
            )
            .properties(width="container", height=300)
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Belum ada kategori untuk ditampilkan.")

    # Low Stock List
    st.subheader("⚠ Item dengan Stok Rendah")
    low = low_stock(threshold)
    if low.empty:
        st.success("Tidak ada stok rendah!")
    else:
        # render with badges and highlighting
        st.markdown(df_with_badges(low), unsafe_allow_html=True)

    # Recent Items (table)
    st.subheader("Terakhir ditambahkan / diperbarui")
    if not inv.empty:
        recent = inv.tail(10).sort_values(by="id", ascending=False)
        st.dataframe(recent, use_container_width=True)
    else:
        st.info("Inventaris kosong. Tambahkan barang di menu 'Tambah Barang'.")

# ------------------------------
#  PAGE: TAMBAH BARANG
# ------------------------------
elif page == "Tambah Barang":
    st.title("➕ Tambah Barang Baru")
    st.write("Isi form berikut untuk menambahkan barang ke inventaris.")

    with st.form("form_add", clear_on_submit=True):
        name = st.text_input("Nama Barang", placeholder="Contoh: Kain Katun T-Shirt L")
        qty = st.number_input("Jumlah", min_value=0, step=1, value=1)
        cat = st.text_input("Kategori (mis. Pakaian, Aksesoris)")
        loc = st.text_input("Lokasi (opsional)")
        notes = st.text_area("Catatan (opsional)")
        submitted = st.form_submit_button("Tambah")

    if submitted:
        if not name:
            st.error("Nama barang wajib diisi.")
        else:
            add_item(name, qty, cat or None, loc or None, notes or None)
            st.success(f"Barang '{name}' berhasil ditambahkan!")
            st.experimental_rerun()

# ------------------------------
#  PAGE: DAFTAR BARANG
# ------------------------------
elif page == "Daftar Barang":
    st.title("📋 Daftar Inventaris")

    # Search & filter UI
    q_col, s_col, reset_col = st.columns([4,2,1])
    with q_col:
        query = st.text_input("Cari Barang (nama/kategori/lokasi/catatan)", value="")
    with s_col:
        cat_filter = st.selectbox("Filter Kategori", options=["(Semua)"] + sorted(list(inv["category"].dropna().unique())) if not inv.empty else ["(Semua)"])
    with reset_col:
        if st.button("Reset"):
            st.experimental_rerun()

    # apply search and filter
    df_show = search_items(query)
    if cat_filter and cat_filter != "(Semua)":
        df_show = df_show[df_show["category"] == cat_filter]

    st.markdown("### Tampilan Tabel")
    # try to display as html with badges but also allow editing below
    st.markdown(df_with_badges(df_show), unsafe_allow_html=True)

    st.markdown("### Aksi Cepat")
    action_col1, action_col2 = st.columns(2)

    with action_col1:
        st.subheader("Update Item")
        if not inv.empty:
            id_update = st.selectbox("Pilih ID untuk Update", inv["id"], key="update_id")
            qty_new = st.number_input("Jumlah Baru", min_value=0, step=1, key="update_qty")
            name_new = st.text_input("Ubah Nama (kosongkan jika tidak)", key="update_name")
            cat_new = st.text_input("Ubah Kategori (kosongkan jika tidak)", key="update_cat")
            loc_new = st.text_input("Ubah Lokasi (kosongkan jika tidak)", key="update_loc")
            if st.button("Update", type="primary"):
                # only pass non-empty optional fields
                res = update_item(
                    int(id_update),
                    qty=qty_new,
                    name=name_new if name_new.strip() else None,
                    category=cat_new if cat_new.strip() else None,
                    location=loc_new if loc_new.strip() else None,
                )
                if res:
                    st.success("Berhasil diperbarui!")
                else:
                    st.error("ID tidak ditemukan.")
                st.experimental_rerun()

    with action_col2:
        st.subheader("Hapus Item")
        if not inv.empty:
            id_delete = st.selectbox("Pilih ID untuk Hapus", inv["id"], key="delete_id")
            if st.button("Hapus", type="secondary"):
                delete_item(int(id_delete))
                st.success("Berhasil dihapus!")
                st.experimental_rerun()
        else:
            st.info("Belum ada barang untuk dihapus.")

    # Inline editor (editable table)
    st.markdown("### Edit Tabel (Inline)")
    try:
        edited = st.data_editor(inv, num_rows="dynamic", use_container_width=True)
        if st.button("Simpan Perubahan (Editor)"):
            # basic validation: ensure id and qty integer
            edited["id"] = edited["id"].astype(int)
            edited["qty"] = edited["qty"].astype(int)
            st.session_state.inventory = edited.reset_index(drop=True)
            st.success("Perubahan tersimpan!")
            st.experimental_rerun()
    except Exception as e:
        st.error(f"Editor tidak dapat dimuat: {e}")

# ------------------------------
#  PAGE: IMPORT / EXPORT
# ------------------------------
elif page == "Import/Export":
    st.title("🔁 Import / Export Inventaris")
    st.write("Ekspor inventaris ke CSV atau impor CSV (format kolom: id,name,qty,category,location,notes).")

    exp_col, imp_col = st.columns(2)
    with exp_col:
        st.subheader("Export CSV")
        csv = inv.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, file_name="inventory_export.csv", mime="text/csv")

        st.markdown("---")
        st.subheader("Export sebagai Excel")
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
            inv.to_excel(writer, index=False, sheet_name="Inventory")
            writer.save()
        st.download_button("Download XLSX", towrite.getvalue(), file_name="inventory_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with imp_col:
        st.subheader("Import CSV")
        uploaded = st.file_uploader("Pilih file CSV", type=["csv"])
        if uploaded is not None:
            try:
                df_new = pd.read_csv(uploaded)
                # basic validation: require columns
                required = {"name","qty"}
                if not required.issubset(set(df_new.columns)):
                    st.error("CSV harus minimal memiliki kolom: name, qty (opsional: id, category, location, notes).")
                else:
                    # if id present and numeric, keep; otherwise generate new ids
                    if "id" in df_new.columns:
                        # attempt to keep ids but avoid collision by shifting new ids if overlap
                        df_new["id"] = pd.to_numeric(df_new["id"], errors="coerce")
                    else:
                        df_new["id"] = [None]*len(df_new)
                    # fill missing optional cols
                    for col in ["category","location","notes"]:
                        if col not in df_new.columns:
                            df_new[col] = None
                    # assign ids if missing
                    for i, row in df_new.iterrows():
                        if pd.isna(row["id"]):
                            df_new.at[i,"id"] = next_id()
                        else:
                            # if id collides, assign new id
                            if int(row["id"]) in list(inv["id"]):
                                df_new.at[i,"id"] = next_id()
                    # coerce qty to int
                    df_new["qty"] = pd.to_numeric(df_new["qty"], errors="coerce").fillna(0).astype(int)
                    # append to inventory
                    st.session_state.inventory = pd.concat([inv, df_new[["id","name","qty","category","location","notes"]]], ignore_index=True)
                    st.success("CSV berhasil diimpor!")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Gagal membaca CSV: {e}")

    st.markdown("---")
    st.info("Catatan: data disimpan di session Streamlit. Jika perlu penyimpanan permanen, tambahkan koneksi database atau simpan file ke disk/server.")

# End of app
