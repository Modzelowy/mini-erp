# app/pages/3_Product_Database.py (VERSION WITH AUTO-INDEX)

import pandas as pd
import streamlit as st
from database import SessionLocal
from models import Product, ProductUnit
from sqlalchemy.orm import Session
from style_loader import load_css
from utils import get_next_product_index  # <-- NEW IMPORT

load_css()
db: Session = SessionLocal()

st.header("Product Database Management")
tab1, tab2 = st.tabs(["Product List", "Add New Product"])

with tab1:
    st.subheader("Search and Filter Products")
    search_name = st.text_input("Search by Product Name")
    search_index = st.text_input("Search by Product Index")
    query = db.query(Product)
    if search_name:
        query = query.filter(Product.name.ilike(f"%{search_name}%"))
    if search_index and search_index.isdigit():
        query = query.filter(Product.product_index == int(search_index))
    products = query.all()
    st.subheader("Product List")
    if not products:
        st.warning("No products found matching your criteria.")
    else:
        product_data = [
            {
                "Product Name": p.name,
                "Index": p.product_index,
                "Unit": p.unit.value,
                "Stock": p.stock,
                "VAT Rate (%)": p.vat_rate,
            }
            for p in products
        ]
        st.dataframe(
            pd.DataFrame(product_data), use_container_width=True, hide_index=True
        )

with tab2:
    st.subheader("Add a New Product")
    with st.form("new_product_form", clear_on_submit=True):
        st.info("A unique Product Index will be assigned automatically.")
        name = st.text_input("Product Name")
        unit = st.selectbox("Unit", options=[u.value for u in ProductUnit])
        stock = st.number_input("Initial Stock", min_value=0.0, step=1.0)
        vat_rate = st.number_input(
            "VAT Rate (%)", min_value=0.0, max_value=100.0, value=23.0, step=1.0
        )

        # REMOVED: product_index_str text input

        if st.form_submit_button("Add Product"):
            if not name:
                st.error("Product Name is required.")
            else:
                # NEW: Get the next available index automatically
                new_index = get_next_product_index(db)

                new_product = Product(
                    name=name,
                    product_index=new_index,
                    unit=ProductUnit(unit),
                    stock=stock,
                    vat_rate=vat_rate,
                )
                db.add(new_product)
                db.commit()
                st.success(
                    f"Product '{name}' with index {new_index} added successfully!"
                )
                st.rerun()

db.close()
