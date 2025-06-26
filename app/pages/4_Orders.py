# app/pages/4_Orders.py (FINAL CORRECTED VERSION)

import pandas as pd
import streamlit as st
from database import SessionLocal
from models import Client, Order, OrderItem, Product
from sqlalchemy.orm import Session, joinedload
from style_loader import load_css

load_css()

# --- Initial Setup ---
db: Session = SessionLocal()

st.header("Order Management")

tab1, tab2 = st.tabs(["Order List", "Create New Order"])

# --- Code for the "Order List" Tab ---
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
            expander_title = (
                f"Order #{order.id} - {order.client.display_name} "
                f"({order.order_date.strftime('%Y-%m-%d')}) - "
                f"Total: {order.total_value:.2f} PLN"
            )
            with st.expander(expander_title):
                st.write("Items in this order:")
                items_data = [
                    {
                        "Product": item.product.name,
                        "Quantity": item.quantity,
                        "Unit": item.product.unit.value,
                        "Price/Unit": f"{item.price_per_unit:.2f}",
                        "Total": f"{(item.quantity * item.price_per_unit):.2f}",
                    }
                    for item in order.items
                ]
                st.dataframe(
                    pd.DataFrame(items_data),
                    use_container_width=True,
                    hide_index=True,
                )

# --- Code for the "Create New Order" Tab ---
with tab2:
    if "cart" not in st.session_state:
        st.session_state.cart = []

    st.subheader("Order Details")
    clients = db.query(Client).all()

    if not clients:
        st.error("Cannot create an order. Please add a client first.")
        st.stop()  # <-- FIX 1: Replaced return with st.stop()

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
        products = db.query(Product).all()  # Get products here to have them available
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
                            st.session_state.cart.append(
                                {
                                    "Product ID": selected_product.id,
                                    "Product Name": selected_product.name,
                                    "Quantity": quantity,
                                    "Price per Unit": price_per_unit,
                                    "Unit": selected_product.unit.value,
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
            st.stop()  # <-- FIX 2: Replaced return with st.stop()

        client_obj = next(
            (c for c in clients if c.display_name == selected_client_name), None
        )
        if client_obj:
            new_order = Order(client_id=client_obj.id)
            db.add(new_order)
            db.flush()
            for item in st.session_state.cart:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item["Product ID"],
                    quantity=item["Quantity"],
                    price_per_unit=item["Price per Unit"],
                )
                db.add(order_item)
            db.commit()
            st.session_state.cart = []
            st.success(
                f"Order #{new_order.id} for {client_obj.display_name} has been created!"
            )
            st.rerun()

# --- End of Page ---
db.close()
