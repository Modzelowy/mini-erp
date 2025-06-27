# app/pages/4_Orders.py (FINAL, SIMPLIFIED VERSION)

from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from database import SessionLocal
from models import (
    Client,
    CompanyProfile,
    Order,
    OrderItem,
    Product,
    ProductUnit,
)
from sqlalchemy.orm import Session, joinedload
from style_loader import load_css
from utils import generate_invoice_pdf, get_next_invoice_number

load_css()
db: Session = SessionLocal()

st.header("Order Management")
tab1, tab2 = st.tabs(["Order List", "Create New Order"])

with tab1:
    st.subheader("Existing Orders")
    clients = db.query(Client).all()
    client_display_names_filter = ["All"] + [c.display_name for c in clients]
    selected_client_filter = st.selectbox(
        "Filter by Client", options=client_display_names_filter
    )
    query = (
        db.query(Order)
        .options(
            joinedload(Order.client),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .order_by(Order.order_date.desc())
    )
    if selected_client_filter != "All":
        selected_client_obj = next(
            (c for c in clients if c.display_name == selected_client_filter), None
        )
        if selected_client_obj:
            query = query.filter(Order.client_id == selected_client_obj.id)

    orders = query.all()

    if not orders:
        st.info("No orders found matching the criteria.")
    else:
        for order in orders:
            status = order.payment_status.value
            color = (
                "green"
                if status == "Paid"
                else "orange"
                if status == "Unpaid"
                else "red"
            )
            invoice_info = (
                f"| Invoice: {order.invoice_number}" if order.invoice_number else ""
            )
            expander_title = (
                f"Order #{order.id} - {order.client.display_name} {invoice_info} | "
                f"Status: :{color}[{status}]"
            )
            with st.expander(expander_title):
                st.write("**Financial Details:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text_input(
                        "Invoice Number",
                        value=order.invoice_number or "Not generated",
                        disabled=True,
                        key=f"inv_num_{order.id}",
                    )
                with col2:
                    st.text_input(
                        "Order Date",
                        value=order.order_date.strftime("%Y-%m-%d"),
                        disabled=True,
                        key=f"ord_date_{order.id}",
                    )
                with col3:
                    due_date_str = (
                        order.payment_due_date.strftime("%Y-%m-%d")
                        if order.payment_due_date
                        else "Not set"
                    )
                    st.text_input(
                        "Payment Due Date",
                        value=due_date_str,
                        disabled=True,
                        key=f"due_date_{order.id}",
                    )

                st.write("**Items in this order:**")
                items_data = [
                    {
                        "Product": item.product.name,
                        "Quantity": item.quantity,
                        "Unit": item.product.unit.value,
                        "Price/Unit": f"{item.price_per_unit:.2f}",
                        "VAT (%)": item.vat_rate,
                        "Total": f"{(item.quantity * item.price_per_unit):.2f}",
                    }
                    for item in order.items
                ]
                st.dataframe(
                    pd.DataFrame(items_data), use_container_width=True, hide_index=True
                )

                st.markdown("---")
                st.write("**Actions**")

                if order.invoice_number:
                    st.success(f"Invoice {order.invoice_number} has been generated.")
                    company = db.query(CompanyProfile).first()
                    if company:
                        pdf_bytes = generate_invoice_pdf(order, company)
                        st.download_button(
                            label="📄 Download Invoice PDF",
                            data=pdf_bytes,
                            file_name=f"Faktura_{order.invoice_number.replace('/', '-')}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{order.id}",
                        )
                    else:
                        st.warning(
                            "Cannot generate PDF. Please complete company profile first."
                        )
                else:
                    if st.button("Generate Invoice", key=f"gen_inv_{order.id}"):
                        next_inv_num = get_next_invoice_number(db)
                        order.invoice_number = next_inv_num
                        order.payment_due_date = datetime.now() + timedelta(days=14)
                        db.commit()
                        st.toast(
                            f"Invoice {order.invoice_number} generated!", icon="🎉"
                        )
                        st.rerun()

with tab2:
    if "cart" not in st.session_state:
        st.session_state.cart = []
    st.subheader("Order Details")
    clients = db.query(Client).all()
    if not clients:
        st.error("Cannot create an order. Please add a client first.")
        st.stop()
    with st.form("order_form"):
        client_display_names = [c.display_name for c in clients]
        selected_client_name = st.selectbox(
            "Select Client for New Order", options=client_display_names
        )
        st.subheader("Order Items (Cart)")
        if not st.session_state.cart:
            st.info("Your cart is empty. Add products below.")
        else:
            cart_df = pd.DataFrame(st.session_state.cart).rename(
                columns={"VAT Rate (%)": "VAT %"}
            )
            st.dataframe(cart_df, use_container_width=True, hide_index=True)
        submitted_order = st.form_submit_button("Create Final Order")
    with st.expander("Add Product to Order", expanded=True):
        products = db.query(Product).all()
        with st.form("add_item_form", clear_on_submit=True):
            product_index_str = st.text_input("Enter Product Index / SKU")
            quantity = st.number_input(
                "Quantity", min_value=0.01, step=0.01, format="%.2f"
            )
            price_per_unit = st.number_input(
                "Price per Unit (Net)", min_value=0.01, step=0.01
            )
            if st.form_submit_button("Add by Index"):
                if product_index_str and quantity > 0:
                    if not product_index_str.isdigit():
                        st.error("Product Index must be a numeric value.")
                    else:
                        product_index = int(product_index_str)
                        selected_product = (
                            db.query(Product)
                            .filter(Product.product_index == product_index)
                            .first()
                        )
                        if selected_product:
                            is_integer_unit = selected_product.unit in [
                                ProductUnit.PCS,
                                ProductUnit.SET,
                            ]
                            if is_integer_unit and (quantity % 1 != 0):
                                st.error(
                                    f"Quantity for unit '{selected_product.unit.value}' must be a whole number."
                                )
                            else:
                                st.session_state.cart.append(
                                    {
                                        "Product ID": selected_product.id,
                                        "Product Name": selected_product.name,
                                        "Quantity": quantity,
                                        "Price per Unit": price_per_unit,
                                        "Unit": selected_product.unit.value,
                                        "VAT Rate (%)": selected_product.vat_rate,
                                    }
                                )
                                st.rerun()
                        else:
                            st.error(
                                f"Product with index '{product_index_str}' not found!"
                            )
                else:
                    st.warning("Please fill all fields to add an item.")
    if submitted_order:
        if not st.session_state.cart:
            st.error("Cannot create an empty order.")
            st.stop()
        client_obj = next(
            (c for c in clients if c.display_name == selected_client_name), None
        )
        if client_obj:
            new_order = Order(client_id=client_obj.id)
            db.add(new_order)
            db.flush()
            for item in st.session_state.cart:
                # --- THIS IS THE FINAL FIX ---
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item["Product ID"],
                    quantity=item["Quantity"],
                    price_per_unit=item["Price per Unit"],
                    vat_rate=item["VAT Rate (%)"],  # We pass the captured VAT rate here
                )
                db.add(order_item)
            db.commit()
            st.session_state.cart = []
            st.success(
                f"Order #{new_order.id} for {client_obj.display_name} has been created!"
            )
            st.rerun()

db.close()
