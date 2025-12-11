import streamlit as st

# =============================
# INITIALIZE DATA
# =============================
if "items" not in st.session_state:
    st.session_state.items = []  # list of dict: {"nim","name","prodi","scores":{}}


# =============================
# CORE FUNCTIONS
# =============================
def find_by_nim(nim: str):
    for idx, it in enumerate(st.session_state.items):
        if it["nim"] == nim:
            return idx, it
    return -1, None


def add_student(nim: str, name: str, prodi: str):
    idx, _ = find_by_nim(nim)
    if idx != -1:
        return False, "NIM sudah ada."

    st.session_state.items.append({
        "nim": nim,
        "name": name,
        "prodi": prodi,
        "scores": {}
    })
    return True, "Mahasiswa berhasil ditambahkan."


def add_or_update_score(nim: str, matkul: str, nilai: float):
    idx, it = find_by_nim(nim)
    if idx == -1:
        return False, "Mahasiswa tidak ditemukan."

    it["scores"][matkul] = nilai
    return True, "Nilai berhasil ditambah/diupdate."


def edit_score(nim: str, matkul: str, nilai_baru: float):
    idx, it = find_by_nim(nim)
    if idx == -1:
        return False, "Mahasiswa tidak ditemukan."

    if matkul not in it["scores"]:
        return False, "Mata kuliah tidak ditemukan."

    it["scores"][matkul] = nilai_baru
    return True, "Nilai berhasil diperbarui."


def delete_student(nim: str):
    before = len(st.session_state.items)
    st.session_state.items = [it for it in st.session_state.items if it["nim"] != nim]

    if len(st.session_state.items) < before:
        return True, "Data mahasiswa berhasil dihapus."
    return False, "NIM tidak ditemukan."


def get_student(nim: str):
    idx, it = find_by_nim(nim)
    if idx == -1:
        return None
    return it


# =============================
# OPTIONAL: Helper for Display
# =============================
def calculate_average(scores: dict):
    if not scores:
        return 0
    return sum(scores.values()) / len(scores)


def display_student(it: dict):
    st.write(f"**NIM:** {it['nim']}")
    st.write(f"**Nama:** {it['name']}")
    st.write(f"**Prodi:** {it['prodi']}")
    st.write("---")

    if not it["scores"]:
        st.info("Belum ada nilai.")
    else:
        for m, v in it["scores"].items():
            st.write(f"- **{m}** : {v}")

        avg = calculate_average(it["scores"])
        st.success(f"Rata-rata nilai: {avg:.2f}")
