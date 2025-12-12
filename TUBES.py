# Stockify_OOP.py - Professional Inventory Management System dengan OOP
# Jalankan: streamlit run Stockify_OOP.py

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd
import numpy as np
import uuid
from datetime import datetime
import json
import os
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# -----------------------
# 1. EXCEPTION CLASSES
# -----------------------
class InventoryError(Exception):
    """Base exception untuk semua error inventory"""
    pass

class ItemNotFoundError(InventoryError):
    """Exception ketika item tidak ditemukan"""
    pass

class InvalidItemError(InventoryError):
    """Exception ketika data item tidak valid"""
    pass

class DataExportError(InventoryError):
    """Exception ketika ekspor data gagal"""
    pass

class DataImportError(InventoryError):
    """Exception ketika impor data gagal"""
    pass

# -----------------------
# 2. MODEL CLASSES
# -----------------------
@dataclass
class Item:
    """Class untuk merepresentasikan satu item inventory"""
    id: str
    name: str
    quantity: int
    image_bytes: bytes
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def create(cls, name: str, quantity: int, image_bytes: bytes = None):
        """Factory method untuk membuat item baru"""
        return cls(
            id=str(uuid.uuid4()),
            name=name.strip(),
            quantity=max(0, quantity),  # Pastikan quantity tidak negatif
            image_bytes=image_bytes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def update(self, name: str = None, quantity: int = None, image_bytes: bytes = None):
        """Update atribut item"""
        if name:
            self.name = name.strip()
        if quantity is not None:
            self.quantity = max(0, quantity)
        if image_bytes:
            self.image_bytes = image_bytes
        self.updated_at = datetime.now()
    
    def get_stock_status(self, threshold: int = 5) -> Tuple[str, str, str]:
        """Mendapatkan status stock berdasarkan quantity"""
        if self.quantity == 0:
            return ("danger", "🔴", "Out of Stock")
        elif self.quantity <= threshold:
            return ("warning", "🟡", "Low Stock")
        else:
            return ("success", "🟢", "In Stock")
    
    def to_dict(self) -> Dict:
        """Convert item ke dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# -----------------------
# 3. SERVICE CLASSES
# -----------------------
class InventoryManager:
    """Class untuk mengelola operasi CRUD inventory"""
    
    def __init__(self, storage_file: str = "inventory_data.json"):
        self.storage_file = storage_file
        self.items: List[Item] = []
        self.low_stock_threshold = 5
        self.load_data()
    
    # === CRUD OPERATIONS ===
    def add_item(self, name: str, quantity: int, image_bytes: bytes = None) -> Item:
        """Menambahkan item baru ke inventory"""
        if not name or not name.strip():
            raise InvalidItemError("Nama item tidak boleh kosong")
        
        if quantity < 0:
            raise InvalidItemError("Quantity tidak boleh negatif")
        
        new_item = Item.create(name, quantity, image_bytes)
        self.items.append(new_item)
        self.save_data()
        return new_item
    
    def get_item(self, item_id: str) -> Item:
        """Mendapatkan item berdasarkan ID"""
        for item in self.items:
            if item.id == item_id:
                return item
        raise ItemNotFoundError(f"Item dengan ID {item_id} tidak ditemukan")
    
    def update_item(self, item_id: str, **kwargs) -> Item:
        """Update item yang ada"""
        item = self.get_item(item_id)
        item.update(**kwargs)
        self.save_data()
        return item
    
    def delete_item(self, item_id: str) -> bool:
        """Menghapus item dari inventory"""
        initial_count = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        
        if len(self.items) == initial_count:
            raise ItemNotFoundError(f"Item dengan ID {item_id} tidak ditemukan")
        
        self.save_data()
        return True
    
    # === SEARCH & FILTER ===
    def search_items(self, search_term: str = "") -> List[Item]:
        """Mencari item berdasarkan nama"""
        if not search_term:
            return self.items
        
        search_term = search_term.lower()
        return [item for item in self.items if search_term in item.name.lower()]
    
    def get_low_stock_items(self) -> List[Item]:
        """Mendapatkan item dengan stock rendah"""
        return [item for item in self.items 
                if 0 < item.quantity <= self.low_stock_threshold]
    
    def get_out_of_stock_items(self) -> List[Item]:
        """Mendapatkan item yang habis stock"""
        return [item for item in self.items if item.quantity == 0]
    
    # === STATISTICS ===
    def get_statistics(self) -> Dict[str, Any]:
        """Mendapatkan statistik inventory"""
        return {
            "total_items": len(self.items),
            "total_quantity": sum(item.quantity for item in self.items),
            "average_quantity": self._calculate_average(),
            "low_stock_count": len(self.get_low_stock_items()),
            "out_of_stock_count": len(self.get_out_of_stock_items()),
            "recent_items": sorted(self.items, 
                                  key=lambda x: x.updated_at, 
                                  reverse=True)[:5]
        }
    
    def _calculate_average(self) -> float:
        """Menghitung rata-rata quantity"""
        if not self.items:
            return 0.0
        return sum(item.quantity for item in self.items) / len(self.items)
    
    # === DATA PERSISTENCE ===
    def save_data(self):
        """Menyimpan data ke file JSON"""
        try:
            data = {
                "items": [item.to_dict() for item in self.items],
                "low_stock_threshold": self.low_stock_threshold,
                "last_saved": datetime.now().isoformat()
            }
            
            # Simpan image bytes terpisah
            for item_dict in data["items"]:
                if hasattr(self.get_item(item_dict["id"]), 'image_bytes'):
                    item = self.get_item(item_dict["id"])
                    if item.image_bytes:
                        # Simpan gambar sebagai file terpisah
                        image_filename = f"images/{item.id}.png"
                        os.makedirs("images", exist_ok=True)
                        with open(image_filename, "wb") as f:
                            f.write(item.image_bytes)
                        item_dict["image_file"] = image_filename
            
            with open(self.storage_file, "w") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            raise DataExportError(f"Gagal menyimpan data: {str(e)}")
    
    def load_data(self):
        """Memuat data dari file JSON"""
        try:
            if not os.path.exists(self.storage_file):
                self.items = []
                return
            
            with open(self.storage_file, "r") as f:
                data = json.load(f)
            
            self.low_stock_threshold = data.get("low_stock_threshold", 5)
            self.items = []
            
            for item_data in data.get("items", []):
                # Load gambar dari file terpisah jika ada
                image_bytes = None
                if "image_file" in item_data:
                    try:
                        with open(item_data["image_file"], "rb") as img_file:
                            image_bytes = img_file.read()
                    except:
                        image_bytes = None
                
                item = Item(
                    id=item_data["id"],
                    name=item_data["name"],
                    quantity=item_data["quantity"],
                    image_bytes=image_bytes,
                    created_at=datetime.fromisoformat(item_data["created_at"]),
                    updated_at=datetime.fromisoformat(item_data["updated_at"])
                )
                self.items.append(item)
                
        except Exception as e:
            raise DataImportError(f"Gagal memuat data: {str(e)}")
    
    # === EXPORT/IMPORT ===
    def export_to_csv(self) -> bytes:
        """Export inventory ke CSV"""
        try:
            df = pd.DataFrame([{
                "ID": item.id,
                "Name": item.name,
                "Quantity": item.quantity,
                "Status": item.get_stock_status(self.low_stock_threshold)[2],
                "Created": item.created_at.strftime('%Y-%m-%d'),
                "Updated": item.updated_at.strftime('%Y-%m-%d')
            } for item in self.items])
            
            return df.to_csv(index=False).encode('utf-8')
            
        except Exception as e:
            raise DataExportError(f"Gagal export ke CSV: {str(e)}")
    
    def import_from_csv(self, csv_bytes: bytes) -> int:
        """Import items dari CSV"""
        try:
            df = pd.read_csv(io.BytesIO(csv_bytes))
            
            required_columns = ["Name", "Quantity"]
            for col in required_columns:
                if col not in df.columns:
                    raise DataImportError(f"Kolom '{col}' tidak ditemukan")
            
            imported_count = 0
            for _, row in df.iterrows():
                if pd.notna(row.get("Name")):
                    self.add_item(
                        name=str(row["Name"]),
                        quantity=int(row.get("Quantity", 0))
                    )
                    imported_count += 1
            
            self.save_data()
            return imported_count
            
        except Exception as e:
            raise DataImportError(f"Gagal import dari CSV: {str(e)}")


class ReportGenerator:
    """Class untuk generate laporan inventory"""
    
    def __init__(self, inventory_manager: InventoryManager):
        self.inventory = inventory_manager
    
    def generate_summary_report(self) -> Dict:
        """Generate laporan summary"""
        stats = self.inventory.get_statistics()
        
        return {
            "overview": {
                "Total Items": stats["total_items"],
                "Total Quantity": stats["total_quantity"],
                "Average per Item": f"{stats['average_quantity']:.1f}"
            },
            "alerts": {
                "Low Stock": stats["low_stock_count"],
                "Out of Stock": stats["out_of_stock_count"]
            }
        }
    
    def generate_stock_distribution(self) -> Dict[str, int]:
        """Generate distribusi status stock"""
        distribution = {"In Stock": 0, "Low Stock": 0, "Out of Stock": 0}
        
        for item in self.inventory.items:
            status = item.get_stock_status(self.inventory.low_stock_threshold)[2]
            distribution[status] += 1
        
        return distribution
    
    def generate_top_items_chart_data(self, limit: int = 10) -> pd.DataFrame:
        """Generate data untuk chart top items"""
        sorted_items = sorted(self.inventory.items, 
                            key=lambda x: x.quantity, 
                            reverse=True)[:limit]
        
        data = {
            "Item": [item.name for item in sorted_items],
            "Quantity": [item.quantity for item in sorted_items],
            "Status": [item.get_stock_status(self.inventory.low_stock_threshold)[2] 
                      for item in sorted_items]
        }
        
        return pd.DataFrame(data)


class ImageProcessor:
    """Class untuk memproses gambar"""
    
    # Color mapping untuk avatar
    COLOR_MAP = {
        'primary': (37, 99, 235),
        'success': (16, 185, 129),
        'accent': (139, 92, 246),
        'warning': (245, 158, 11),
    }
    
    @staticmethod
    def generate_avatar(size: int = 256, color: str = 'primary') -> Image.Image:
        """Generate default avatar"""
        img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        bg_color = ImageProcessor.COLOR_MAP.get(color, ImageProcessor.COLOR_MAP['primary'])
        
        # Draw circle background
        draw.ellipse((10, 10, size-10, size-10), fill=bg_color + (255,))
        
        # Draw simple user icon
        head_size = size // 4
        cx, cy = size // 2, size // 2 - size // 8
        draw.ellipse((cx - head_size//2, cy - head_size//2, 
                     cx + head_size//2, cy + head_size//2), fill=(255, 255, 255))
        
        # Draw body
        body_width = size // 2
        body_height = size // 3
        body_top = cy + head_size // 2 - 10
        draw.ellipse((cx - body_width//2, body_top, 
                     cx + body_width//2, body_top + body_height), fill=(255, 255, 255))
        
        return img
    
    @staticmethod
    def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
        """Convert PIL Image ke bytes"""
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        return buf.getvalue()
    
    @staticmethod
    def validate_image(file_bytes: bytes) -> bool:
        """Validasi gambar yang diupload"""
        try:
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()  # Verify it's a valid image
            return True
        except:
            return False
    
    @staticmethod
    def resize_image(image_bytes: bytes, max_size: Tuple[int, int] = (256, 256)) -> bytes:
        """Resize gambar ke ukuran maksimum"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            return buf.getvalue()
        except:
            return image_bytes  # Return original jika gagal


# -----------------------
# 4. UI COMPONENT CLASSES
# -----------------------
class UIConfig:
    """Class untuk konfigurasi UI"""
    
    COLORS = {
    # Brand / Primary Colors
    'primary': '#2563EB',
    'primary_dark': '#1E3A8A',
    'primary_hover': '#1D4ED8',
    
    # Secondary Colors
    'success': '#10B981',
    'success_dark': '#047857',
    'warning': '#F59E0B',
    'warning_dark': '#B45309',
    'danger': '#EF4444',
    'danger_dark': '#B91C1C',
    'danger_hover': '#DC2626',
    'accent': '#8B5CF6',
    'accent_dark': '#6D28D9',
    
    # Neutral System
    'neutral_0': '#FFFFFF',
    'neutral_50': '#F9FAFB',
    'neutral_100': '#F3F4F6',
    'neutral_200': '#E5E7EB',
    'neutral_300': '#D1D5DB',
    'neutral_500': '#6B7280',
    'neutral_700': '#374151',
    'neutral_900': '#111827',
    'neutral_muted': '#9CA3AF',
    
    # Badge Backgrounds
    'badge_success_bg': '#D1FAE5',
    'badge_success_text': '#065F46',
    'badge_warning_bg': '#FEF3C7',
    'badge_warning_text': '#B45309',
    'badge_danger_bg': '#FEE2E2',
    'badge_danger_text': '#B91C1C',
    'badge_info_bg': '#EDE9FE',
    'badge_info_text': '#5B21B6',
}
    
    @staticmethod
    def inject_css():
        """Inject custom CSS ke Streamlit"""
        css = f"""
        <style>
        /* CSS yang sama seperti versi original */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        * {{ font-family: 'Poppins', sans-serif; }}
        
        .card {{
            background: {UIConfig.COLORS['neutral_0']};
            border: 1px solid {UIConfig.COLORS['neutral_200']};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .badge-success {{
            background: #D1FAE5;
            color: #065F46;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .metric-card {{
            background: {UIConfig.COLORS['neutral_0']};
            border: 1px solid {UIConfig.COLORS['neutral_200']};
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.2s ease;
        }}
        
        .metric-value {{
            font-size: 32px;
            font-weight: 700;
            color: {UIConfig.COLORS['neutral_900']};
            margin: 0.5rem 0;
        }}
        
        .stButton > button {{
            background: {UIConfig.COLORS['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.625rem 1.25rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)


class DashboardPage:
    """Class untuk halaman Dashboard"""
    
    def __init__(self, inventory_manager: InventoryManager):
        self.inventory = inventory_manager
        self.image_processor = ImageProcessor()
    
    def render(self):
        """Render halaman dashboard"""
        st.markdown("<h1>🏠 Dashboard</h1>", unsafe_allow_html=True)
        
        # Render metrics
        self._render_metrics()
        
        # Render alerts
        self._render_alerts()
        
        # Render recent activity
        self._render_recent_activity()
    
    def _render_metrics(self):
        """Render metric cards"""
        stats = self.inventory.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon'>📦</div>
                <div class='metric-value'>{stats['total_items']}</div>
                <div class='metric-label'>Total Items</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon'>📈</div>
                <div class='metric-value'>{stats['total_quantity']}</div>
                <div class='metric-label'>Total Quantity</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon'>⚠️</div>
                <div class='metric-value'>{stats['low_stock_count']}</div>
                <div class='metric-label'>Low Stock</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-icon'>🚫</div>
                <div class='metric-value'>{stats['out_of_stock_count']}</div>
                <div class='metric-label'>Out of Stock</div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_alerts(self):
        """Render alert sections"""
        low_stock = self.inventory.get_low_stock_items()
        out_of_stock = self.inventory.get_out_of_stock_items()
        
        if out_of_stock:
            st.markdown("<h3>🚫 Out of Stock Items</h3>", unsafe_allow_html=True)
            for item in out_of_stock[:3]:
                self._render_item_row(item, "danger")
        
        if low_stock:
            st.markdown("<h3>⚠️ Low Stock Alert</h3>", unsafe_allow_html=True)
            for item in low_stock[:3]:
                self._render_item_row(item, "warning")
    
    def _render_item_row(self, item: Item, alert_type: str):
        """Render satu baris item"""
        cols = st.columns([0.1, 0.7, 0.2])
        
        # Image
        if item.image_bytes:
            cols[0].image(Image.open(io.BytesIO(item.image_bytes)), width=60)
        else:
            cols[0].image(self.image_processor.generate_avatar(60, 'primary'), width=60)
        
        # Info
        cols[1].markdown(f"""
        <p style='font-weight: 600; margin: 0;'>{item.name}</p>
        <span class='badge-{alert_type}'>Qty: {item.quantity}</span>
        """, unsafe_allow_html=True)
        
        # Action button
        if cols[2].button("🔔 Reorder", key=f"reorder-{item.id}"):
            st.success(f"✅ Reorder notification sent for {item.name}")
    
    def _render_recent_activity(self):
        """Render recent activity section"""
        st.markdown("<h3>🕐 Recent Activity</h3>", unsafe_allow_html=True)
        
        recent_items = sorted(self.inventory.items, 
                             key=lambda x: x.updated_at, 
                             reverse=True)[:5]
        
        for item in recent_items:
            status = item.get_stock_status(self.inventory.low_stock_threshold)[0]
            
            cols = st.columns([0.1, 0.6, 0.3])
            
            # Image
            if item.image_bytes:
                cols[0].image(Image.open(io.BytesIO(item.image_bytes)), width=50)
            
            # Info
            cols[1].markdown(f"""
            <p style='font-weight: 600; margin: 0;'>{item.name}</p>
            <p style='font-size: 12px; color: #6B7280; margin: 0;'>
                Updated: {item.updated_at.strftime('%Y-%m-%d %H:%M')}
            </p>
            """, unsafe_allow_html=True)
            
            # Status
            cols[2].markdown(f"""
            <span class='badge-{status}'>Qty: {item.quantity}</span>
            """, unsafe_allow_html=True)


class ItemsPage:
    """Class untuk halaman Items"""
    
    def __init__(self, inventory_manager: InventoryManager):
        self.inventory = inventory_manager
        self.image_processor = ImageProcessor()
        
        # State untuk edit mode
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = {}
        if 'filter_text' not in st.session_state:
            st.session_state.filter_text = ""
    
    def render(self):
        """Render halaman items"""
        st.markdown("<h1>📋 All Items</h1>", unsafe_allow_html=True)
        
        # Search bar
        self._render_search()
        
        # Items list
        self._render_items_list()
        
        # Export/Import section
        self._render_data_management()
    
    def _render_search(self):
        """Render search bar"""
        col1, col2 = st.columns([3, 1])
        
        search_term = col1.text_input(
            "🔍 Search", 
            value=st.session_state.filter_text,
            placeholder="Search items..."
        )
        st.session_state.filter_text = search_term
    
    def _render_items_list(self):
        """Render list of items"""
        search_term = st.session_state.filter_text
        filtered_items = self.inventory.search_items(search_term)
        
        st.markdown(f"**{len(filtered_items)} items found**")
        
        for item in filtered_items:
            self._render_item_card(item)
    
    def _render_item_card(self, item: Item):
        """Render card untuk satu item"""
        status, icon, label = item.get_stock_status(self.inventory.low_stock_threshold)
        
        col1, col2, col3, col4 = st.columns([0.1, 0.5, 0.2, 0.2])
        
        # Image
        with col1:
            if item.image_bytes:
                st.image(Image.open(io.BytesIO(item.image_bytes)), width=60)
            else:
                st.image(self.image_processor.generate_avatar(60, 'primary'), width=60)
        
        # Info
        with col2:
            st.markdown(f"""
            <p style='font-weight: 600; margin: 0;'>{item.name}</p>
            <p style='font-size: 12px; color: #6B7280; margin: 0;'>
                ID: {item.id[:8]}... | Updated: {item.updated_at.strftime('%Y-%m-%d')}
            </p>
            """, unsafe_allow_html=True)
        
        # Status
        with col3:
            st.markdown(f"""
            <span class='badge-{status}'>{icon} {item.quantity} units</span>
            """, unsafe_allow_html=True)
        
        # Actions
        with col4:
            action_col1, action_col2 = st.columns(2)
            
            if action_col1.button("✏️", key=f"edit-btn-{item.id}"):
                st.session_state.edit_mode[item.id] = True
                st.rerun()
            
            if action_col2.button("🗑️", key=f"del-btn-{item.id}"):
                try:
                    self.inventory.delete_item(item.id)
                    st.success(f"✅ '{item.name}' deleted!")
                    st.rerun()
                except ItemNotFoundError as e:
                    st.error(str(e))
        
        # Edit mode expander
        if st.session_state.edit_mode.get(item.id, False):
            self._render_edit_form(item)
    
    def _render_edit_form(self, item: Item):
        """Render form untuk edit item"""
        with st.expander(f"✏️ Edit '{item.name}'", expanded=True):
            with st.form(f"edit-form-{item.id}"):
                new_name = st.text_input("Name", value=item.name)
                new_qty = st.number_input("Quantity", min_value=0, value=item.quantity)
                new_image = st.file_uploader("Change Image", type=["png", "jpg", "jpeg"])
                
                col1, col2 = st.columns(2)
                
                if col1.form_submit_button("💾 Save"):
                    try:
                        image_bytes = None
                        if new_image:
                            image_bytes = new_image.read()
                        
                        self.inventory.update_item(
                            item.id, 
                            name=new_name, 
                            quantity=new_qty,
                            image_bytes=image_bytes
                        )
                        st.session_state.edit_mode[item.id] = False
                        st.success("✅ Item updated!")
                        st.rerun()
                    except InvalidItemError as e:
                        st.error(str(e))
                
                if col2.form_submit_button("❌ Cancel"):
                    st.session_state.edit_mode[item.id] = False
                    st.rerun()
    
    def _render_data_management(self):
        """Render export/import section"""
        st.markdown("---")
        st.markdown("<h3>📤 Export / Import</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export to CSV"):
                try:
                    csv_data = self.inventory.export_to_csv()
                    
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv_data,
                        file_name=f"stockify_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                except DataExportError as e:
                    st.error(str(e))
        
        with col2:
            uploaded_file = st.file_uploader("📤 Import CSV", type=["csv"])
            if uploaded_file:
                try:
                    imported_count = self.inventory.import_from_csv(uploaded_file.getvalue())
                    st.success(f"✅ {imported_count} items imported!")
                    st.rerun()
                except DataImportError as e:
                    st.error(str(e))


# -----------------------
# 5. MAIN APPLICATION CLASS
# -----------------------
class StockifyApp:
    """Main application class untuk Stockify"""
    
    def __init__(self):
        # Initialize services
        self.inventory_manager = InventoryManager()
        self.report_generator = ReportGenerator(self.inventory_manager)
        self.image_processor = ImageProcessor()
        
        # Initialize UI config
        self.ui_config = UIConfig()
        
        # Initialize pages
        self.dashboard_page = DashboardPage(self.inventory_manager)
        self.items_page = ItemsPage(self.inventory_manager)
        
        # App state
        self.current_page = "Dashboard"
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state variables"""
        if 'profile_image' not in st.session_state:
            default_avatar = self.image_processor.generate_avatar(256, 'primary')
            st.session_state.profile_image = self.image_processor.image_to_bytes(default_avatar)
    
    def _render_sidebar(self):
        """Render sidebar navigation"""
        with st.sidebar:
            # Profile section
            try:
                profile_img = Image.open(io.BytesIO(st.session_state.profile_image))
                st.image(profile_img, width=100)
            except:
                st.image(self.image_processor.generate_avatar(100, 'primary'), width=100)
            
            # App title
            st.markdown("<h1 style='color: white;'>📦 Stockify</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: rgba(255,255,255,0.8);'>Smart Inventory System</p>", 
                       unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Navigation
            page_options = {
                "🏠 Dashboard": "Dashboard",
                "➕ Add Item": "Add Item", 
                "📋 Items": "Items",
                "📊 Reports": "Reports",
                "⚙️ Settings": "Settings"
            }
            
            selected_label = st.radio(
                "Navigation",
                list(page_options.keys()),
                label_visibility="collapsed"
            )
            
            self.current_page = page_options[selected_label]
    
    def _render_add_item_page(self):
        """Render add item page"""
        st.markdown("<h1>➕ Add New Item</h1>", unsafe_allow_html=True)
        
        with st.form("add_item_form"):
            col1, col2 = st.columns([3, 1])
            
            name = col1.text_input("🏷️ Item Name *", placeholder="Enter item name...")
            quantity = col2.number_input("📊 Quantity *", min_value=0, value=1)
            
            image_file = st.file_uploader("📷 Upload Photo (Optional)", 
                                         type=["png", "jpg", "jpeg"])
            
            submitted = st.form_submit_button("✅ Add Item")
            
            if submitted:
                try:
                    image_bytes = None
                    if image_file:
                        image_bytes = image_file.read()
                    
                    new_item = self.inventory_manager.add_item(name, quantity, image_bytes)
                    st.success(f"✅ Item '{new_item.name}' added successfully!")
                    st.balloons()
                except InvalidItemError as e:
                    st.error(f"❌ {str(e)}")
    
    def _render_settings_page(self):
        """Render settings page"""
        st.markdown("<h1>⚙️ Settings</h1>", unsafe_allow_html=True)
        
        # Low stock threshold
        st.markdown("### 📦 Inventory Settings")
        new_threshold = st.number_input(
            "Low Stock Threshold",
            min_value=1,
            max_value=100,
            value=self.inventory_manager.low_stock_threshold
        )
        
        if st.button("💾 Save Threshold"):
            self.inventory_manager.low_stock_threshold = new_threshold
            self.inventory_manager.save_data()
            st.success(f"✅ Threshold updated to {new_threshold}")
        
        # Data management
        st.markdown("### 🗄️ Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Items", use_container_width=True):
                if st.checkbox("Confirm deletion of all items"):
                    self.inventory_manager.items = []
                    self.inventory_manager.save_data()
                    st.success("✅ All items cleared!")
                    st.rerun()
        
        with col2:
            if st.button("🔄 Reset to Demo Data", use_container_width=True):
                # Add some demo items
                demo_items = [
                    ("Laptop", 15),
                    ("Mouse", 3),
                    ("Keyboard", 20),
                    ("Monitor", 8),
                    ("Headphones", 0)
                ]
                
                for name, qty in demo_items:
                    self.inventory_manager.add_item(name, qty)
                
                st.success("✅ Demo data loaded!")
                st.rerun()
    
    def run(self):
        """Main method untuk menjalankan aplikasi"""
        # Configure page
        st.set_page_config(
            page_title="Stockify - Inventory Management",
            page_icon="📦",
            layout="wide"
        )
        
        # Inject CSS
        self.ui_config.inject_css()
        
        # Render sidebar
        self._render_sidebar()
        
        # Render selected page
        if self.current_page == "Dashboard":
            self.dashboard_page.render()
        elif self.current_page == "Add Item":
            self._render_add_item_page()
        elif self.current_page == "Items":
            self.items_page.render()
        elif self.current_page == "Reports":
            # Render reports page
            st.markdown("<h1>📊 Reports</h1>", unsafe_allow_html=True)
            
            # Generate and display reports
            summary = self.report_generator.generate_summary_report()
            distribution = self.report_generator.generate_stock_distribution()
            chart_data = self.report_generator.generate_top_items_chart_data()
            
            # Display summary
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Items", summary["overview"]["Total Items"])
            col2.metric("Total Quantity", summary["overview"]["Total Quantity"])
            col3.metric("Average per Item", summary["overview"]["Average per Item"])
            
            # Display chart
            st.bar_chart(chart_data.set_index("Item")["Quantity"])
            
        elif self.current_page == "Settings":
            self._render_settings_page()
        
        # Render footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #6B7280; padding: 2rem;'>"
            "Built with ❤️ using Streamlit | Stockify OOP v1.0 | © 2024"
            "</div>",
            unsafe_allow_html=True
        )


# -----------------------
# 6. APPLICATION ENTRY POINT
# -----------------------
if __name__ == "__main__":
    try:
        # Create and run the application
        app = StockifyApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        st.write("Please refresh the page or contact support.")
