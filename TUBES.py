i# TUBES.py - Integrated with model.py
# Jalankan: streamlit run TUBES.py
# PASTIKAN model.py ada di folder yang sama!

import streamlit as st
from PIL import Image, ImageDraw
import io
import base64
from datetime import datetime

# Import OOP model - HARUS ADA model.py di folder yang sama
try:
    from model import (
        get_inventory, 
        Item, 
        InventoryError, 
        ItemNotFoundError,
        InvalidQuantityError,
        DuplicateItemError,
        ValidationError
    )
    MODEL_IMPORTED = True
except ImportError as e:
    st.error(f"❌ ERROR: model.py tidak ditemukan! Error: {e}")
    st.info("Pastikan file model.py ada di folder yang sama dengan TUBES.py")
    MODEL_IMPORTED = False

# -----------------------
# Helper Functions
# -----------------------
def generate_default_avatar(size=256):
    """Generate default avatar image"""
    img = Image.new("RGB", (size, size), (245, 247, 251))
    draw = ImageDraw.Draw(img)
    cx, cy = size//2, size//2 - 16
    r = size//4
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(230,230,230), outline=(200,200,200))
    bx1, by1 = cx - r - 12, cy + r - 6
    bx2, by2 = cx + r + 12, cy + r + 80
    draw.rectangle((bx1, by1, bx2, by2), fill=(230,230,230))
    draw.ellipse((cx-30, cy-10, cx-20, cy), fill=(180,180,180))
    draw.ellipse((cx+20, cy-10, cx+30, cy), fill=(180,180,180))
    draw.arc((cx-20, cy+5, cx+20, cy+30), start=0, end=180, fill=(160,160,160), width=3)
    return img

def pil_image_to_base64(img, fmt="PNG"):
    """Convert PIL image to base64 string"""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def base64_to_pil(b64_string):
    """Convert base64 string to PIL image"""
    img_bytes = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(img_bytes))

# -----------------------
# Session State Init
# -----------------------
def init_state():
    if MODEL_IMPORTED and "inventory" not in st.session_state:
        st.session_state["inventory"] = get_inventory("data")
    
    if "profile_img" not in st.session_state:
        default_img = generate_default_avatar(256)
        st.session_state["profile_img"] = pil_image_to_base64(default_img)

