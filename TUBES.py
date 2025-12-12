# Stockify_CSV.py - Inventory Management System dengan CSV
# Jalankan: streamlit run Stockify_CSV.py

import streamlit as st
from PIL import Image, ImageDraw
import io
import pandas as pd
from datetime import datetime
import csv
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# ======================
# DATA MODEL
# ======================
@dataclass
class Barang:
    """Model untuk barang inventory"""
    id: str
    nama: str
    jumlah: int
    category: str
    image_path: str
    created_at: str
    
    def get_id(self) -> str:
        return self.id
    
    def get_nama(self) -> str:
        return self.nama
    
    def get_jumlah(self) -> int:
        return self.jumlah
    
    def set_nama(self, nama: str):
        self.nama = nama
    
    def set_jumlah(self, jumlah: int):
        self.jumlah = jumlah
    
    def tambah_stok(self, amount: int):
        """Tambah stok barang"""
        self.jumlah += amount
    
    def kurangi_stok(self, amount: int):
        """Kurangi stok barang"""
        if self.jumlah >= amount:
            self.jumlah -= amount
            return True
        return False
    
    def get_status(self):
        """Dapatkan status stock"""
        if self.jumlah == 0:
            return ("🔴", "Out of Stock", "#FEE2E2", "#991B1B")
        elif self.jumlah <= 5:
            return ("🟡", "Low Stock", "#FEF3C7", "#92400E")
        return ("🟢", "In Stock", "#D1FAE5", "#065F46")

