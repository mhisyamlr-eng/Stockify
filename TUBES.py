# Stockify_Simple.py - Inventory Management System
# Jalankan: streamlit run Stockify_Simple.py

import streamlit as st
from PIL import Image, ImageDraw
import io
import pandas as pd
from datetime import datetime
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict

# ======================
# DATA MODEL
# ======================
@dataclass
class Item:
    """Model untuk item inventory"""
    id: str
    name: str
    quantity: int
    category: str
    image_path: str
    created_at: str
    
    def get_status(self):
        """Dapatkan status stock"""
        if self.quantity == 0:
            return ("🔴", "Out of Stock", "#FEE2E2", "#991B1B")
        elif self.quantity <= 5:
            return ("🟡", "Low Stock", "#FEF3C7", "#92400E")
        return ("🟢", "In Stock", "#D1FAE5", "#065F46")

# ======================
# DATA MANAGER
# ======================
class InventoryManager:
    """Kelola data inventory"""
    
    def __init__(self):
        self.file = "inventory.json"
        self.items: List[Item] = []
        self.load()
    
    def add(self, name: str, qty: int, category: str, img_path: str = ""):
        """Tambah item baru"""
        item = Item(
            id=str(len(self.items) + 1),
            name=name,
            quantity=qty,
            category=category,
            image_path=img_path,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        self.items.append(item)
        self.save()
        return item
    
    def update(self, item_id: str, **kwargs):
        """Update item"""
        for item in self.items:
            if item.id == item_id:
                for key, val in kwargs.items():
                    setattr(item, key, val)
                self.save()
                return True
        return False
    
    def delete(self, item_id: str):
        """Hapus item"""
        self.items = [i for i in self.items if i.id != item_id]
        self.save()
    
    def search(self, query: str = ""):
        """Cari item"""
        if not query:
            return self.items
        return [i for i in self.items if query.lower() in i.name.lower()]
    
    def get_stats(self):
        """Statistik inventory"""
        return {
            "total": len(self.items),
            "quantity": sum(i.quantity for i in self.items),
            "low_stock": len([i for i in self.items if 0 < i.quantity <= 5]),
            "out_stock": len([i for i in self.items if i.quantity == 0])
        }
    
    def save(self):
        """Simpan ke file"""
        data = [asdict(i) for i in self.items]
        with open(self.file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load dari file"""
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                data = json.load(f)
                self.items = [Item(**i) for i in data]

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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
def render_dashboard(inv: InventoryManager):
    """Dashboard dengan metrics"""
    st.markdown("<h1>🏠 Dashboard</h1>", unsafe_allow_html=True)
    
    stats = inv.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        (col1, "📦", stats["total"], "Total Items", "#667eea"),
        (col2, "📊", stats["quantity"], "Total Stock", "#48bb78"),
        (col3, "⚠️", stats["low_stock"], "Low Stock", "#f6ad55"),
        (col4, "🚫", stats["out_stock"], "Out of Stock", "#fc8181")
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
    for item in inv.items[-5:]:
        icon, status, bg, text = item.get_status()
        st.markdown(f"""
        <div class='item-card'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div class='item-name'>{item.name}</div>
                    <span class='item-category'>{item.category}</span>
                </div>
                <span class='status-badge' style='background: {bg}; color: {text};'>
                    {icon} {item.quantity} units
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_add_item(inv: InventoryManager):
    """Form tambah item"""
    st.markdown("<h1>➕ Add New Item</h1>", unsafe_allow_html=True)
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        
        name = col1.text_input("🏷️ Item Name", placeholder="Enter item name...")
        category = col2.selectbox("📁 Category", 
                                  ["Electronics", "Furniture", "Stationery", "Tools", "Other"])
        
        quantity = st.number_input("📊 Quantity", min_value=0, value=1)
        
        if st.form_submit_button("✅ Add Item", use_container_width=True):
            if name:
                inv.add(name, quantity, category)
                st.success(f"✅ '{name}' added successfully!")
                st.balloons()
            else:
                st.error("❌ Please enter item name")

def render_items(inv: InventoryManager):
    """List semua items"""
    st.markdown("<h1>📋 All Items</h1>", unsafe_allow_html=True)
    
    # Search
    search = st.text_input("🔍 Search", placeholder="Search items...")
    items = inv.search(search)
    
    st.markdown(f"**{len(items)} items found**")
    
    # Items list
    for item in items:
        icon, status, bg, text = item.get_status()
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div class='item-card'>
                <div class='item-name'>{item.name}</div>
                <span class='item-category'>{item.category}</span>
                <span class='status-badge' style='background: {bg}; color: {text}; margin-left: 12px;'>
                    {icon} {item.quantity}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("✏️ Edit", key=f"edit_{item.id}"):
                st.session_state[f"edit_{item.id}"] = True
        
        with col3:
            if st.button("🗑️ Delete", key=f"del_{item.id}"):
                inv.delete(item.id)
                st.rerun()
        
        # Edit form
        if st.session_state.get(f"edit_{item.id}", False):
            with st.form(f"form_{item.id}"):
                new_name = st.text_input("Name", value=item.name)
                new_qty = st.number_input("Quantity", value=item.quantity, min_value=0)
                new_cat = st.selectbox("Category", 
                                      ["Electronics", "Furniture", "Stationery", "Tools", "Other"],
                                      index=["Electronics", "Furniture", "Stationery", "Tools", "Other"].index(item.category))
                
                col_a, col_b = st.columns(2)
                if col_a.form_submit_button("💾 Save"):
                    inv.update(item.id, name=new_name, quantity=new_qty, category=new_cat)
                    st.session_state[f"edit_{item.id}"] = False
                    st.rerun()
                
                if col_b.form_submit_button("❌ Cancel"):
                    st.session_state[f"edit_{item.id}"] = False
                    st.rerun()

def render_reports(inv: InventoryManager):
    """Laporan dan statistik"""
    st.markdown("<h1>📊 Reports</h1>", unsafe_allow_html=True)
    
    stats = inv.get_stats()
    
    # Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Items", stats["total"])
    col2.metric("📊 Total Quantity", stats["quantity"])
    col3.metric("📈 Average", f"{stats['quantity']/stats['total']:.1f}" if stats['total'] > 0 else "0")
    
    # Chart
    if inv.items:
        st.markdown("### 📈 Top Items by Stock")
        df = pd.DataFrame([{"Item": i.name, "Quantity": i.quantity} for i in inv.items])
        df = df.sort_values("Quantity", ascending=False).head(10)
        st.bar_chart(df.set_index("Item"))
        
        # Export
        st.markdown("### 📥 Export Data")
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv, "stockify_report.csv", "text/csv")

def render_settings(inv: InventoryManager):
    """Pengaturan aplikasi"""
    st.markdown("<h1>⚙️ Settings</h1>", unsafe_allow_html=True)
    
    st.markdown("### 🗄️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            if st.checkbox("⚠️ Confirm deletion"):
                inv.items = []
                inv.save()
                st.success("✅ All data cleared!")
                st.rerun()
    
    with col2:
        if st.button("🔄 Load Demo Data", use_container_width=True):
            demo = [
                ("Laptop Dell", 12, "Electronics"),
                ("Office Chair", 5, "Furniture"),
                ("Pen Blue", 0, "Stationery"),
                ("Hammer", 20, "Tools"),
                ("USB Cable", 3, "Electronics")
            ]
            for name, qty, cat in demo:
                inv.add(name, qty, cat)
            st.success("✅ Demo data loaded!")
            st.rerun()

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
    
    # Initialize
    if 'inv' not in st.session_state:
        st.session_state.inv = InventoryManager()
    
    inv = st.session_state.inv
    
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
    
    pages[page](inv)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6b7280; padding: 20px;'>"
        "Built with ❤️ from Kirana, Billa, Arqam, Hisyam | Stockify  | © 2025"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
