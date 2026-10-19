import streamlit as st
import os
import json
import math
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Set page configuration for Chrome
st.set_page_config(
    page_title="Signmart Mediatech - Lightbox Manager",
    page_icon="💡",
    layout="wide"
)

CONFIG_FILE = "lightbox_config.json"

# Load default data structures
DEFAULT_ALUMINUM_FRAMES = {
    "frame_6cm_white": {"label": "Aluminum Frame 6cm Side Profile 6mtrs length (White)", "price": 2600.00, "cuttable": True},
    "frame_6cm_silver": {"label": "Aluminum Frame 6cm Side Profile 6mtrs length (Silver)", "price": 2600.00, "cuttable": True},
    "frame_6cm_sandblack": {"label": "Aluminum Frame 6cm Side Profile 6mtrs length (Sand Black)", "price": 2600.00, "cuttable": True},
    "frame_8cm_white": {"label": "Aluminum Frame 8cm Side Profile 6mtrs length (White)", "price": 2700.00, "cuttable": True},
    "frame_8cm_silver": {"label": "Aluminum Frame 8cm Side Profile 6mtrs length (Silver)", "price": 2700.00, "cuttable": True},
    "frame_8cm_sandblack": {"label": "Aluminum Frame 8cm Side Profile 6mtrs length (Sand Black)", "price": 2700.00, "cuttable": True},
    "frame_10cm_sandblack": {"label": "Aluminum Frame 10cm Side Profile 6mtrs length (Sand Black)", "price": 4000.00, "cuttable": True},
    "bracket_6cm": {"label": "L-Brackets 1 set per pack for 6cm", "price": 192.00, "cuttable": False},
    "bracket_8cm": {"label": "L-Brackets 1 set per pack for 8cm", "price": 216.00, "cuttable": False},
    "bracket_10cm": {"label": "L-Brackets 1 set per pack for 10cm", "price": 312.00, "cuttable": False},
}

DEFAULT_POWER_SUPPLIES = {
    "ps_12v_60w": {"label": "Slim Indoor Power Supply 12V 60W", "price": 517.00},
    "ps_12v_100w": {"label": "Slim Indoor Power Supply 12V 100W", "price": 640.00},
    "ps_12v_150w": {"label": "Slim Indoor Power Supply 12V 150W", "price": 694.00},
    "ps_12v_200w": {"label": "Slim Indoor Power Supply 12V 200W", "price": 841.00},
    "ps_12v_240w": {"label": "Slim Indoor Power Supply 12V 240W", "price": 876.00},
    "ps_12v_300w": {"label": "Slim Indoor Power Supply 12V 300W", "price": 900.00},
    "ps_12v_400w": {"label": "Slim Indoor Power Supply 12V 400W", "price": 937.00},
}

DEFAULT_UV_STF = {
    "uv_stf_standard": {"label": "UV STF", "price_per_sqft": 150.00},
    "uv_stf_seg": {"label": "Backlit Film W/ Add White ink", "price_per_sqft": 166.00}
}

