import streamlit as st
from PIL import Image, ImageDraw
import io
import pandas as pd
import base64
from datetime import datetime

from model import (
    get_inventory, 
    Item, 
    InventoryError, 
    ItemNotFoundError,
    InvalidQuantityError,
    DuplicateItemError,
    ValidationError
)

def generate_default_avatar(size=256):
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

def bytes_to_pil(image_bytes):
    """Convert bytes to PIL image"""
    return Image.open(io.BytesIO(image_bytes))

def init_state():
    if "inventory" not in st.session_state:
        st.session_state["inventory"] = get_inventory("data")
    
    if "profile_img" not in st.session_state:
        default_img = generate_default_avatar(256)
        st.session_state["profile_img"] = pil_image_to_base64(default_img)

init_state()
inv = st.session_state["inventory"]

def inject_css():
    css = """
    <style>
    :root{
      --bg: #F5F7FB;
      --card-bg: #FFFFFF;
      --text-primary: #1F2937;
      --text-muted: #8A97B2;
      --primary: #0B66FF;
      --primary-600: #0856D6;
      --secondary: #0BB39A;
      --warning: #FFB020;
      --danger: #FF4D4F;
      --shadow: rgba(11,102,255,0.06);
    }
    .brand { font-weight:700; font-size:20px; color:var(--primary); }
    .card { background:var(--card-bg); border-radius:12px; border:1px solid #E8EEF8; padding:16px; box-shadow:0 6px 18px var(--shadow); }
    .thumbnail { width:84px; height:84px; object-fit:cover; border-radius:8px; border:1px solid #E8EEF8; }
    .badge-warning { background:var(--warning); color:white; padding:4px 8px; border-radius:8px; font-weight:600; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_css()

st.set_page_config(page_title="Stockify Pro - OOP", layout="wide")
with st.sidebar:
    profile_img_data = base64.b64decode(st.session_state["profile_img"])
    st.image(Image.open(io.BytesIO(profile_img_data)), width=84, caption="Profil")
    
    st.markdown("<div class='brand'>Stockify Pro</div>", unsafe_allow_html=True)
    st.write("OOP-Based Inventory System")
    st.write("---")
    page = st.radio("Menu", ["Dashboard", "Add Item", "Items List", "Reports", "Settings"])

if page == "Dashboard":
    st.title("📊 Dashboard")
    
    stats = inv.get_statistics()
    low_stock_items = inv.get_low_stock_items(threshold=5)
    
    col1, col2, col3 = st.columns([1,1,1])
    col1.metric("Total SKUs", stats['total_items'])
    col2.metric("Total Quantity", stats['total_quantity'])
    col3.metric("Low Stock", stats['low_stock_count'])

    st.write("")
    st.markdown("#### ⚠️ Low Stock Items")
    if not low_stock_items:
        st.success("✅ All items are well stocked!")
    else:
        for item in low_stock_items:
            cols = st.columns([0.12, 0.6, 0.28])
            
            if item.image_data:
                img_bytes = base64.b64decode(item.image_data)
                cols[0].image(bytes_to_pil(img_bytes), width=64)
            else:
                cols[0].image(generate_default_avatar(64), width=64)
            
            cols[1].markdown(f"**{item.name}**\n\nQty: {item.qty} | Category: {item.category or 'N/A'}")
            
            if cols[2].button("Restock", key=f"restock-{item.id}"):
                try:
                    inv.restock_item(item.id, 10)
                    st.success(f"Restocked {item.name} (+10)")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.write("---")
    st.markdown("#### 📦 Recent Items")
    recent_items = inv.list_items(sort_by="created_at")[-5:]
    for item in reversed(recent_items):
        cols = st.columns([0.12, 0.6, 0.28])
        
        if item.image_data:
            img_bytes = base64.b64decode(item.image_data)
            cols[0].image(bytes_to_pil(img_bytes), width=64)
        else:
            cols[0].image(generate_default_avatar(64), width=64)
        
        cols[1].markdown(f"**{item.name}**\n\nAdded: {item.created_at.strftime('%Y-%m-%d %H:%M')}")
        cols[2].markdown(f"Qty: **{item.qty}**")

elif page == "Add Item":
    st.title("➕ Add New Item")
    
    with st.form("add_item_form", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        name = c1.text_input("Item Name *", key="item_name")
        qty = c2.number_input("Quantity *", min_value=0, value=1, step=1, key="item_qty")
        
        c3, c4 = st.columns(2)
        category = c3.text_input("Category", key="item_category")
        location = c4.text_input("Location", key="item_location")
        
        notes = st.text_area("Notes", key="item_notes")
        image_file = st.file_uploader("Image (optional)", type=["png","jpg","jpeg"], key="item_image")
        
        submitted = st.form_submit_button("Add Item")

        if submitted:
            try:
                image_data = None
                if image_file is not None:
                    img_bytes = image_file.read()
                    image_data = base64.b64encode(img_bytes).decode('utf-8')
                else:
                    default_img = generate_default_avatar(256)
                    image_data = pil_image_to_base64(default_img)

                item = inv.create_item(
                    name=name,
                    qty=qty,
                    image_data=image_data,
                    category=category or None,
                    location=location or None,
                    notes=notes or None
                )
                
                st.success(f"✅ Item '{item.name}' added successfully (ID: {item.id[:8]}...)")
                st.rerun()
                
            except ValidationError as e:
                st.error(f"❌ Validation Error: {e}")
            except DuplicateItemError as e:
                st.error(f"❌ Duplicate: {e}")
            except Exception as e:
                st.error(f"❌ Error: {e}")


elif page == "Items List":
    st.title("📋 Items List")
    
    col1, col2, col3 = st.columns([2,1,1])
    search_query = col1.text_input("🔍 Search items...", key="search_query")
    filter_category = col2.selectbox("Filter Category", ["All"] + list(inv.get_statistics()['categories'].keys()))
    sort_by = col3.selectbox("Sort By", ["name", "qty", "created_at", "updated_at"])
    
    if search_query:
        items_list = inv.search_items(search_query)
    else:
        items_list = inv.list_items(
            category=None if filter_category == "All" else filter_category,
            sort_by=sort_by
        )
    
    st.markdown(f"**{len(items_list)} items found**")
    st.write("---")
    
    for item in items_list:
        with st.container():
            cols = st.columns([0.12, 0.5, 0.38])
            
            if item.image_data:
                img_bytes = base64.b64decode(item.image_data)
                cols[0].image(bytes_to_pil(img_bytes), width=64)
            else:
                cols[0].image(generate_default_avatar(64), width=64)
            
            cols[1].markdown(f"**{item.name}**")
            cols[1].caption(f"Qty: {item.qty} | Category: {item.category or 'N/A'} | Location: {item.location or 'N/A'}")
            if item.notes:
                cols[1].caption(f"📝 {item.notes[:50]}...")
            
            action_cols = cols[2].columns([1,1,1])
            
            if action_cols[0].button("✏️", key=f"edit-{item.id}"):
                st.session_state[f"editing_{item.id}"] = True
            
            if action_cols[1].button("🗑️", key=f"del-{item.id}"):
                try:
                    inv.delete_item(item.id)
                    st.success(f"Deleted '{item.name}'")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            
            if action_cols[2].button("📜", key=f"hist-{item.id}"):
                st.session_state[f"show_history_{item.id}"] = True
            
            if st.session_state.get(f"editing_{item.id}", False):
                with st.expander(f"Edit {item.name}", expanded=True):
                    with st.form(f"edit_form_{item.id}"):
                        new_name = st.text_input("Name", value=item.name)
                        new_qty = st.number_input("Quantity", min_value=0, value=item.qty)
                        new_category = st.text_input("Category", value=item.category or "")
                        new_location = st.text_input("Location", value=item.location or "")
                        new_notes = st.text_area("Notes", value=item.notes or "")
                        
                        col_save, col_cancel = st.columns(2)
                        if col_save.form_submit_button("💾 Save"):
                            try:
                                inv.update_item(
                                    item.id,
                                    name=new_name,
                                    qty=new_qty,
                                    category=new_category or None,
                                    location=new_location or None,
                                    notes=new_notes or None
                                )
                                st.success("Updated successfully!")
                                st.session_state[f"editing_{item.id}"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        
                        if col_cancel.form_submit_button("❌ Cancel"):
                            st.session_state[f"editing_{item.id}"] = False
                            st.rerun()
            
            if st.session_state.get(f"show_history_{item.id}", False):
                with st.expander(f"History: {item.name}", expanded=True):
                    history = inv.get_item_history(item.id)
                    if history:
                        for log in reversed(history[-10:]): 
                            st.caption(f"🕒 {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                            st.caption(f"Operation: **{log.operation.value}**")
                            if log.old_value:
                                st.caption(f"Old: {log.old_value}")
                            if log.new_value:
                                st.caption(f"New: {log.new_value}")
                            st.divider()
                    else:
                        st.info("No history available")
                    
                    if st.button("Close", key=f"close_hist_{item.id}"):
                        st.session_state[f"show_history_{item.id}"] = False
                        st.rerun()
            
            st.divider()
    
    st.write("---")
    st.markdown("#### 🔧 Bulk Operations")
    
    col1, col2 = st.columns(2)
    
    if col1.button("📥 Export to CSV"):
        try:
            csv_path = "export_items.csv"
            inv.export_to_csv(csv_path)
            
            with open(csv_path, 'rb') as f:
                st.download_button(
                    "Download CSV",
                    data=f,
                    file_name=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            st.success("CSV exported successfully!")
        except Exception as e:
            st.error(f"Export failed: {e}")
    
    uploaded_csv = col2.file_uploader("📤 Import CSV", type=["csv"], key="import_csv")
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

elif page == "Reports":
    st.title("📊 Reports")
    
    stats = inv.get_statistics()
    
    st.markdown("### 📈 Overall Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items", stats['total_items'])
    col2.metric("Total Quantity", stats['total_quantity'])
    col3.metric("Categories", stats['total_categories'])
    col4.metric("Low Stock", stats['low_stock_count'])
    
    st.markdown("### 📦 Category Distribution")
    if stats['categories']:
        cat_df = pd.DataFrame(list(stats['categories'].items()), columns=['Category', 'Count'])
        st.bar_chart(cat_df.set_index('Category'))
    else:
        st.info("No category data available")
    
    st.markdown("### 📍 Location Distribution")
    if stats['locations']:
        loc_df = pd.DataFrame(list(stats['locations'].items()), columns=['Location', 'Count'])
        st.bar_chart(loc_df.set_index('Location'))
    else:
        st.info("No location data available")
    
    st.markdown("### 🕒 Recent Activity (Audit Logs)")
    recent_logs = inv.get_recent_logs(limit=20)
    if recent_logs:
        for log in reversed(recent_logs):
            st.caption(f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | **{log.operation.value}** | Item ID: {log.item_id[:8]}...")
    else:
        st.info("No activity logs yet")


elif page == "Settings":
    st.title("⚙️ Settings")
    
    st.markdown("### 👤 Profile Settings")
    col1, col2 = st.columns([1,2])
    
    with col1:
        profile_img_data = base64.b64decode(st.session_state["profile_img"])
        st.image(Image.open(io.BytesIO(profile_img_data)), width=150)
        
        uploaded = st.file_uploader("Upload profile picture", type=["jpg","jpeg","png"])
        if uploaded:
            img_bytes = uploaded.read()
            st.session_state["profile_img"] = base64.b64encode(img_bytes).decode('utf-8')
            st.success("Profile picture updated!")
            st.rerun()
    
    with col2:
        st.markdown("### 🔧 App Preferences")
        low_stock_threshold = st.number_input(
            "Low stock threshold", 
            min_value=0, 
            value=5,
            help="Items below this quantity will be flagged as low stock"
        )
        
        st.markdown("### 💾 Data Management")
        if st.button("🗄️ Create Backup"):
            try:
                inv._backup_data()
                st.success("Backup created successfully!")
            except Exception as e:
                st.error(f"Backup failed: {e}")
        
        st.warning("⚠️ Data is automatically saved after each operation")

st.markdown("---")
st.caption(f"Stockify Pro - OOP Edition | Items: {len(inv.items)} | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
