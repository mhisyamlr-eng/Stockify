import streamlit as st

# =============================
#   INITIALIZE SESSION STATE
# =============================
if "items" not in st.session_state:
    st.session_state.items = []  # Data mahasiswa


# =============================
#           FUNCTIONS
# =============================
def find_by_nim(nim: str):
    for idx, it in enumerate(st.session_state.items):
        if it["nim"] == nim:
            return idx, it
    return -1, None


def add_student(nim: str, name: str, prodi: str):
    idx, _ = find_by_nim(nim)
    if idx != -1:
        return False, "❌ NIM sudah ada."

    st.session_state.items.append({
        "nim": nim,
        "name": name,
        "prodi": prodi,
        "scores": {}
    })
    return True, "✅ Mahasiswa berhasil ditambahkan."


def add_or_update_score(nim: str, matkul: str, nilai: float):
    idx, it = find_by_nim(nim)
    if idx == -1:
        return False, "❌ Mahasiswa tidak ditemukan."

    it["scores"][matkul] = nilai
    return True, "✅ Nilai berhasil ditambah atau diupdate."


def edit_score(nim: str, matkul: str, nilai_baru: float):
    idx, it = find_by_nim(nim)
    if idx == -1:
        return False, "❌ Mahasiswa tidak ditemukan."
    if matkul not in it["scores"]:
        return False, "❌ Mata kuliah tidak ditemukan."

    it["scores"][matkul] = nilai_baru
    return True, "✅ Nilai berhasil diubah."


def delete_student(nim: str):
    before = len(st.session_state.items)
    st.session_state.items = [it for it in st.session_state.items if it["nim"] != nim]

    if len(st.session_state.items) < before:
        return True, "🗑️ Data mahasiswa berhasil dihapus."
    return False, "❌ NIM tidak ditemukan."


def calculate_average(scores: dict):
    if not scores:
        return 0
    return sum(scores.values()) / len(scores)


def display_student(it: dict):
    st.write(f"### 👤 {it['name']} ({it['nim']})")
    st.write(f"**Prodi:** {it['prodi']}")
    st.write("---")

    if not it["scores"]:
        st.info("Belum ada nilai.")
    else:
        st.subheader("📚 Nilai Mata Kuliah")
        for m, v in it["scores"].items():
            st.write(f"- **{m}**: {v}")

        avg = calculate_average(it["scores"])
        st.success(f"**Rata-rata Nilai: {avg:.2f}**")


# =============================
#           UI STREAMLIT
# =============================
st.title("🎓 Student Grade Manager (Streamlit Version)")

menu = st.sidebar.radio("Menu", [
    "Tambah Mahasiswa",
    "Tambah/Update Nilai",
    "Edit Nilai",
    "Hapus Mahasiswa",
    "Cari Mahasiswa",
    "Tampilkan Semua"
])

# =============================
#       TAMBAH MAHASISWA
# =============================
if menu == "Tambah Mahasiswa":
    st.header("➕ Tambah Mahasiswa Baru")

    nim = st.text_input("NIM")
    name = st.text_input("Nama")
    prodi = st.text_input("Prodi")

    if st.button("Simpan"):
        if nim and name and prodi:
            ok, msg = add_student(nim, name, prodi)
            st.info(msg)
        else:
            st.warning("Harap isi semua field!")

# =============================
#   TAMBAH / UPDATE NILAI
# =============================
elif menu == "Tambah/Update Nilai":
    st.header("📝 Tambah / Update Nilai")

    nim = st.text_input("Masukkan NIM Mahasiswa")
    matkul = st.text_input("Nama Mata Kuliah")
    nilai = st.number_input("Nilai", min_value=0.0, max_value=100.0)

    if st.button("Simpan Nilai"):
        if nim and matkul:
            ok, msg = add_or_update_score(nim, matkul, nilai)
            st.info(msg)
        else:
            st.warning("Isi semua field!")

# =============================
#         EDIT NILAI
# =============================
elif menu == "Edit Nilai":
    st.header("✏️ Edit Nilai Mata Kuliah")

    nim = st.text_input("Masukkan NIM")
    idx, it = find_by_nim(nim)

    if idx != -1:
        if it["scores"]:
            matkul = st.selectbox("Pilih Mata Kuliah", list(it["scores"].keys()))
            nilai_baru = st.number_input("Nilai Baru", min_value=0.0, max_value=100.0)

            if st.button("Update Nilai"):
                ok, msg = edit_score(nim, matkul, nilai_baru)
                st.info(msg)
        else:
            st.warning("Mahasiswa belum memiliki nilai.")
    elif nim:
        st.error("Mahasiswa tidak ditemukan.")

# =============================
#       HAPUS MAHASISWA
# =============================
elif menu == "Hapus Mahasiswa":
    st.header("🗑️ Hapus Mahasiswa")

    nim = st.text_input("Masukkan NIM yang ingin dihapus")

    if st.button("Hapus"):
        ok, msg = delete_student(nim)
        st.info(msg)

# =============================
#     CARI MAHASISWA
# =============================
elif menu == "Cari Mahasiswa":
    st.header("🔍 Cari Mahasiswa")

    nim = st.text_input("Masukkan NIM")

    idx, it = find_by_nim(nim)

    if idx != -1:
        display_student(it)
    elif nim:
        st.error("Mahasiswa tidak ditemukan.")

# =============================
#       TAMPILKAN SEMUA
# =============================
elif menu == "Tampilkan Semua":
    st.header("📋 Daftar Semua Mahasiswa")

    if not st.session_state.items:
        st.info("Belum ada data mahasiswa.")
    else:
        for it in st.session_state.items:
            st.write("---")
            display_student(it)
        st.write("---")
