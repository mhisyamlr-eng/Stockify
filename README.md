# 📦 Stockify

> **Smart Inventory System** - Kelola stok barang dengan mudah dan efisien

[![Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Live Demo](https://img.shields.io/badge/🚀-Live_Demo-success?style=flat-square)](https://stockifyapp.streamlit.app)

---

## ✨ Fitur Utama

### 🏠 Dashboard
- **4 Metrik Penting** dalam satu layar:
  - 📦 Total Items - Total jumlah jenis barang
  - 📊 Total Stock - Total kuantitas semua barang
  - ⚠️ Low Stock - Barang yang perlu direstock
  - 🚫 Out of Stock - Barang yang habis
- **Recent Items** - Tampilan barang terbaru dengan kategori dan jumlah

### ➕ Add Item
- Form sederhana untuk menambah barang baru:
  - Nama barang
  - Kategori (Electronics, Furniture, dll)
  - Jumlah stok (dengan tombol +/-)
- Langsung tersimpan ke database

### 📋 Items Management
- **Search** - Cari barang dengan cepat
- **Item Counter** - Lihat berapa barang yang ada
- **Edit & Delete** - Ubah atau hapus item dengan mudah
- Card view dengan info lengkap:
  - Nama barang
  - Kategori (badge biru)
  - Jumlah stok dengan warna indikator:
    - 🟢 Hijau = Stok aman (>10)
    - 🟡 Kuning = Low stock (5-10)
    - 🔴 Merah = Kritis (<5)

### 📊 Reports
- Visualisasi data inventory (coming soon)
- Analytics dan insights

### ⚙️ Settings
- **Data Management**:
  - 🗑️ Clear All Data - Hapus semua data
  - 🔄 Load Demo Data - Muat data contoh untuk testing

---

## 🚀 Quick Start

### Instalasi

```bash
# Clone repository
git clone https://github.com/yourusername/stockify.git
cd stockify

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
streamlit run app.py
```

Buka browser di `http://localhost:8501` 🎉

---

## 🛠️ Tech Stack

- **Framework**: Streamlit
- **Language**: Python 3.8+
- **Database**: JSON file storage
- **UI**: Custom CSS dengan color indicators

---

## 📸 Screenshots

<div align="center">

| Dashboard | Add Item | All Items |
|-----------|----------|-----------|
| Lihat overview stok | Tambah barang baru | Kelola inventory |

</div>

---

## 📖 Cara Penggunaan

### Menambah Barang Baru
1. Klik menu **"➕ Add Item"** di sidebar
2. Isi nama barang (contoh: "Laptop Dell")
3. Pilih kategori dari dropdown
4. Atur jumlah stok
5. Klik tombol **"✅ Add Item"**

### Melihat Semua Barang
1. Klik menu **"📋 Items"** di sidebar
2. Gunakan search bar untuk mencari barang
3. Lihat semua item dalam bentuk card
4. Klik **"✏️ Edit"** untuk mengubah
5. Klik **"🗑️ Delete"** untuk menghapus

### Mengatur Data
1. Klik menu **"⚙️ Settings"** di sidebar
2. **"Clear All Data"** - Hapus semua inventory
3. **"Load Demo Data"** - Isi dengan data contoh

---

## 🗂️ Struktur Project

```
stockify/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── data.json          # Data storage
└── README.md          # Documentation
```

---

## 🎯 Roadmap

- [x] Dashboard dengan 4 metrik
- [x] Add new items dengan kategori
- [x] View all items dengan search
- [x] Edit & delete functionality
- [x] Settings untuk data management
- [ ] Export to CSV/Excel
- [ ] Import from CSV
- [ ] Charts & analytics
- [ ] Multi-user support
- [ ] Dark mode theme


---

## 👥 Credits

**Built with ❤️ by Kirana, Billa, Hisyam, Arqam**

Stockify © 2025

---

<div align="center">

### 🌟 [Try Live Demo](https://stockifyapp.streamlit.app) 🌟

[![Star on GitHub](https://img.shields.io/github/stars/yourusername/stockify?style=social)](https://github.com/yourusername/stockify)

</div>