# ======================
# REPOSITORY LAYER
# ======================
class InventoryRepository:
    """Repository untuk mengelola data barang dengan CSV"""
    
    def __init__(self, filename: str = "inventory.csv"):
        self.filename = filename
        self.barang_list: List[Barang] = []
        self._load_from_csv()
    
    def create_barang(self, nama: str, jumlah: int, category: str, image_path: str = "") -> Barang:
        """Buat barang baru"""
        barang = Barang(
            id=str(len(self.barang_list) + 1),
            nama=nama,
            jumlah=jumlah,
            category=category,
            image_path=image_path,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        self.barang_list.append(barang)
        self._save_to_csv()
        return barang
    
    def get_all(self) -> List[Barang]:
        """Dapatkan semua barang"""
        return self.barang_list
    
    def get_by_nama(self, nama: str) -> List[Barang]:
        """Cari barang berdasarkan nama"""
        return [b for b in self.barang_list if nama.lower() in b.nama.lower()]
    
    def update_barang(self, barang_id: str, **kwargs) -> bool:
        """Update data barang"""
        for barang in self.barang_list:
            if barang.id == barang_id:
                for key, val in kwargs.items():
                    setattr(barang, key, val)
                self._save_to_csv()
                return True
        return False
    
    def delete_barang(self, barang_id: str) -> bool:
        """Hapus barang"""
        initial_length = len(self.barang_list)
        self.barang_list = [b for b in self.barang_list if b.id != barang_id]
        if len(self.barang_list) < initial_length:
            self._save_to_csv()
            return True
        return False
    
    def _save_to_csv(self):
        """Simpan data ke CSV"""
        if not self.barang_list:
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'nama', 'jumlah', 'category', 'image_path', 'created_at']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
            return
        
        with open(self.filename, 'w', newline='', encoding='utf-8') as f:
            data = [asdict(b) for b in self.barang_list]
            fieldnames = data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def _load_from_csv(self):
        """Load data dari CSV"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.barang_list = []
                    
                    for row in reader:
                        row['jumlah'] = int(row['jumlah'])
                        self.barang_list.append(Barang(**row))
            except Exception as e:
                self.barang_list = []
                print(f"Error loading CSV: {e}")

# ======================
# MANAGER LAYER
# ======================
class StockManager:
    """Manager untuk mengelola operasi stok"""
    
    def __init__(self, inventory_repo: InventoryRepository):
        self.inventory_repo = inventory_repo
    
    def tambah_barang(self, nama: str, jumlah: int, category: str, image_path: str = "") -> Barang:
        """Tambah barang baru ke inventory"""
        return self.inventory_repo.create_barang(nama, jumlah, category, image_path)
    
    def tambah_stok(self, barang_id: str, amount: int) -> bool:
        """Tambah stok barang yang sudah ada"""
        for barang in self.inventory_repo.get_all():
            if barang.id == barang_id:
                barang.tambah_stok(amount)
                self.inventory_repo._save_to_csv()
                return True
        return False
    
    def kurangi_stok(self, barang_id: str, amount: int) -> bool:
        """Kurangi stok barang"""
        for barang in self.inventory_repo.get_all():
            if barang.id == barang_id:
                if barang.kurangi_stok(amount):
                    self.inventory_repo._save_to_csv()
                    return True
                return False
        return False
    
    def cek_stok(self, barang_id: str) -> Optional[int]:
        """Cek jumlah stok barang"""
        for barang in self.inventory_repo.get_all():
            if barang.id == barang_id:
                return barang.get_jumlah()
        return None
    
    def laporang_stok(self) -> Dict:
        """Buat laporan statistik stok"""
        barang_list = self.inventory_repo.get_all()
        return {
            "total_items": len(barang_list),
            "total_quantity": sum(b.jumlah for b in barang_list),
            "low_stock": len([b for b in barang_list if 0 < b.jumlah <= 5]),
            "out_of_stock": len([b for b in barang_list if b.jumlah == 0])
        }

# ======================
# UI STYLING
# ======================
def apply_styles():
    """CSS styling dengan warna menarik"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    }
    
    [data-testid="stSidebar"] h1 {
        color: white !important;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 10px;
    }
    
    [data-testid="stSidebar"] p {
        color: rgba(255,255,255,0.8);
        text-align: center;
        font-size: 14px;
    }
    
    /* Radio buttons di sidebar */
    [data-testid="stSidebar"] .stRadio > label {
        color: white !important;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] label[data-baseweb="radio"] {
        background: rgba(255,255,255,0.1);
        padding: 12px 16px;
        border-radius: 8px;
        margin: 4px 0;
        transition: all 0.3s;
    }
    
    [data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
        background: rgba(255,255,255,0.2);
        transform: translateX(5px);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-icon {
        font-size: 36px;
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin: 8px 0;
    }
    
    .metric-label {
        font-size: 14px;
        color: rgba(255,255,255,0.9);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Item Cards */
    .item-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.3s;
    }
    
    .item-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 8px 16px rgba(59,130,246,0.2);
        transform: translateY(-2px);
    }
    
    .item-name {
        font-size: 18px;
        font-weight: 700;
        color: #1f2937;
        margin: 8px 0;
    }
    
    .item-category {
        display: inline-block;
        background: #dbeafe;
        color: #1e40af;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 8px 0;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(102,126,234,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102,126,234,0.4);
    }
    
    /* Headers */
    h1 {
        color: #1f2937;
        font-weight: 700;
        margin-bottom: 24px;
    }
    
    h3 {
        color: #374151;
        font-weight: 600;
        margin: 24px 0 16px 0;
    }
    
    /* Input Fields */
    .stTextInput input, .stNumberInput input {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        padding: 12px;
        transition: border-color 0.3s;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }
    
    /* File Uploader */
    .stFileUploader {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 24px;
        background: #f9fafb;
    }
    
    /* Chart styling */
    .stBarChart {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ======================
# PAGE RENDERERS
# ======================
def render_dashboard(manager: StockManager):
    """Dashboard dengan metrics"""
    st.markdown("<h1>🏠 Dashboard</h1>", unsafe_allow_html=True)
    
    stats = manager.laporang_stok()
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        (col1, "📦", stats["total_items"], "Total Items", "#667eea"),
        (col2, "📊", stats["total_quantity"], "Total Stock", "#48bb78"),
        (col3, "⚠️", stats["low_stock"], "Low Stock", "#f6ad55"),
        (col4, "🚫", stats["out_of_stock"], "Out of Stock", "#fc8181")
    ]
    
    for col, icon, val, label, color in metrics:
        col.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%);'>
            <div class='metric-icon'>{icon}</div>
            <div class='metric-value'>{val}</div>
            <div class='metric-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent Items
    st.markdown("### 🕐 Recent Items")
    items = manager.inventory_repo.get_all()
    if items:
        for barang in items[-5:]:
            icon, status, bg, text = barang.get_status()
            st.markdown(f"""
            <div class='item-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <div class='item-name'>{barang.nama}</div>
                        <span class='item-category'>{barang.category}</span>
                    </div>
                    <span class='status-badge' style='background: {bg}; color: {text};'>
                        {icon} {barang.jumlah} units
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📦 No items yet. Add your first item!")

def render_add_item(manager: StockManager):
    """Form tambah item"""
    st.markdown("<h1>➕ Add New Item</h1>", unsafe_allow_html=True)
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        
        nama = col1.text_input("🏷️ Item Name", placeholder="Enter item name...")
        category = col2.selectbox("📁 Category", 
                                  ["Electronics", "Furniture", "Stationery", "Tools", "Other"])
        
        jumlah = st.number_input("📊 Quantity", min_value=0, value=1)
        
        if st.form_submit_button("✅ Add Item", use_container_width=True):
            if nama:
                manager.tambah_barang(nama, jumlah, category)
                st.success(f"✅ '{nama}' added successfully!")
                st.balloons()
            else:
                st.error("❌ Please enter item name")

def render_items(manager: StockManager):
    """List semua items"""
    st.markdown("<h1>📋 All Items</h1>", unsafe_allow_html=True)
    
    # Search
    search = st.text_input("🔍 Search", placeholder="Search items...")
    items = manager.inventory_repo.get_by_nama(search) if search else manager.inventory_repo.get_all()
    
    st.markdown(f"**{len(items)} items found**")
    
    if not items:
        st.info("📦 No items found. Try different search terms or add new items.")
        return
    
    # Items list
    for barang in items:
        icon, status, bg, text = barang.get_status()
        
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div class='item-card'>
                <div class='item-name'>{barang.nama}</div>
                <span class='item-category'>{barang.category}</span>
                <span class='status-badge' style='background: {bg}; color: {text}; margin-left: 12px;'>
                    {icon} {barang.jumlah}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("➕", key=f"add_{barang.id}", help="Add stock"):
                manager.tambah_stok(barang.id, 1)
                st.rerun()
        
        with col3:
            if st.button("➖", key=f"sub_{barang.id}", help="Remove stock"):
                if manager.kurangi_stok(barang.id, 1):
                    st.rerun()
                else:
                    st.error("Cannot reduce below 0")
        
        with col4:
            if st.button("🗑️", key=f"del_{barang.id}", help="Delete"):
                manager.inventory_repo.delete_barang(barang.id)
                st.rerun()

def render_reports(manager: StockManager):
    """Laporan dan statistik"""
    st.markdown("<h1>📊 Reports</h1>", unsafe_allow_html=True)
    
    stats = manager.laporang_stok()
    
    # Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Items", stats["total_items"])
    col2.metric("📊 Total Quantity", stats["total_quantity"])
    col3.metric("📈 Average", f"{stats['total_quantity']/stats['total_items']:.1f}" if stats['total_items'] > 0 else "0")
    
    # Chart
    items = manager.inventory_repo.get_all()
    if items:
        st.markdown("### 📈 Top Items by Stock")
        df = pd.DataFrame([{"Item": b.nama, "Quantity": b.jumlah} for b in items])
        df = df.sort_values("Quantity", ascending=False).head(10)
        st.bar_chart(df.set_index("Item"))
        
        # Export
        st.markdown("### 📥 Export Data")
        csv_data = df.to_csv(index=False)
        st.download_button("⬇️ Download CSV Report", csv_data, "stockify_report.csv", "text/csv")
        
        # Show raw data
        with st.expander("📄 View Raw CSV Data"):
            full_df = pd.DataFrame([asdict(b) for b in items])
            st.dataframe(full_df, use_container_width=True)
    else:
        st.info("📦 No data to display. Add some items first!")

def render_settings(manager: StockManager):
    """Pengaturan aplikasi"""
    st.markdown("<h1>⚙️ Settings</h1>", unsafe_allow_html=True)
    
    st.markdown("### 🗄️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🗑️ Clear All Data")
        if st.button("Clear All Data", use_container_width=True, type="secondary"):
            if st.checkbox("⚠️ I understand this will delete all data"):
                manager.inventory_repo.barang_list = []
                manager.inventory_repo._save_to_csv()
                st.success("✅ All data cleared!")
                st.rerun()
    
    with col2:
        st.markdown("#### 🔄 Load Demo Data")
        if st.button("Load Demo Data", use_container_width=True, type="primary"):
            demo = [
                ("Laptop Dell", 12, "Electronics"),
                ("Office Chair", 5, "Furniture"),
                ("Pen Blue", 0, "Stationery"),
                ("Hammer", 20, "Tools"),
                ("USB Cable", 3, "Electronics")
            ]
            for nama, qty, cat in demo:
                manager.tambah_barang(nama, qty, cat)
            st.success("✅ Demo data loaded!")
            st.rerun()
    
    # File Info
    st.markdown("---")
    st.markdown("### 📁 File Information")
    if os.path.exists(manager.inventory_repo.filename):
        file_size = os.path.getsize(manager.inventory_repo.filename)
        st.info(f"""
        **File:** `{manager.inventory_repo.filename}`  
        **Size:** {file_size} bytes  
        **Format:** CSV (Comma-Separated Values)  
        **Encoding:** UTF-8
        """)
    else:
        st.warning("⚠️ Data file not created yet. Add items to create the file.")

# ======================
# MAIN APP
# ======================
def main():
    st.set_page_config(
        page_title="Stockify - Inventory System",
        page_icon="📦",
        layout="wide"
    )
    
    apply_styles()
    
    # Initialize dengan pattern yang benar
    if 'repository' not in st.session_state:
        st.session_state.repository = InventoryRepository()
    
    if 'manager' not in st.session_state:
        st.session_state.manager = StockManager(st.session_state.repository)
    
    manager = st.session_state.manager
    
    # Sidebar
    with st.sidebar:
        st.markdown("<h1>📦 Stockify</h1>", unsafe_allow_html=True)
        st.markdown("<p>Smart Inventory System</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "➕ Add Item", "📋 Items", "📊 Reports", "⚙️ Settings"],
            label_visibility="collapsed"
        )
    
    # Render page
    pages = {
        "🏠 Dashboard": render_dashboard,
        "➕ Add Item": render_add_item,
        "📋 Items": render_items,
        "📊 Reports": render_reports,
        "⚙️ Settings": render_settings
    }
    
    pages[page](manager)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6b7280; padding: 20px;'>"
        "Built with ❤️ from Kirana, Billa, Hisyam, Arqam | Stockify | ©️ 2025"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
