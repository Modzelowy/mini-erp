# app/main.py (FINALNA WERSJA)

import streamlit as st
import pandas as pd
from database import engine, SessionLocal
from models import (
    Base,
    Client,
    ClientType,
    Product,
    ProductUnit,
    Order,
    OrderItem,
)  # Added Order, OrderItem
from streamlit_option_menu import option_menu
from sqlalchemy.orm import joinedload

# --- Initial Setup ---
Base.metadata.create_all(bind=engine)
db_session = SessionLocal()

# --- Styling ---
st.set_page_config(layout="wide")

st.markdown(
    """
<style>
    /* Style for text inputs */
    div[data-baseweb="input"] > div > input, div[data-baseweb="input"] > div > textarea {
        border-radius: 8px !important;
        border: 2px solid #ff4b4b !important;
    }
    /* Style for select boxes */
    div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border: 2px solid #ff4b4b !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- Page Functions ---


def page_client_management(db):
    st.header("Client Management")
    st.subheader("Client List")
    clients = db.query(Client).all()
    if not clients:
        st.warning("No clients found.")
    else:
        df = pd.DataFrame(
            [
                {
                    "ID": c.id,
                    "Company Name": c.company_name,
                    "VAT ID": c.vat_id,
                    "Type": c.client_type.value,
                }
                for c in clients
            ]
        )
        st.dataframe(df, use_container_width=True)

    st.subheader("Add a New Client")
    with st.form("new_client_form", clear_on_submit=True):
        company_name = st.text_input("Company Name")
        vat_id = st.text_input("VAT ID")
        client_type = st.selectbox("Client Type", options=[t.value for t in ClientType])
        if st.form_submit_button("Add Client"):
            if company_name and vat_id:
                new_client = Client(
                    company_name=company_name,
                    vat_id=vat_id,
                    client_type=ClientType(client_type),
                )
                db.add(new_client)
                db.commit()
                st.success(f"Client '{company_name}' added!")
                st.rerun()
            else:
                st.error("Please fill all fields.")


def page_product_database(db):
    st.header("Product Database Management")
    st.subheader("Product List")
    products = db.query(Product).all()
    if not products:
        st.warning("No products found.")
    else:
        df = pd.DataFrame(
            [
                {
                    "ID": p.id,
                    "Product Name": p.name,
                    "Index": p.product_index,
                    "Unit": p.unit.value,
                }
                for p in products
            ]
        )
        st.dataframe(df, use_container_width=True)

    st.subheader("Add a New Product")
    with st.form("new_product_form", clear_on_submit=True):
        name = st.text_input("Product Name")
        product_index = st.text_input("Product Index / SKU")
        unit = st.selectbox("Unit", options=[u.value for u in ProductUnit])
        if st.form_submit_button("Add Product"):
            if name and product_index:
                new_product = Product(
                    name=name, product_index=product_index, unit=ProductUnit(unit)
                )
                db.add(new_product)
                db.commit()
                st.success(f"Product '{name}' added!")
                st.rerun()
            else:
                st.error("Please fill all fields.")


def page_orders(db):
    st.header("Order Management")

    # --- Initialize session state for the shopping cart ---
    if "cart" not in st.session_state:
        st.session_state.cart = []

    # --- Display Existing Orders ---
    st.subheader("Existing Orders")
    # Eagerly load client and items data to prevent multiple DB queries
    orders = (
        db.query(Order)
        .options(
            joinedload(Order.client),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .order_by(Order.order_date.desc())
        .all()
    )

    if not orders:
        st.info("No orders found yet.")
    else:
        for order in orders:
            with st.expander(
                f"Order #{order.id} - {order.client.company_name} ({order.order_date.strftime('%Y-%m-%d')}) - Total: {order.total_value:.2f} PLN"
            ):
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
                st.dataframe(pd.DataFrame(items_data), use_container_width=True)

    # --- Create New Order Form ---
    st.subheader("Create a New Order")
    clients = db.query(Client).all()
    products = db.query(Product).all()

    if not clients:
        st.error("Cannot create an order. Please add a client first.")
        return

    # Use a form for the main order details
    with st.form("order_form"):
        selected_client_name = st.selectbox(
            "Select Client", options=[c.company_name for c in clients]
        )

        st.write("---")
        st.subheader("Order Items (Cart)")

        # Display current cart
        if not st.session_state.cart:
            st.info("Your cart is empty. Add products below.")
        else:
            cart_df = pd.DataFrame(st.session_state.cart)
            st.dataframe(cart_df, use_container_width=True)

        # Final submit button for the whole order
        submitted_order = st.form_submit_button("Create Final Order")

    # --- Add product to cart section (outside the main form) ---
    with st.expander("Add Product to Order", expanded=True):
        with st.form("add_item_form", clear_on_submit=True):
            selected_product_name = st.selectbox(
                "Select Product", options=[p.name for p in products]
            )
            quantity = st.number_input(
                "Quantity", min_value=0.01, step=0.1, format="%.2f"
            )
            price_per_unit = st.number_input(
                "Price per Unit", min_value=0.01, step=0.01, format="%.2f"
            )
            add_item_submitted = st.form_submit_button("Add to Cart")

            if add_item_submitted:
                if selected_product_name and quantity > 0 and price_per_unit > 0:
                    selected_product = next(
                        (p for p in products if p.name == selected_product_name), None
                    )
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

    # --- Logic to process the final order submission ---
    if submitted_order:
        if not st.session_state.cart:
            st.error("Cannot create an empty order. Please add items to the cart.")
        else:
            # Create the main Order object
            client_obj = next(
                (c for c in clients if c.company_name == selected_client_name), None
            )
            new_order = Order(client_id=client_obj.id)
            db.add(new_order)
            db.flush()  # Flush to get the new_order.id before committing

            # Create OrderItem objects from the cart
            for item in st.session_state.cart:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item["Product ID"],
                    quantity=item["Quantity"],
                    price_per_unit=item["Price per Unit"],
                )
                db.add(order_item)

            # Commit everything to the database
            db.commit()

            # Clear the cart and show success message
            st.session_state.cart = []
            st.success(
                f"Order #{new_order.id} for {client_obj.company_name} has been created successfully!"
            )
            st.rerun()


# --- Main App Router ---
with st.sidebar:
    page = option_menu(
        menu_title="Navigation",  # required
        options=["Client Management", "Product Database", "Orders"],  # required
        # Icons from https://icons.getbootstrap.com/
        icons=["people-fill", "box-seam-fill", "cart-check-fill"],  # optional
        menu_icon="robot",  # optional
        default_index=2,  # optional
        styles={
            "container": {"padding": "0!important", "background-color": "#1f1f2e"},
            "icon": {"color": "#c4a7e7", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#33334d",
            },
            # This is the style for the selected (active) button
            "nav-link-selected": {"background-color": "#ff4b4b"},
        },
    )

st.title("Mini ERP System")

if page == "Client Management":
    page_client_management(db_session)
elif page == "Product Database":
    page_product_database(db_session)
elif page == "Orders":
    page_orders(db_session)

db_session.close()
