# app/main.py (FINAL, FULLY CORRECTED VERSION)

import pandas as pd
import streamlit as st
from database import SessionLocal, engine
from models import (
    Base,
    Client,
    ClientType,
    CompanyProfile,
    Order,
    OrderItem,
    Product,
    ProductUnit,
)
from sqlalchemy.orm import Session, joinedload
from streamlit_option_menu import option_menu

# --- Initial Setup ---
Base.metadata.create_all(bind=engine)
db_session: Session = SessionLocal()

# --- Styling ---
st.set_page_config(layout="wide")
st.markdown(
    """
<style>
    /* Style for text inputs and text areas */
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


def page_company_profile(db: Session) -> None:
    st.header("Manage Your Company Profile")
    profile = db.query(CompanyProfile).first()
    if not profile:
        profile = CompanyProfile()
    with st.form("company_profile_form"):
        st.write(
            "Enter your company details. This information will be used on invoices."
        )
        profile.company_name = st.text_input(
            "Company Name", value=profile.company_name or ""
        )
        profile.vat_id = st.text_input("VAT ID (NIP)", value=profile.vat_id or "")
        profile.address_street = st.text_input(
            "Street and Number", value=profile.address_street or ""
        )
        profile.address_zipcode = st.text_input(
            "ZIP Code", value=profile.address_zipcode or ""
        )
        profile.address_city = st.text_input("City", value=profile.address_city or "")
        profile.bank_account_number = st.text_input(
            "Bank Account Number", value=profile.bank_account_number or ""
        )
        profile.additional_info = st.text_area(
            "Additional Info (e.g., on invoices)", value=profile.additional_info or ""
        )
        if st.form_submit_button("Save Profile"):
            if not profile.id:
                db.add(profile)
            db.commit()
            st.success("Company profile saved successfully!")
            st.rerun()


def page_client_management(db: Session) -> None:
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
        st.dataframe(df, use_container_width=True, hide_index=True)
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


def page_product_database(db: Session) -> None:
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
                }
                for p in products
            ]
            st.dataframe(
                pd.DataFrame(product_data), use_container_width=True, hide_index=True
            )
    with tab2:
        st.subheader("Add a New Product")
        with st.form("new_product_form", clear_on_submit=True):
            name = st.text_input("Product Name")
            product_index_str = st.text_input("Product Index / SKU (must be numeric)")
            unit = st.selectbox("Unit", options=[u.value for u in ProductUnit])
            stock = st.number_input("Initial Stock", min_value=0.0, step=1.0)
            if st.form_submit_button("Add Product"):
                if not (name and product_index_str and unit):
                    st.error("Please fill all fields.")
                elif not product_index_str.isdigit():
                    st.error("Product Index must be a numeric value.")
                else:
                    product_index = int(product_index_str)
                    if (
                        db.query(Product)
                        .filter(Product.product_index == product_index)
                        .first()
                    ):
                        st.error(
                            f"A product with index {product_index} already exists!"
                        )
                    else:
                        new_product = Product(
                            name=name,
                            product_index=product_index,
                            unit=ProductUnit(unit),
                            stock=stock,
                        )
                        db.add(new_product)
                        db.commit()
                        st.success(f"Product '{name}' added successfully!")
                        st.rerun()


def page_orders(db: Session) -> None:
    st.header("Order Management")
    tab1, tab2 = st.tabs(["Order List", "Create New Order"])
    with tab1:
        st.subheader("Existing Orders")
        clients = db.query(Client).all()
        client_names = ["All"] + [c.company_name for c in clients]
        selected_client_filter = st.selectbox("Filter by Client", options=client_names)
        query = (
            db.query(Order)
            .options(
                joinedload(Order.client),
                joinedload(Order.items).joinedload(OrderItem.product),
            )
            .order_by(Order.order_date.desc())
        )
        if selected_client_filter != "All":
            query = query.join(Client).filter(
                Client.company_name == selected_client_filter
            )
        orders = query.all()
        if not orders:
            st.info("No orders found matching the criteria.")
        else:
            for order in orders:
                expander_title = f"Order #{order.id} - {order.client.company_name} ({order.order_date.strftime('%Y-%m-%d')}) - Total: {order.total_value:.2f} PLN"
                with st.expander(expander_title):
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
    with tab2:
        if "cart" not in st.session_state:
            st.session_state.cart = []
        st.subheader("Order Details")
        clients = db.query(Client).all()
        # products = db.query(Product).all() # RUFF FIX: This was unused, so we get it inside the form instead.
        if not clients:
            st.error("Cannot create an order. Please add a client first.")
            return  # RUFF FIX: Replaced one-liner with proper return
        with st.form("order_form"):
            selected_client_name = st.selectbox(
                "Select Client for New Order", options=[c.company_name for c in clients]
            )
            st.subheader("Order Items (Cart)")
            if not st.session_state.cart:
                st.info("Your cart is empty. Add products below.")
            else:
                st.dataframe(
                    pd.DataFrame(st.session_state.cart),
                    use_container_width=True,
                    hide_index=True,
                )
            submitted_order = st.form_submit_button("Create Final Order")
        with st.expander("Add Product to Order", expanded=True):
            with st.form("add_item_form", clear_on_submit=True):
                product_index_str = st.text_input("Enter Product Index / SKU")
                quantity = st.number_input("Quantity", min_value=0.01, step=0.1)
                price_per_unit = st.number_input(
                    "Price per Unit", min_value=0.01, step=0.01
                )
                if st.form_submit_button("Add by Index"):
                    if product_index_str and quantity > 0:
                        products = db.query(
                            Product
                        ).all()  # Get products only when needed
                        selected_product = next(
                            (
                                p
                                for p in products
                                if p.product_index == int(product_index_str)
                            ),
                            None,
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
            else:
                client_obj = next(
                    (c for c in clients if c.company_name == selected_client_name), None
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
                        f"Order #{new_order.id} for {client_obj.company_name} has been created!"
                    )
                    st.rerun()


# --- Main App Router ---
with st.sidebar:
    page = option_menu(
        "Navigation",
        ["Company Profile", "Client Management", "Product Database", "Orders"],
        icons=["building-fill", "people-fill", "box-seam-fill", "cart-check-fill"],
        menu_icon="robot",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#1f1f2e"},
            "icon": {"color": "#c4a7e7", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#33334d",
            },
            "nav-link-selected": {"background-color": "#ff4b4b"},
        },
    )

st.title("Mini ERP System")
if page == "Company Profile":
    page_company_profile(db_session)
elif page == "Client Management":
    page_client_management(db_session)
elif page == "Product Database":
    page_product_database(db_session)
elif page == "Orders":
    page_orders(db_session)
db_session.close()