# -----------------------
# CSS Styling
# -----------------------
def inject_css():
    css = """
    <style>
    .brand { font-weight:700; font-size:20px; color:#0B66FF; }
    .card { background:#FFFFFF; border-radius:12px; padding:16px; box-shadow:0 4px 12px rgba(0,0,0,0.1); margin:10px 0; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -----------------------
# Main App
# -----------------------
st.set_page_config(page_title="Stockify Pro - OOP", layout="wide")

inject_css()
init_state()

# Jika model tidak berhasil diimport, stop di sini
if not MODEL_IMPORTED:
    st.stop()

inv = st.session_state["inventory"]

# -----------------------
# Sidebar
# -----------------------
with st.sidebar:
    profile_img = base64_to_pil(st.session_state["profile_img"])
    st.image(profile_img, width=84, caption="Profile")
    
    st.markdown("<div class='brand'>Stockify Pro</div>", unsafe_allow_html=True)
    st.write("OOP-Based Inventory System")
    st.write("---")
    page = st.radio("Menu", ["Dashboard", "Add Item", "Items List", "Reports"])

# -----------------------
# PAGE: DASHBOARD
# -----------------------
if page == "Dashboard":
    st.title("📊 Dashboard")
    
    stats = inv.get_statistics()
    low_stock_items = inv.get_low_stock_items(threshold=5)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total SKUs", stats['total_items'])
    col2.metric("Total Quantity", stats['total_quantity'])
    col3.metric("Low Stock", stats['low_stock_count'])

    st.write("---")
    st.markdown("#### ⚠️ Low Stock Items")
    
    if not low_stock_items:
        st.success("✅ All items are well stocked!")
    else:
        for item in low_stock_items:
            cols = st.columns([0.15, 0.6, 0.25])
            
            # Display image
            if item.image_data:
                cols[0].image(base64_to_pil(item.image_data), width=64)
            else:
                cols[0].image(generate_default_avatar(64), width=64)
            
            cols[1].markdown(f"**{item.name}**")
            cols[1].caption(f"Qty: {item.qty} | Category: {item.category or 'N/A'}")
            
            if cols[2].button("🔄 Restock +10", key=f"restock-{item.id}"):
                try:
                    inv.restock_item(item.id, 10)
                    st.success(f"Restocked {item.name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.write("---")
    st.markdown("#### 📦 Recent Items")
    recent = inv.list_items(sort_by="created_at")[-5:]
    
    for item in reversed(recent):
        cols = st.columns([0.15, 0.85])
        
        if item.image_data:
            cols[0].image(base64_to_pil(item.image_data), width=64)
        else:
            cols[0].image(generate_default_avatar(64), width=64)
        
        cols[1].markdown(f"**{item.name}** | Qty: {item.qty}")
        cols[1].caption(f"Added: {item.created_at.strftime('%Y-%m-%d %H:%M')}")

# -----------------------
# PAGE: ADD ITEM
# -----------------------
elif page == "Add Item":
    st.title("➕ Add New Item")
    
    with st.form("add_item_form", clear_on_submit=True):
        name = st.text_input("Item Name *")
        
        col1, col2 = st.columns(2)
        qty = col1.number_input("Quantity *", min_value=0, value=1, step=1)
        category = col2.text_input("Category")
        
        location = st.text_input("Location")
        notes = st.text_area("Notes")
        image_file = st.file_uploader("Image (optional)", type=["png","jpg","jpeg"])
        
        submitted = st.form_submit_button("➕ Add Item")

        if submitted:
            try:
                # Process image
                image_data = None
                if image_file is not None:
                    img_bytes = image_file.read()
                    image_data = base64.b64encode(img_bytes).decode('utf-8')
                else:
                    # Default avatar
                    default_img = generate_default_avatar(256)
                    image_data = pil_image_to_base64(default_img)

                # Create item
                item = inv.create_item(
                    name=name,
                    qty=qty,
                    image_data=image_data,
                    category=category or None,
                    location=location or None,
                    notes=notes or None
                )
                
                st.success(f"✅ Item '{item.name}' added successfully!")
                st.rerun()
                
            except ValidationError as e:
                st.error(f"❌ Validation Error: {e}")
            except DuplicateItemError as e:
                st.error(f"❌ Duplicate: {e}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# -----------------------
# PAGE: ITEMS LIST
# -----------------------
elif page == "Items List":
    st.title("📋 Items List")
    
    # Search bar
    search_query = st.text_input("🔍 Search items...")
    
    # Get items
    if search_query:
        items_list = inv.search_items(search_query)
    else:
        items_list = inv.list_items(sort_by="name")
    
    st.markdown(f"**{len(items_list)} items found**")
    st.write("---")
    
    # Display items
    if not items_list:
        st.info("No items found. Add some items first!")
    else:
        for item in items_list:
            cols = st.columns([0.1, 0.6, 0.3])
            
            # Image
            if item.image_data:
                cols[0].image(base64_to_pil(item.image_data), width=64)
            else:
                cols[0].image(generate_default_avatar(64), width=64)
            
            # Info
            cols[1].markdown(f"**{item.name}**")
            cols[1].caption(f"Qty: {item.qty} | Category: {item.category or 'N/A'}")
            if item.notes:
                cols[1].caption(f"📝 {item.notes[:50]}...")
            
            # Actions
            action_cols = cols[2].columns(2)
            
            # Edit
            if action_cols[0].button("✏️ Edit", key=f"edit-{item.id}"):
                st.session_state[f"editing_{item.id}"] = True
            
            # Delete
            if action_cols[1].button("🗑️ Delete", key=f"del-{item.id}"):
                try:
                    inv.delete_item(item.id)
                    st.success(f"Deleted '{item.name}'")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            
            # Edit form
            if st.session_state.get(f"editing_{item.id}", False):
                with st.expander(f"✏️ Edit {item.name}", expanded=True):
                    with st.form(f"edit_form_{item.id}"):
                        new_name = st.text_input("Name", value=item.name)
                        new_qty = st.number_input("Quantity", min_value=0, value=item.qty)
                        new_category = st.text_input("Category", value=item.category or "")
                        new_location = st.text_input("Location", value=item.location or "")
                        new_notes = st.text_area("Notes", value=item.notes or "")
                        
                        col1, col2 = st.columns(2)
                        save = col1.form_submit_button("💾 Save")
                        cancel = col2.form_submit_button("❌ Cancel")
                        
                        if save:
                            try:
                                inv.update_item(
                                    item.id,
                                    name=new_name,
                                    qty=new_qty,
                                    category=new_category or None,
                                    location=new_location or None,
                                    notes=new_notes or None
                                )
                                st.success("Updated!")
                                st.session_state[f"editing_{item.id}"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        
                        if cancel:
                            st.session_state[f"editing_{item.id}"] = False
                            st.rerun()
            
            st.divider()
    
    # Export/Import
    st.write("---")
    st.markdown("### 🔧 Bulk Operations")
    
    col1, col2 = st.columns(2)
    
    # Export
    if col1.button("📥 Export to CSV"):
        try:
            csv_path = "export_items.csv"
            inv.export_to_csv(csv_path)
            
            with open(csv_path, 'rb') as f:
                st.download_button(
                    "⬇️ Download CSV",
                    data=f,
                    file_name=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            st.success("CSV ready for download!")
        except Exception as e:
            st.error(f"Export failed: {e}")
    
    # Import
    uploaded_csv = col2.file_uploader("📤 Import CSV", type=["csv"])
    if uploaded_csv:
        try:
            temp_path = "temp_import.csv"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_csv.read())
            
            imported = inv.import_from_csv(temp_path, skip_duplicates=True)
            st.success(f"✅ Imported {imported} items")
            st.rerun()
        except Exception as e:
            st.error(f"Import failed: {e}")

# -----------------------
# PAGE: REPORTS
# -----------------------
elif page == "Reports":
    st.title("📊 Reports")
    
    stats = inv.get_statistics()
    
    # Overall stats
    st.markdown("### 📈 Overall Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items", stats['total_items'])
    col2.metric("Total Quantity", stats['total_quantity'])
    col3.metric("Categories", stats['total_categories'])
    col4.metric("Low Stock", stats['low_stock_count'])
    
    # Category distribution
    st.write("---")
    st.markdown("### 📦 Category Distribution")
    if stats['categories']:
        import pandas as pd
        cat_df = pd.DataFrame(list(stats['categories'].items()), columns=['Category', 'Count'])
        st.bar_chart(cat_df.set_index('Category'))
    else:
        st.info("No category data available")
    
    # Recent activity
    st.write("---")
    st.markdown("### 🕒 Recent Activity")
    recent_logs = inv.get_recent_logs(limit=10)
    if recent_logs:
        for log in reversed(recent_logs):
            st.caption(
                f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"**{log.operation.value}** | "
                f"Item: {log.item_id[:8]}..."
            )
    else:
        st.info("No activity logs yet")

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.caption(f"Stockify Pro - OOP Edition | Total Items: {len(inv.items)}")
