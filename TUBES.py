# TUBES_Enhanced.py - Streamlit Enhanced with Colors & Icons
# Jalankan: streamlit run TUBES_Enhanced.py

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import pandas as pd
import numpy as np
import base64
import uuid
from datetime import datetime

# -----------------------
# SKEMA WARNA MODERN
# -----------------------
COLORS = {
    # Primary Colors
    'primary': '#6366F1',        # Indigo - warna utama
    'primary_dark': '#4F46E5',   # Indigo gelap
    'primary_light': '#818CF8',  # Indigo terang
    
    # Secondary Colors
    'secondary': '#10B981',      # Emerald - untuk success
    'warning': '#F59E0B',        # Amber - untuk warning
    'danger': '#EF4444',         # Red - untuk danger
    'info': '#3B82F6',          # Blue - untuk info
    
    # Accent Colors
    'accent_purple': '#A855F7',  # Purple
    'accent_pink': '#EC4899',    # Pink
    'accent_cyan': '#06B6D4',    # Cyan
    'accent_orange': '#F97316',  # Orange
    
    # Neutral Colors
    'bg_primary': '#0F172A',     # Slate 900 - dark bg
    'bg_secondary': '#1E293B',   # Slate 800
    'bg_card': '#FFFFFF',        # White card
    'bg_light': '#F8FAFC',       # Slate 50
    'text_primary': '#0F172A',   # Slate 900
    'text_secondary': '#64748B', # Slate 500
    'border': '#E2E8F0',         # Slate 200
    
    # Gradient Colors
    'gradient_start': '#6366F1',
    'gradient_end': '#EC4899',
}

# -----------------------
# Helper: Default avatar dengan gradient
# -----------------------
def generate_default_avatar(size=256, color_scheme='blue'):
    img = Image.new("RGB", (size, size), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Background gradient effect (simplified)
    if color_scheme == 'blue':
        bg_color = (99, 102, 241)  # Indigo
    elif color_scheme == 'green':
        bg_color = (16, 185, 129)  # Emerald
    elif color_scheme == 'purple':
        bg_color = (168, 85, 247)  # Purple
    else:
        bg_color = (59, 130, 246)  # Blue
    
    # Circle background
    draw.ellipse((0, 0, size, size), fill=bg_color)
    
    # Head
    cx, cy = size//2, size//2 - 16
    r = size//4
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(255, 255, 255), outline=(240, 240, 240))
    
    # Body
    bx1, by1 = cx - r - 12, cy + r - 6
    bx2, by2 = cx + r + 12, cy + r + 80
    draw.rectangle((bx1, by1, bx2, by2), fill=(255, 255, 255))
    
    # Eyes
    draw.ellipse((cx-30, cy-10, cx-20, cy), fill=bg_color)
    draw.ellipse((cx+20, cy-10, cx+30, cy), fill=bg_color)
    
    # Smile
    draw.arc((cx-20, cy+5, cx+20, cy+30), start=0, end=180, fill=bg_color, width=3)
    
    return img

