import streamlit as st
import pandas as pd

# ===============================
#     STOCKIFY PRO - SINGLE FILE
# ===============================

st.set_page_config(page_title="Stockify Pro", layout="wide")

# -------------------------------
#  INITIALIZATION (DATABASE)
# -------------------------------
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(
        columns=["id", "name", "qty", "category", "location", "notes"]
    )

inv = st.session_state.inventory


# -------------------------------
#     HELPER FUNCTIONS
# -------------------------------
def next_id():
    if inv.empty:
        return 1
    return int(inv["id"].max()) + 1

def add_item(name, qty, category=None, location=None, notes=None):
    new_row = {
        "id": next_id(),
        "name": name,
        "qty": int(qty),
        "category": category,
        "location": location,
        "notes": notes,
    }
    st.session_state.inventory = pd.concat([inv, pd.DataFrame([new_row])], ignore_index=True)

def update_item(item_id, qty=None):
    idx = inv.index[inv["id"] == item_id].tolist()
    if not idx:
        return False
    if qty is not None:
        inv.at[idx[0]], inv.at[idx[0], "qty"] = qty, qty
    return True

def delete_item(item_id):
    st.session_state.inventory = inv[inv["id"] != item_id]

def search_items(query):
    q = str(query).lower()
    mask = inv.apply(
        lambda r: q in str(r["name"]).lower()
        or q in str(r["category"]).lower()
        or q in str(r["notes"]).lower(),
        axis=1,
    )
    return inv[mask]

def low_stock(threshold=5):
    return inv[inv["qty"] <= threshold]

def total_items():
    return len(inv)

def total_quantity():
    return int(inv["qty"].sum()) if not inv.empty else 0


# -------------------------------
#        SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("Stockify Billa")
page = st.sidebar.radio("Menu", ["Dashboard", "Tambah Barang", "Daftar Barang"])

threshold = st.sidebar.number_input("Ambang Stok Rendah (≤)", min_value=0, value=5)

st.sidebar.markdown("---")
st.sidebar.caption("Aplikasi Inventaris | Tanpa File Eksternal")


# ===============================
#              PAGE 1
#           DASHBOARD
# ===============================
if page == "Dashboard":
    st.title("📊 Dashboard Inventaris")

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Item", total_items())
    c2.metric("Total Kuantitas", total_quantity())
    c3.metric("Stok Rendah", len(low_stock(threshold)))

    st.subheader("Distribusi Kategori")
    if not inv.empty and inv["category"].notna().any():
        chart_data = inv.groupby("category")["qty"].sum().reset_index()
        st.bar_chart(chart_data.set_index("category"))
    else:
        st.info("Belum ada kategori untuk ditampilkan.")

    # Low Stock List
    st.subheader("⚠ Item dengan Stok Rendah")
    low = low_stock(threshold)
    if len(low) == 0:
        st.success("Tidak ada stok rendah!")
    else:
        st.table(low)


# ===============================
#              PAGE 2
#          TAMBAH BARANG
# ===============================
elif page == "Tambah Barang":
    st.title("➕ Tambah Barang Baru")

    with st.form("form_add"):
        name = st.text_input("Nama Barang")
        qty = st.number_input("Jumlah", min_value=0, step=1)
        cat = st.text_input("Kategori")
        loc = st.text_input("Lokasi (opsional)")
        notes = st.text_area("Catatan (opsional)")
        submit = st.form_submit_button("Tambah")

    if submit:
        if not name:
            st.error("Nama barang wajib diisi.")
        else:
            add_item(name, qty, cat or None, loc or None, notes or None)
            st.success(f"Barang '{name}' berhasil ditambahkan!")
            st.experimental_rerun()


# ===============================
#              PAGE 3
#          DAFTAR BARANG
# ===============================
elif page == "Daftar Barang":
    st.title("📋 Daftar Inventaris")

    # Search
    query = st.text_input("Cari Barang (nama/kategori/catatan)")
    if query:
        df_show = search_items(query)
    else:
        df_show = inv

    st.dataframe(df_show, use_container_width=True)

    st.markdown("### Aksi Cepat")
    col1, col2 = st.columns(2)

    # Update
    with col1:
        if not inv.empty:
            id_update = st.selectbox("Pilih ID untuk Update", inv["id"])
            qty_new = st.number_input("Jumlah Baru", min_value=0, step=1)
            if st.button("Update"):
                update_item(id_update, qty_new)
                st.success("Berhasil diperbarui!")
                st.experimental_rerun()

    # Delete
    with col2:
        if not inv.empty:
            id_delete = st.selectbox("Pilih ID untuk Hapus", inv["id"])
            if st.button("Hapus"):
                delete_item(id_delete)
                st.success("Berhasil dihapus!")
                st.experimental_rerun()

    # Inline editor
    st.markdown("### Edit Tabel (Inline)")
    edited = st.data_editor(inv, num_rows="dynamic")
    if st.button("Simpan Perubahan"):
        st.session_state.inventory = edited
        st.success("Perubahan tersimpan!")
        st.experimental_rerun()
