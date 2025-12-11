# Stockify.py - Professional Inventory Management System
# Jalankan: streamlit run Stockify.py

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd
import numpy as np
import uuid
from datetime import datetime

# -----------------------
# PROFESSIONAL COLOR PALETTE
# -----------------------
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

# -----------------------
# Helper: Generate Avatar
# -----------------------
def generate_default_avatar(size=256, color='primary'):
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Color mapping
    color_map = {
        'primary': (37, 99, 235),
        'success': (16, 185, 129),
        'accent': (139, 92, 246),
        'warning': (245, 158, 11),
    }
    
    bg_color = color_map.get(color, color_map['primary'])
    
    # Circle background
    draw.ellipse((10, 10, size-10, size-10), fill=bg_color + (255,))
    
    # Simple user icon
    head_size = size // 4
    cx, cy = size // 2, size // 2 - size // 8
    draw.ellipse((cx - head_size//2, cy - head_size//2, 
                  cx + head_size//2, cy + head_size//2), fill=(255, 255, 255))
    
    # Body
    body_width = size // 2
    body_height = size // 3
    body_top = cy + head_size // 2 - 10
    draw.ellipse((cx - body_width//2, body_top, 
                  cx + body_width//2, body_top + body_height), fill=(255, 255, 255))
    
    return img

def pil_image_to_bytes(img, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()

# -----------------------
# Session State Initialization
# -----------------------
def init_state():
    defaults = {
        "items": [],
        "profile_img": pil_image_to_bytes(generate_default_avatar(256, 'primary')),
        "filter_text": "",
        "low_stock_threshold": 5,
        "edit_mode": {},
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# -----------------------
# CSS: Professional Styling with Poppins
# -----------------------
def inject_css():
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Poppins', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    .stApp {{
        background: {COLORS['neutral_50']};
    }}
    
    .main {{
        padding: 2rem;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['primary_dark']} 0%, {COLORS['primary']} 100%);
        padding: 2rem 1rem;
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    [data-testid="stSidebar"] .stRadio > label {{
        font-weight: 500;
        font-size: 14px;
        margin-bottom: 0.5rem;
    }}
    
    [data-testid="stSidebar"] [role="radiogroup"] label {{
        background: rgba(255,255,255,0.08);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        transition: all 0.2s ease;
        cursor: pointer;
        border: 2px solid transparent;
        font-weight: 400;
    }}
    
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
        background: rgba(255,255,255,0.15);
        transform: translateX(4px);
    }}
    
    [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {{
        background: {COLORS['neutral_0']};
        color: {COLORS['primary']} !important;
        font-weight: 600;
        border-color: {COLORS['neutral_0']};
    }}
    
    /* Brand */
    .brand {{
        font-size: 28px;
        font-weight: 700;
        color: {COLORS['neutral_0']};
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }}
    
    .brand-subtitle {{
        font-size: 13px;
        font-weight: 400;
        color: rgba(255,255,255,0.8);
        margin-bottom: 1.5rem;
    }}
    
    /* Typography */
    h1 {{
        font-size: 32px;
        font-weight: 700;
        color: {COLORS['neutral_900']};
        margin-bottom: 0.5rem;
    }}
    
    h2 {{
        font-size: 24px;
        font-weight: 600;
        color: {COLORS['neutral_900']};
        margin: 1.5rem 0 1rem 0;
    }}
    
    h3 {{
        font-size: 20px;
        font-weight: 600;
        color: {COLORS['neutral_900']};
        margin: 1rem 0 0.75rem 0;
    }}
    
    p, .body-text {{
        font-size: 16px;
        font-weight: 400;
        color: {COLORS['neutral_700']};
        line-height: 1.6;
    }}
    
    .text-secondary {{
        font-size: 14px;
        font-weight: 400;
        color: {COLORS['neutral_500']};
    }}
    
    .caption {{
        font-size: 12px;
        font-weight: 300;
        color: {COLORS['neutral_500']};
    }}
    
    /* Cards */
    .card {{
        background: {COLORS['neutral_0']};
        border: 1px solid {COLORS['neutral_200']};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        transition: all 0.2s ease;
    }}
    
    .card:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: {COLORS['neutral_0']};
        border: 1px solid {COLORS['neutral_200']};
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s ease;
        height: 100%;
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.12);
    }}
    
    .metric-icon {{
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }}
    
    .metric-value {{
        font-size: 32px;
        font-weight: 700;
        color: {COLORS['neutral_900']};
        margin: 0.5rem 0;
    }}
    
    .metric-label {{
        font-size: 14px;
        font-weight: 500;
        color: {COLORS['neutral_500']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: {COLORS['primary']};
        color: {COLORS['neutral_0']};
        border: none;
        border-radius: 8px;
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
        cursor: pointer;
    }}
    
    .stButton > button:hover {{
        background: {COLORS['primary_hover']};
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }}
    
    /* Badges */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}
    
    .badge-success {{
        background: {COLORS['badge_success_bg']};
        color: {COLORS['badge_success_text']};
    }}
    
    .badge-warning {{
        background: {COLORS['badge_warning_bg']};
        color: {COLORS['badge_warning_text']};
    }}
    
    .badge-danger {{
        background: {COLORS['badge_danger_bg']};
        color: {COLORS['badge_danger_text']};
    }}
    
    .badge-info {{
        background: {COLORS['badge_info_bg']};
        color: {COLORS['badge_info_text']};
    }}
    
    /* Item Cards */
    .item-card {{
        background: {COLORS['neutral_0']};
        border: 1px solid {COLORS['neutral_200']};
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }}
    
    .item-card:hover {{
        border-color: {COLORS['primary']};
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }}
    
    /* Form Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {{
        border-radius: 8px;
        border: 1px solid {COLORS['neutral_300']};
        padding: 0.625rem 0.875rem;
        font-size: 14px;
        transition: all 0.2s ease;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: {COLORS['primary']};
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }}
    
    /* Tables */
    .dataframe {{
        border: 1px solid {COLORS['neutral_200']};
        border-radius: 8px;
    }}
    
    .dataframe thead tr {{
        background: {COLORS['neutral_100']};
    }}
    
    .dataframe thead th {{
        color: {COLORS['neutral_900']};
        font-weight: 600;
        padding: 0.75rem;
    }}
    
    .dataframe tbody tr:hover {{
        background: {COLORS['neutral_50']};
    }}
    
    .dataframe tbody td {{
        color: {COLORS['neutral_700']};
        padding: 0.75rem;
    }}
    
    /* Profile Container */
    .profile-container {{
        text-align: center;
        margin-bottom: 1.5rem;
    }}
    
    .profile-img {{
        border-radius: 50%;
        border: 3px solid rgba(255,255,255,0.2);
    }}
    
    /* Alert Boxes */
    .stAlert {{
        border-radius: 8px;
        border: none;
    }}
    
    /* Success Messages */
    .success-box {{
        background: {COLORS['badge_success_bg']};
        color: {COLORS['success_dark']};
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COLORS['success']};
        margin: 1rem 0;
    }}
    
    .warning-box {{
        background: {COLORS['badge_warning_bg']};
        color: {COLORS['warning_dark']};
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COLORS['warning']};
        margin: 1rem 0;
    }}
    
    .danger-box {{
        background: {COLORS['badge_danger_bg']};
        color: {COLORS['danger_dark']};
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {COLORS['danger']};
        margin: 1rem 0;
    }}
    
    /* Divider */
    hr {{
        border: none;
        border-top: 1px solid {COLORS['neutral_200']};
        margin: 2rem 0;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem;
        color: {COLORS['neutral_500']};
        font-size: 14px;
        font-weight: 400;
    }}
    
    /* Responsive */
    @media (max-width: 768px) {{
        .main {{
            padding: 1rem;
        }}
        
        h1 {{
            font-size: 24px;
        }}
        
        .metric-value {{
            font-size: 24px;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_css()

# -----------------------
# Core Functions
# -----------------------
def add_item(name: str, qty: int, image_bytes: bytes = None):
    """Add new item to inventory"""
    if image_bytes is None:
        image_bytes = pil_image_to_bytes(generate_default_avatar(256, 'primary'))
    
    item = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "qty": int(qty),
        "image": image_bytes,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    st.session_state["items"].append(item)
    return item

def update_item(item_id: str, name: str = None, qty: int = None, image_bytes: bytes = None):
    """Update existing item"""
    for idx, item in enumerate(st.session_state["items"]):
        if item["id"] == item_id:
            if name is not None:
                st.session_state["items"][idx]["name"] = name.strip()
            if qty is not None:
                st.session_state["items"][idx]["qty"] = int(qty)
            if image_bytes is not None:
                st.session_state["items"][idx]["image"] = image_bytes
            st.session_state["items"][idx]["updated_at"] = datetime.now()
            return True
    return False

def delete_item(item_id: str):
    """Delete item from inventory"""
    st.session_state["items"] = [it for it in st.session_state["items"] if it["id"] != item_id]

def get_items_filtered(filter_text: str = ""):
    """Get filtered items"""
    if not filter_text:
        return st.session_state["items"]
    ft = filter_text.lower()
    return [it for it in st.session_state["items"] if ft in it["name"].lower()]

def get_stock_status(qty: int):
    """Determine stock status"""
    threshold = st.session_state.get("low_stock_threshold", 5)
    if qty == 0:
        return "danger", "🔴", "Out of Stock"
    elif qty <= threshold:
        return "warning", "🟡", "Low Stock"
    else:
        return "success", "🟢", "In Stock"

# -----------------------
# Page Configuration
# -----------------------
st.set_page_config(
    page_title="Stockify - Inventory Management",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# Sidebar Navigation
# -----------------------
with st.sidebar:
    st.markdown("<div class='profile-container'>", unsafe_allow_html=True)
    try:
        profile_img = Image.open(io.BytesIO(st.session_state["profile_img"]))
        st.image(profile_img, width=100)
    except:
        st.image(generate_default_avatar(100, 'primary'), width=100)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='brand'>📦 Stockify</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-subtitle'>Smart Inventory System</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "➕ Add Item", "📋 Items", "📊 Reports", "⚙️ Settings"],
        label_visibility="collapsed"
    )

# -----------------------
# PAGE: Dashboard
# -----------------------
if page == "🏠 Dashboard":
    st.markdown("<h1>🏠 Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='text-secondary'>Overview of your inventory status</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    items = st.session_state["items"]
    total_skus = len(items)
    total_qty = sum(it["qty"] for it in items)
    threshold = st.session_state.get("low_stock_threshold", 5)
    low_stock = [it for it in items if 0 < it["qty"] <= threshold]
    out_of_stock = [it for it in items if it["qty"] == 0]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-icon'>📦</div>
            <div class='metric-value'>{total_skus}</div>
            <div class='metric-label'>Total Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-icon'>📈</div>
            <div class='metric-value'>{total_qty}</div>
            <div class='metric-label'>Total Quantity</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-icon'>⚠️</div>
            <div class='metric-value'>{len(low_stock)}</div>
            <div class='metric-label'>Low Stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-icon'>🚫</div>
            <div class='metric-value'>{len(out_of_stock)}</div>
            <div class='metric-label'>Out of Stock</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Alerts Section
    if out_of_stock:
        st.markdown("<h3>🚫 Out of Stock Items</h3>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        for it in out_of_stock[:5]:
            cols = st.columns([0.1, 0.6, 0.3])
            try:
                cols[0].image(Image.open(io.BytesIO(it["image"])), width=60)
            except:
                cols[0].image(generate_default_avatar(60, 'primary'), width=60)
            
            cols[1].markdown(f"""
            <p style='font-weight: 600; color: {COLORS['neutral_900']}; margin: 0;'>{it['name']}</p>
            <span class='badge badge-danger'>Out of Stock</span>
            """, unsafe_allow_html=True)
            
            if cols[2].button("🔔 Reorder", key=f"reorder-out-{it['id']}"):
                st.success(f"✅ Reorder notification sent for {it['name']}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    if low_stock:
        st.markdown("<h3>⚠️ Low Stock Alert</h3>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        for it in low_stock[:5]:
            cols = st.columns([0.1, 0.6, 0.3])
            try:
                cols[0].image(Image.open(io.BytesIO(it["image"])), width=60)
            except:
                cols[0].image(generate_default_avatar(60, 'primary'), width=60)
            
            cols[1].markdown(f"""
            <p style='font-weight: 600; color: {COLORS['neutral_900']}; margin: 0;'>{it['name']}</p>
            <span class='badge badge-warning'>Qty: {it['qty']}</span>
            """, unsafe_allow_html=True)
            
            if cols[2].button("🔔 Reorder", key=f"reorder-low-{it['id']}"):
                st.success(f"✅ Reorder notification sent for {it['name']}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent Activity
    st.markdown("<h3>🕐 Recent Activity</h3>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    recent_items = sorted(items, key=lambda x: x.get("updated_at", x["created_at"]), reverse=True)[:8]
    
    if recent_items:
        for it in recent_items:
            cols = st.columns([0.1, 0.65, 0.25])
            try:
                cols[0].image(Image.open(io.BytesIO(it["image"])), width=60)
            except:
                cols[0].image(generate_default_avatar(60, 'primary'), width=60)
            
            status, icon, label = get_stock_status(it["qty"])
            
            cols[1].markdown(f"""
            <p style='font-weight: 600; color: {COLORS['neutral_900']}; margin: 0;'>{it['name']}</p>
            <p class='caption'>Updated: {it.get('updated_at', it['created_at']).strftime('%Y-%m-%d %H:%M')}</p>
            """, unsafe_allow_html=True)
            
            cols[2].markdown(f"""
            <span class='badge badge-{status}'>{icon} Qty: {it['qty']}</span>
            """, unsafe_allow_html=True)
    else:
        st.info("🔍 No items yet. Start adding items!")
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# PAGE: Add Item
# -----------------------
elif page == "➕ Add Item":
    st.markdown("<h1>➕ Add New Item</h1>", unsafe_allow_html=True)
    st.markdown("<p class='text-secondary'>Add items to your inventory</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>📝 Item Details</h3>", unsafe_allow_html=True)
    
    with st.form("add_item_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        name = col1.text_input("🏷️ Item Name *", placeholder="Enter item name...")
        qty = col2.number_input("📊 Quantity *", min_value=0, value=1, step=1)
        
        image_file = st.file_uploader("📷 Upload Photo (Optional)", type=["png", "jpg", "jpeg"])
        
        col1, col2, col3 = st.columns([1, 1, 1])
        submitted = col2.form_submit_button("✅ Add Item", use_container_width=True)
        
        if submitted:
            if not name or name.strip() == "":
                st.error("⚠️ Item name is required!")
            else:
                image_bytes = None
                if image_file is not None:
                    image_bytes = image_file.read()
                else:
                    image_bytes = pil_image_to_bytes(generate_default_avatar(256, 'success'))
                
                add_item(name, qty, image_bytes)
                st.success(f"✅ Item '{name}' added successfully!")
                st.balloons()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Add Section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>⚡ Quick Add</h3>", unsafe_allow_html=True)
    st.markdown("<p class='text-secondary'>Fast entry for barcode scanning or quick input</p>", unsafe_allow_html=True)
    
    with st.form("quick_add_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        quick_name = col1.text_input("📱 Scan/Type Item", placeholder="Barcode or item name...")
        quick_qty = col2.number_input("Qty", min_value=1, value=1, step=1)
        
        if st.form_submit_button("🚀 Quick Add", use_container_width=True):
            if not quick_name or quick_name.strip() == "":
                st.error("⚠️ Item name is required!")
            else:
                add_item(quick_name, quick_qty, pil_image_to_bytes(generate_default_avatar(256, 'accent')))
                st.success(f"✅ '{quick_name}' added (Qty: {quick_qty})")
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# PAGE: Items List
# -----------------------
elif page == "📋 Items":
    st.markdown("<h1>📋 All Items</h1>", unsafe_allow_html=True)
    st.markdown("<p class='text-secondary'>Manage your inventory items</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Search and Filter
    col1, col2, col3 = st.columns([2, 1, 1])
    filter_text = col1.text_input("🔍 Search", value=st.session_state.get("filter_text", ""), 
                                   placeholder="Search items...", key="search_items")
    st.session_state["filter_text"] = filter_text
    
    # Export/Import buttons
    export_col, import_col = col2, col3
    
    items_filtered = get_items_filtered(filter_text)
    
    st.markdown(f"""
    <div class='card'>
        <h3 style='margin: 0;'>📊 {len(items_filtered)} items found</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Items Display
    if items_filtered:
        for item in items_filtered:
            st.markdown("<div class='item-card'>", unsafe_allow_html=True)
            
            cols = st.columns([0.1, 0.5, 0.2, 0.2])
            
            # Image
            try:
                cols[0].image(Image.open(io.BytesIO(item["image"])), width=70)
            except:
                cols[0].image(generate_default_avatar(70, 'primary'), width=70)
            
            # Item Info
            status, icon, label = get_stock_status(item["qty"])
            cols[1].markdown(f"""
            <p style='font-weight: 600; color: {COLORS['neutral_900']}; margin: 0; font-size: 16px;'>{item['name']}</p>
            <p class='caption'>ID: {item['id'][:8]}... | Updated: {item.get('updated_at', item['created_at']).strftime('%Y-%m-%d')}</p>
            """, unsafe_allow_html=True)
            
            # Status Badge
            cols[2].markdown(f"""
            <span class='badge badge-{status}'>{icon} {item['qty']} units</span>
            """, unsafe_allow_html=True)
            
            # Actions
            action_col1, action_col2 = cols[3].columns(2)
            
            # Edit Button
            if action_col1.button("✏️", key=f"edit-{item['id']}", help="Edit item"):
                st.session_state["edit_mode"][item['id']] = True
                st.rerun()
            
            # Delete Button
            if action_col2.button("🗑️", key=f"del-{item['id']}", help="Delete item"):
                delete_item(item["id"])
                st.success(f"✅ '{item['name']}' deleted!")
                st.rerun()
            
            # Edit Mode Expander
            if st.session_state.get("edit_mode", {}).get(item['id'], False):
                with st.expander(f"✏️ Edit '{item['name']}'", expanded=True):
                    with st.form(f"edit_form_{item['id']}"):
                        edit_name = st.text_input("Name", value=item["name"])
                        edit_qty = st.number_input("Quantity", min_value=0, value=item["qty"], step=1)
                        edit_img = st.file_uploader("Change Photo", type=["png", "jpg", "jpeg"], key=f"img-{item['id']}")
                        
                        col_save, col_cancel = st.columns(2)
                        
                        if col_save.form_submit_button("💾 Save", use_container_width=True):
                            img_bytes = edit_img.read() if edit_img else None
                            update_item(item['id'], edit_name, edit_qty, img_bytes)
                            st.session_state["edit_mode"][item['id']] = False
                            st.success("✅ Changes saved!")
                            st.rerun()
                        
                        if col_cancel.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state["edit_mode"][item['id']] = False
                            st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("🔍 No items found. Try adjusting your search or add new items.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Export/Import Section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>📤 Export / Import</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export to CSV", use_container_width=True):
            if st.session_state["items"]:
                df = pd.DataFrame([
                    {
                        "id": it["id"],
                        "name": it["name"],
                        "quantity": it["qty"],
                        "created_at": it["created_at"].strftime('%Y-%m-%d %H:%M:%S'),
                        "updated_at": it.get("updated_at", it["created_at"]).strftime('%Y-%m-%d %H:%M:%S')
                    } for it in st.session_state["items"]
                ])
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "⬇️ Download CSV",
                    data=csv,
                    file_name=f"stockify_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ No items to export")
    
    with col2:
        uploaded_csv = st.file_uploader("📤 Import from CSV", type=["csv"])
        if uploaded_csv is not None:
            try:
                df = pd.read_csv(uploaded_csv)
                if 'name' not in df.columns or 'quantity' not in df.columns:
                    st.error("⚠️ CSV must have 'name' and 'quantity' columns")
                else:
                    added = 0
                    for _, row in df.iterrows():
                        if pd.notna(row.get("name")):
                            name = str(row["name"]).strip()
                            qty = int(row.get("quantity", 0)) if pd.notna(row.get("quantity")) else 0
                            add_item(name, qty)
                            added += 1
                    st.success(f"✅ {added} items imported successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"⚠️ Import failed: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# PAGE: Reports
# -----------------------
elif page == "📊 Reports":
    st.markdown("<h1>📊 Reports & Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<p class='text-secondary'>Visual insights of your inventory</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    items = st.session_state["items"]
    
    if not items:
        st.info("📊 No data available. Add some items first!")
    else:
        # Summary Stats
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>📈 Summary Statistics</h3>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_items = len(items)
        total_qty = sum(it["qty"] for it in items)
        avg_qty = total_qty / total_items if total_items > 0 else 0
        threshold = st.session_state.get("low_stock_threshold", 5)
        low_stock_count = len([it for it in items if 0 < it["qty"] <= threshold])
        
        col1.metric("Total Items", total_items)
        col2.metric("Total Quantity", total_qty)
        col3.metric("Average Qty/Item", f"{avg_qty:.1f}")
        col4.metric("Low Stock Items", low_stock_count)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>📊 Quantity by Item</h3>", unsafe_allow_html=True)
        
        df = pd.DataFrame([{"name": it["name"], "quantity": it["qty"]} for it in items])
        df_sorted = df.sort_values("quantity", ascending=False).head(15)
        
        st.bar_chart(df_sorted.set_index("name")["quantity"])
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Stock Status Distribution
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>📊 Stock Status Distribution</h3>", unsafe_allow_html=True)
        
        status_data = {"In Stock": 0, "Low Stock": 0, "Out of Stock": 0}
        for it in items:
            status, _, _ = get_stock_status(it["qty"])
            if status == "success":
                status_data["In Stock"] += 1
            elif status == "warning":
                status_data["Low Stock"] += 1
            else:
                status_data["Out of Stock"] += 1
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 In Stock", status_data["In Stock"])
        col2.metric("🟡 Low Stock", status_data["Low Stock"])
        col3.metric("🔴 Out of Stock", status_data["Out of Stock"])
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Detailed Table
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>📋 Detailed Inventory Table</h3>", unsafe_allow_html=True)
        
        table_df = pd.DataFrame([
            {
                "Item Name": it["name"],
                "Quantity": it["qty"],
                "Status": get_stock_status(it["qty"])[2],
                "Last Updated": it.get("updated_at", it["created_at"]).strftime('%Y-%m-%d %H:%M')
            } for it in items
        ])
        
        st.dataframe(table_df, use_container_width=True, hide_index=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# PAGE: Settings
# -----------------------
elif page == "⚙️ Settings":
    st.markdown("<h1>⚙️ Settings</h1>", unsafe_allow_html=True)
    st.markdown("<p class='text-secondary'>Configure your Stockify preferences</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Profile Settings
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>👤 Profile Settings</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        try:
            current_img = Image.open(io.BytesIO(st.session_state["profile_img"]))
            st.image(current_img, width=150)
        except:
            st.image(generate_default_avatar(150, 'primary'), width=150)
        
        uploaded_profile = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"], key="profile_upload")
        
        if uploaded_profile is not None:
            try:
                st.session_state["profile_img"] = uploaded_profile.read()
                st.success("✅ Profile photo updated!")
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ Failed to update photo: {str(e)}")
    
    with col2:
        st.markdown("<p class='text-secondary'>Update your profile picture to personalize your dashboard.</p>", unsafe_allow_html=True)
        
        color_options = {
            "🔵 Blue (Default)": "primary",
            "🟢 Green": "success",
            "🟣 Purple": "accent",
            "🟡 Amber": "warning"
        }
        
        selected_color = st.selectbox("Avatar Color Theme", list(color_options.keys()))
        
        if st.button("🎨 Generate New Avatar"):
            color = color_options[selected_color]
            st.session_state["profile_img"] = pil_image_to_bytes(generate_default_avatar(256, color))
            st.success(f"✅ New avatar generated!")
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Inventory Settings
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>📦 Inventory Settings</h3>", unsafe_allow_html=True)
    
    threshold = st.number_input(
        "🔔 Low Stock Alert Threshold",
        min_value=1,
        max_value=50,
        value=st.session_state.get("low_stock_threshold", 5),
        help="Items with quantity at or below this number will be flagged as low stock"
    )
    
    if st.button("💾 Save Threshold"):
        st.session_state["low_stock_threshold"] = threshold
        st.success(f"✅ Low stock threshold set to {threshold}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data Management
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>🗄️ Data Management</h3>", unsafe_allow_html=True)
    
    st.warning("⚠️ Warning: These actions cannot be undone!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Items", use_container_width=True):
            if st.session_state["items"]:
                item_count = len(st.session_state["items"])
                st.session_state["items"] = []
                st.success(f"✅ {item_count} items cleared!")
                st.rerun()
            else:
                st.info("ℹ️ No items to clear")
    
    with col2:
        if st.button("🔄 Reset All Settings", use_container_width=True):
            st.session_state["low_stock_threshold"] = 5
            st.session_state["profile_img"] = pil_image_to_bytes(generate_default_avatar(256, 'primary'))
            st.success("✅ Settings reset to default!")
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # About
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>ℹ️ About Stockify</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <p class='body-text'>
    <strong>Version:</strong> 1.0.0<br>
    <strong>Built with:</strong> Streamlit & Python<br>
    <strong>Color Palette:</strong> Professional Blue Theme<br>
    <strong>Font:</strong> Poppins
    </p>
    <p class='text-secondary'>
    Stockify is a smart inventory management system designed for simplicity and efficiency.
    </p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.markdown("""
<div class='footer'>
    Built with ❤️ using Streamlit | Stockify v1.0 | © 2024
</div>
""", unsafe_allow_html=True)