def pil_image_to_bytes(img, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()

# -----------------------
# Session state initialization
# -----------------------
def init_state():
    if "items" not in st.session_state:
        st.session_state["items"] = []
    if "profile_img" not in st.session_state:
        st.session_state["profile_img"] = pil_image_to_bytes(generate_default_avatar(256, 'blue'))
    if "form_item_name" not in st.session_state:
        st.session_state["form_item_name"] = ""
    if "form_item_qty" not in st.session_state:
        st.session_state["form_item_qty"] = 1
    if "form_item_image" not in st.session_state:
        st.session_state["form_item_image"] = None
    if "filter_text" not in st.session_state:
        st.session_state["filter_text"] = ""
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "light"

init_state()

# -----------------------
# CSS: Enhanced Colorful Styles with Icons
# -----------------------
def inject_css():
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    :root {{
        --primary: {COLORS['primary']};
        --primary-dark: {COLORS['primary_dark']};
        --secondary: {COLORS['secondary']};
        --warning: {COLORS['warning']};
        --danger: {COLORS['danger']};
        --info: {COLORS['info']};
        --accent-purple: {COLORS['accent_purple']};
        --accent-pink: {COLORS['accent_pink']};
        --bg-light: {COLORS['bg_light']};
        --bg-card: {COLORS['bg_card']};
        --text-primary: {COLORS['text_primary']};
        --text-secondary: {COLORS['text_secondary']};
        --border: {COLORS['border']};
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }}
    
    .main {{
        background: var(--bg-light);
        border-radius: 24px;
        margin: 20px;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%);
        padding: 24px 16px;
    }}
    
    [data-testid="stSidebar"] .stRadio > label {{
        color: white !important;
        font-weight: 600;
        font-size: 14px;
    }}
    
    [data-testid="stSidebar"] [role="radiogroup"] {{
        gap: 8px;
    }}
    
    [data-testid="stSidebar"] [role="radiogroup"] label {{
        background: rgba(255,255,255,0.1);
        padding: 12px 16px;
        border-radius: 12px;
        color: white !important;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
    }}
    
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
        background: rgba(255,255,255,0.2);
        transform: translateX(4px);
    }}
    
    [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {{
        background: white;
        color: var(--primary) !important;
        border-color: white;
        font-weight: 700;
    }}
    
    /* Brand Styling */
    .brand {{
        font-weight: 800;
        font-size: 28px;
        background: linear-gradient(135deg, #fff 0%, #f0f0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }}
    
    .brand-subtitle {{
        color: rgba(255,255,255,0.8);
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 24px;
    }}
    
    /* Card Styling */
    .card {{
        background: var(--bg-card);
        border-radius: 16px;
        border: 1px solid var(--border);
        padding: 24px;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.08);
        transition: all 0.3s ease;
        margin-bottom: 16px;
    }}
    
    .card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
    }}
    
    .card-gradient {{
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent-purple) 100%);
        color: white;
        border: none;
    }}
    
    .card-success {{
        background: linear-gradient(135deg, var(--secondary) 0%, #059669 100%);
        color: white;
        border: none;
    }}
    
    .card-warning {{
        background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%);
        color: white;
        border: none;
    }}
    
    .card-danger {{
        background: linear-gradient(135deg, var(--danger) 0%, #dc2626 100%);
        color: white;
        border: none;
    }}
    
    /* Metric Cards */
    .metric-card {{
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border-left: 4px solid var(--primary);
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }}
    
    .metric-icon {{
        font-size: 32px;
        margin-bottom: 12px;
        display: inline-block;
    }}
    
    .metric-value {{
        font-size: 32px;
        font-weight: 800;
        color: var(--text-primary);
        margin: 8px 0;
    }}
    
    .metric-label {{
        font-size: 14px;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Button Styling */
    .stButton > button {{
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
    }}
    
    /* Badge Styling */
    .badge {{
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .badge-primary {{
        background: var(--primary);
        color: white;
    }}
    
    .badge-success {{
        background: var(--secondary);
        color: white;
    }}
    
    .badge-warning {{
        background: var(--warning);
        color: white;
    }}
    
    .badge-danger {{
        background: var(--danger);
        color: white;
    }}
    
    .badge-info {{
        background: var(--info);
        color: white;
    }}
    
    /* Item Card Styling */
    .item-card {{
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 2px solid var(--border);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    
    .item-card:hover {{
        border-color: var(--primary);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
        transform: translateX(4px);
    }}
    
    .item-thumbnail {{
        width: 80px;
        height: 80px;
        object-fit: cover;
        border-radius: 12px;
        border: 3px solid var(--border);
    }}
    
    /* Title Styling */
    .page-title {{
        font-size: 36px;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 8px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent-purple) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .section-title {{
        font-size: 20px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 24px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    /* Icon Styling */
    .icon {{
        display: inline-block;
        margin-right: 8px;
    }}
    
    /* Input Styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {{
        border-radius: 10px;
        border: 2px solid var(--border);
        padding: 12px 16px;
        transition: all 0.3s ease;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }}
    
    /* Expander Styling */
    .streamlit-expanderHeader {{
        background: var(--bg-light);
        border-radius: 10px;
        font-weight: 600;
        color: var(--primary);
    }}
    
    /* Profile Image Styling */
    .profile-container {{
        text-align: center;
        padding: 20px;
    }}
    
    .profile-img {{
        border-radius: 50%;
        border: 4px solid white;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 20px;
        color: var(--text-secondary);
        font-size: 14px;
        margin-top: 40px;
    }}
    
    /* Responsive */
    @media (max-width: 600px) {{
        .item-thumbnail {{
            width: 60px;
            height: 60px;
        }}
        .page-title {{
            font-size: 28px;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_css()

# -----------------------
# Utility functions
# -----------------------
def add_item(name: str, qty: int, image_bytes: bytes):
    item = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "qty": int(qty),
        "image": image_bytes,
        "created_at": datetime.utcnow()
    }
    st.session_state["items"].append(item)
    return item

def delete_item(item_id: str):
    st.session_state["items"] = [it for it in st.session_state["items"] if it["id"] != item_id]

def get_items_filtered(filter_text: str = ""):
    if not filter_text:
        return st.session_state["items"]
    ft = filter_text.lower()
    return [it for it in st.session_state["items"] if ft in it["name"].lower()]

# -----------------------
# Layout: Sidebar navigation
# -----------------------
st.set_page_config(
    page_title="Stockify Pro",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.markdown("<div class='profile-container'>", unsafe_allow_html=True)
    st.image(Image.open(io.BytesIO(st.session_state["profile_img"])), width=120)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='brand'>📦 Stockify Pro</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-subtitle'>Smart Inventory Management</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "➕ Scan & Add", "📋 Items", "📊 Reports", "⚙️ Settings"],
        label_visibility="collapsed"
    )

# -----------------------
# Page: Dashboard
# -----------------------
if page == "🏠 Dashboard":
    st.markdown("<div class='page-title'>🏠 Dashboard</div>", unsafe_allow_html=True)
    st.markdown("Welcome back! Here's your inventory overview.")
    
    items = st.session_state["items"]
    total_skus = len(items)
    total_qty = sum(it["qty"] for it in items)
    low_stock = [it for it in items if it["qty"] <= 2]

    # Metrics with colorful cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card' style='border-left-color: {COLORS['primary']}'>
            <div class='metric-icon'>📦</div>
            <div class='metric-value'>{total_skus}</div>
            <div class='metric-label'>Total SKUs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card' style='border-left-color: {COLORS['secondary']}'>
            <div class='metric-icon'>📈</div>
            <div class='metric-value'>{total_qty}</div>
            <div class='metric-label'>Total Quantity</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        badge_color = COLORS['danger'] if len(low_stock) > 0 else COLORS['secondary']
        st.markdown(f"""
        <div class='metric-card' style='border-left-color: {badge_color}'>
            <div class='metric-icon'>⚠️</div>
            <div class='metric-value'>{len(low_stock)}</div>
            <div class='metric-label'>Low Stock Alert</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Low stock items
    if low_stock:
        st.markdown("<div class='section-title'>⚠️ Low Stock Items</div>", unsafe_allow_html=True)
        st.markdown("<div class='card card-danger'>", unsafe_allow_html=True)
        
        for it in low_stock:
            cols = st.columns([0.15, 0.6, 0.25])
            if it["image"]:
                img = Image.open(io.BytesIO(it["image"]))
                cols[0].image(img, width=70)
            else:
                cols[0].image(generate_default_avatar(70, 'purple'), width=70)
            
            cols[1].markdown(f"""
            **{it['name']}**  
            <span class='badge badge-danger'>⚠️ Qty: {it['qty']}</span>
            """, unsafe_allow_html=True)
            
            if cols[2].button("🔔 Reorder", key=f"reorder-{it['id']}"):
                st.success(f"✅ Reorder request sent for {it['name']}")
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Recent items
    st.markdown("<div class='section-title'>🕐 Recent Activity</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    recent_items = sorted(items, key=lambda x: x["created_at"], reverse=True)[:5]
    
    if recent_items:
        for it in recent_items:
            cols = st.columns([0.15, 0.6, 0.25])
            if it["image"]:
                cols[0].image(Image.open(io.BytesIO(it["image"])), width=70)
            else:
                cols[0].image(generate_default_avatar(70, 'blue'), width=70)
            
            cols[1].markdown(f"""
            **{it['name']}**  
            <small style='color: {COLORS['text_secondary']}'>
            Added: {it['created_at'].strftime('%Y-%m-%d %H:%M')}
            </small>
            """, unsafe_allow_html=True)
            
            qty_badge = 'success' if it['qty'] > 10 else 'warning' if it['qty'] > 2 else 'danger'
            cols[2].markdown(f"""
            <span class='badge badge-{qty_badge}'>📊 Qty: {it['qty']}</span>
            """, unsafe_allow_html=True)
    else:
        st.info("🔍 No items yet. Start adding items from the 'Scan & Add' page!")
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# Page: Scan & Add
# -----------------------
elif page == "➕ Scan & Add":
    st.markdown("<div class='page-title'>➕ Add New Item</div>", unsafe_allow_html=True)
    st.markdown("Quickly add new items to your inventory")

    st.markdown("<div class='card card-gradient'>", unsafe_allow_html=True)
    
    with st.form("add_item_form", clear_on_submit=False):
        st.markdown("### 📝 Item Details")
        c1, c2 = st.columns([3, 1])
        name = c1.text_input("🏷️ Item Name", value=st.session_state["form_item_name"], 
                            key="form_name_input", placeholder="Enter item name...")
        qty = c2.number_input("📊 Quantity", min_value=0, value=st.session_state["form_item_qty"], 
                             step=1, key="form_qty_input")
        
        image_file = st.file_uploader("📷 Upload Photo (optional)", 
                                     type=["png", "jpg", "jpeg"], 
                                     key="form_image_uploader")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        submitted = col2.form_submit_button("✅ Add Item", use_container_width=True)

        if submitted:
            image_bytes = None
            if image_file is not None:
                image_bytes = image_file.read()
            else:
                image_bytes = pil_image_to_bytes(generate_default_avatar(256, 'green'))

            if not name or name.strip() == "":
                st.warning("⚠️ Item name cannot be empty!")
            else:
                add_item(name, qty, image_bytes)
                st.success(f"✅ Item '{name}' (qty: {qty}) added successfully!")
                st.session_state["form_name_input"] = ""
                st.session_state["form_qty_input"] = 1
                st.session_state["form_item_name"] = ""
                st.session_state["form_item_qty"] = 1

    st.markdown("</div>", unsafe_allow_html=True)

    # Quick Scan Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='card card-success'>", unsafe_allow_html=True)
    st.markdown("### 🔍 Quick Scan")
    
    with st.form("quick_scan_form"):
        col1, col2 = st.columns([3, 1])
        scan_input = col1.text_input("📱 Scan Barcode/QR", value="", 
                                    key="scan_input_field",
                                    placeholder="Scan or type item code...")
        scan_qty = col2.number_input("Qty", min_value=1, value=1, step=1, key="scan_qty_field")
        
        if st.form_submit_button("🚀 Quick Add", use_container_width=True):
            if not scan_input.strip():
                st.warning("⚠️ Scan input is empty")
            else:
                add_item(scan_input.strip(), scan_qty, 
                        pil_image_to_bytes(generate_default_avatar(256, 'purple')))
                st.success(f"✅ '{scan_input.strip()}' added (qty: {scan_qty})")
                st.session_state["scan_input_field"] = ""
                st.session_state["scan_qty_field"] = 1
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# Page: Items
# -----------------------
elif page == "📋 Items":
    st.markdown("<div class='page-title'>📋 All Items</div>", unsafe_allow_html=True)
    
    # Filter and actions
    col1, col2, col3 = st.columns([2, 1, 1])
    filter_text = col1.text_input("🔍 Search items...", 
                                  value=st.session_state["filter_text"],
                                  key="items_filter",
                                  placeholder="Type to filter...")
    st.session_state["filter_text"] = filter_text

    items_listed = get_items_filtered(filter_text)

    # Stats
    st.markdown(f"""
    <div class='card' style='background: linear-gradient(135deg, {COLORS['info']} 0%, {COLORS['accent_cyan']} 100%); color: white;'>
        <h3 style='margin:0'>📊 {len(items_listed)} items found</h3>
    </div>
    """, unsafe_allow_html=True)

    # Items list
    for idx, it in enumerate(items_listed):
        st.markdown("<div class='item-card'>", unsafe_allow_html=True)
        
        cols = st.columns([0.15, 0.5, 0.35])
        
        # Image
        if it["image"]:
            cols[0].image(Image.open(io.BytesIO(it["image"])), width=80)
        else:
            cols[0].image(generate_default_avatar(80, 'blue'), width=80)
        
        # Info
        qty_status = '🟢' if it['qty'] > 10 else '🟡' if it['qty'] > 2 else '🔴'
        cols[1].markdown(f"""
        **{it['name']}**  
        {qty_status} Quantity: **{it['qty']}**  
        <small style='color: {COLORS['text_secondary']}'>ID: {it['id'][:8]}...</small>
        """, unsafe_allow_html=True)
        
        # Actions
        c1, c2 = cols[2].columns([1, 1])
        if c1.button("🗑️ Delete", key=f"del-{it['id']}", use_container_width=True):
            delete_item(it["id"])
            st.success(f"✅ '{it['name']}' deleted!")
            st.rerun()
        
        if c2.button("✏️ Edit", key=f"edit-{it['id']}", use_container_width=True):
            with st.expander(f"✏️ Edit {it['name']}", expanded=True):
                new_name = st.text_input("Name", value=it["name"], key=f"name-edit-{it['id']}")
                new_qty = st.number_input("Quantity", min_value=0, value=it["qty"], 
                                        key=f"qty-edit-{it['id']}")
                new_img = st.file_uploader("Photo", type=["png", "jpg", "jpeg"], 
                                          key=f"img-edit-{it['id']}")
                
                if st.button("💾 Save Changes", key=f"save-edit-{it['id']}"):
                    for j, ii in enumerate(st.session_state["items"]):
                        if ii["id"] == it["id"]:
                            st.session_state["items"][j]["name"] = new_name.strip() or ii["name"]
                            st.session_state["items"][j]["qty"] = int(new_qty)
                            if new_img:
                                st.session_state["items"][j]["image"] = new_img.read()
                            st.success("✅ Changes saved!")
                            st.rerun()
                            break
        
        st.markdown("</div>", unsafe_allow_html=True)