DEFAULT_POLYCLOTH = {
    "polycloth_seg": {"label": "Polycloth W/Silicone Edge", "price_per_sqft": 160.00},
    "polycloth_standard": {"label": "Polycloth", "price_per_sqft": 140.00}
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "quotations": {},
        "receipts": {},
        "aluminum_frames": DEFAULT_ALUMINUM_FRAMES,
        "power_supplies": DEFAULT_POWER_SUPPLIES,
        "uv_stf": DEFAULT_UV_STF,
        "polycloth": DEFAULT_POLYCLOTH,
        "frame_length_cm": 604.0,
        "fallback_flat_rate": 800.0
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()

# --- Streamlit UI App Layout ---
st.title("💡 Signmart Mediatech — Lightbox & Quotation Manager")
st.sidebar.header("Navigation & Settings")

app_mode = st.sidebar.selectbox("Choose Mode", ["Create Quotation / POS", "View Saved Documents"])

if "cart" not in st.session_state:
    st.session_state.cart = []

if app_mode == "Create Quotation / POS":
    st.subheader("📝 New Client & Project Setup")
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer / Client Name")
        company_name = st.text_input("Company Name", value="N/A")
        contact_number = st.text_input("Contact Number")
    with col2:
        tin = st.text_input("TIN", value="N/A")
        address = st.text_input("Address")
        prepared_by = st.text_input("Prepared By", value="Vaughn Jordan")

    st.markdown("---")
    st.subheader("🛒 Add Items to Order")
    
    item_type = st.selectbox("Select Item Category", [
        "Fabric Cloth Lightbox", 
        "Aluminum Profile Frame", 
        "UV Print / Backlit Film", 
        "Polycloth Material",
        "Rush Fee / Installation"
    ])

    if item_type == "Fabric Cloth Lightbox":
        frame_size = st.selectbox("Frame Size Profile", ["6cm", "8cm", "10cm"])
        unit_mode = st.selectbox("Unit", ["CM", "MM", "IN", "FT"])
        
        c1, c2, c3 = st.columns(3)
        with c1: width = st.number_input("Width", min_value=1.0, value=100.0)
        with c2: height = st.number_input("Height", min_value=1.0, value=100.0)
        with c3: qty = st.number_input("Quantity (pcs)", min_value=1, value=1)

        if unit_mode == "CM": sq_ft = (width * height) / 929.0304
        elif unit_mode == "MM": sq_ft = (width * height) / 92903.04
        elif unit_mode == "FT": sq_ft = width * height
        else: sq_ft = (width * height) / 144.0

        default_rate = config.get("fallback_flat_rate", 800.0)
        rate = st.number_input("Rate per Sq. Ft. (P)", value=default_rate)
        custom_note = st.text_input("Custom Note / Description Override", value="")

        if st.button("Add Lightbox to Cart"):
            total_price = sq_ft * rate * qty
            item = {
                "type": "lightbox",
                "frame_size": frame_size,
                "unit": unit_mode,
                "width": width,
                "height": height,
                "sq_ft": sq_ft,
                "rate": rate,
                "qty": qty,
                "total_price": total_price,
                "custom_note": custom_note,
                "images": []
            }
            st.session_state.cart.append(item)
            st.success("Added Lightbox to Cart successfully!")

    elif item_type == "UV Print / Backlit Film":
        uv_db = config.get("uv_stf", DEFAULT_UV_STF)
        uv_choice = st.selectbox("Select Material Option", list(uv_db.keys()), format_func=lambda x: uv_db[x]["label"])
        selected_uv = uv_db[uv_choice]

        unit_mode = st.selectbox("Unit", ["CM", "MM", "IN", "FT"])
        c1, c2, c3 = st.columns(3)
        with c1: width = st.number_input("Width", min_value=1.0, value=100.0)
        with c2: height = st.number_input("Height", min_value=1.0, value=100.0)
        with c3: qty = st.number_input("Quantity", min_value=1, value=1)

        if unit_mode == "CM": sq_ft = (width * height) / 929.0304
        elif unit_mode == "MM": sq_ft = (width * height) / 92903.04
        elif unit_mode == "FT": sq_ft = width * height
        else: sq_ft = (width * height) / 144.0

        rate = st.number_input("Price per Sq. Ft.", value=selected_uv["price_per_sqft"])
        
        if st.button("Add Print Material to Cart"):
            total_price = sq_ft * rate * qty
            item = {
                "type": "uv_stf",
                "label": selected_uv["label"],
                "unit": unit_mode,
                "width": width,
                "height": height,
                "sq_ft": sq_ft,
                "rate": rate,
                "qty": qty,
                "total_price": total_price,
                "images": []
            }
            st.session_state.cart.append(item)
            st.success(f"Added {selected_uv['label']} to Cart!")

    # --- Cart Review Section ---
    st.markdown("---")
    st.subheader("📋 Current Cart Summary")
    if st.session_state.cart:
        subtotal = 0
        for i, cart_item in enumerate(st.session_state.cart):
            subtotal += cart_item["total_price"]
            st.write(f"**{i+1}.** {cart_item.get('label', cart_item.get('type'))} — Qty: {cart_item.get('qty', 1)} — **P{cart_item['total_price']:,.2f}**")
        
        st.markdown(f"### Subtotal: P{subtotal:,.2f}")
        
        if st.button("Clear Cart"):
            st.session_state.cart = []
            st.rerun()

        if st.button("💾 Save Quotation"):
            doc_id = "QT-" + datetime.now().strftime("%Y%m%d-%H%M")
            doc_data = {
                "date": datetime.now().strftime("%B %d, %Y"),
                "customer": customer_name if customer_name else "Walk-In Client",
                "company_name": company_name,
                "address": address,
                "tin": tin,
                "contact_number": contact_number,
                "items": st.session_state.cart,
                "subtotal": subtotal,
                "discount_percent": 0.0,
                "discount_amount": 0.0,
                "grand_total": subtotal,
                "down_payment": 0.0,
                "balance": subtotal,
                "si_number": doc_id
            }
            config["quotations"][doc_id] = doc_data
            save_config(config)
            st.success(f"Quotation successfully generated and saved with ID: {doc_id}!")
    else:
        st.info("Your cart is currently empty.")

elif app_mode == "View Saved Documents":
    st.subheader("📂 Saved Quotations & Receipts")
    saved_quotes = config.get("quotations", {})
    if saved_quotes:
        selected_doc = st.selectbox("Select Document ID", list(saved_quotes.keys()))
        doc = saved_quotes[selected_doc]
        st.write(f"**Client:** {doc['customer']} ({doc.get('company_name', 'N/A')})")
        st.write(f"**Date:** {doc['date']}")
        st.write(f"**Grand Total:** P{doc['grand_total']:,.2f}")
        
        st.markdown("#### Items:")
        for item in doc["items"]:
            st.text(f"- {item.get('type')} | Total: P{item['total_price']:,.2f}")
    else:
        st.info("No saved documents found.")