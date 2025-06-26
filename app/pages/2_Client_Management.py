# app/pages/2_Client_Management.py
import pandas as pd
import streamlit as st
from database import SessionLocal
from models import Client, ClientCategory
from sqlalchemy.orm import Session
from style_loader import load_css

load_css()
db: Session = SessionLocal()

st.header("Client Management")


st.subheader("Client List")
clients = db.query(Client).all()
if not clients:
    st.warning("No clients found.")
else:
    client_data = [
        {
            "ID": c.id,
            "Display Name": c.display_name,
            "Category": c.category.value,
            "VAT ID": c.vat_id or "---",
            "Email": c.email or "---",
            "Phone": c.phone_number or "---",
        }
        for c in clients
    ]
    df = pd.DataFrame(client_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Add a New Client")

# --- WIDGET MOVED OUTSIDE THE FORM ---
# This radio button now immediately triggers a rerun when changed.
category_str = st.radio(
    "Select Client Category",
    options=[c.value for c in ClientCategory],
    horizontal=True,
    key="client_category_radio",  # A key helps Streamlit track the widget
)

# --- THE FORM STARTS HERE ---
with st.form("new_client_form", clear_on_submit=True):
    # --- Conditional Fields based on the radio button state ---
    if category_str == ClientCategory.COMPANY.value:
        st.write("Company Information:")
        company_name = st.text_input("Company Name")
        vat_id = st.text_input("VAT ID")
        # Set personal names to None for companies
        first_name, last_name = None, None
    else:  # Individual
        st.write("Personal Information:")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        # Set company names to None for individuals
        company_name, vat_id = None, None

    # --- Common fields ---
    st.write("Contact & Address Information:")
    email = st.text_input("Email Address")
    phone_number = st.text_input("Phone Number")
    address_street = st.text_input("Street and Number")
    address_zipcode = st.text_input("ZIP Code")
    address_city = st.text_input("City")

    submitted = st.form_submit_button("Add Client")
    if submitted:
        is_company_valid = (
            category_str == ClientCategory.COMPANY.value and company_name and vat_id
        )
        is_individual_valid = (
            category_str == ClientCategory.INDIVIDUAL.value and first_name and last_name
        )

        if is_company_valid or is_individual_valid:
            new_client = Client(
                category=ClientCategory(category_str),
                company_name=company_name,
                vat_id=vat_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                address_street=address_street,
                address_zipcode=address_zipcode,
                address_city=address_city,
            )
            db.add(new_client)
            db.commit()
            st.success(f"Client '{new_client.display_name}' added!")
            st.rerun()
        else:
            st.error("Please fill all required fields for the selected category.")


db.close()
