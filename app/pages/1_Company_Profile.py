# app/pages/1_Company_Profile.py (FINAL CORRECTED VERSION)

import streamlit as st
from database import SessionLocal
from models import CompanyProfile
from sqlalchemy.orm import Session
from style_loader import load_css

load_css()
# --- Initial Setup ---
db: Session = SessionLocal()

st.header("Manage Your Company Profile")

# --- Section to display the current profile ---
st.subheader("Current Company Information")
profile = db.query(CompanyProfile).first()

if not profile:
    st.info("No company profile has been saved yet. Please fill the form below.")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Company Name", value=profile.company_name or "", disabled=True)
        st.text_input("VAT ID (NIP)", value=profile.vat_id or "", disabled=True)
        st.text_input(
            "Bank Account Number",
            value=profile.bank_account_number or "",
            disabled=True,
        )
    with col2:
        st.text_input(
            "Address",
            value=f"{profile.address_street or ''}, {profile.address_zipcode or ''} {profile.address_city or ''}",
            disabled=True,
        )
        st.text_area(
            "Additional Info", value=profile.additional_info or "", disabled=True
        )

st.markdown("---")

# --- Section to edit the profile ---
with st.expander("Edit Company Profile"):
    if not profile:
        # If no profile exists, create a blank one for the form
        profile = CompanyProfile()

    with st.form("company_profile_form"):
        st.write("Enter or update your company details below.")

        # Step 1: Get values from widgets into temporary variables
        company_name = st.text_input("Company Name", value=profile.company_name or "")
        vat_id = st.text_input("VAT ID (NIP)", value=profile.vat_id or "")
        address_street = st.text_input(
            "Street and Number", value=profile.address_street or ""
        )
        address_zipcode = st.text_input("ZIP Code", value=profile.address_zipcode or "")
        address_city = st.text_input("City", value=profile.address_city or "")
        bank_account_number = st.text_input(
            "Bank Account Number", value=profile.bank_account_number or ""
        )
        additional_info = st.text_area(
            "Additional Info (e.g., on invoices)", value=profile.additional_info or ""
        )

        # --- FIX: The submit button and its logic are NOW INSIDE the form block ---
        submitted = st.form_submit_button("Save Profile")
        if submitted:
            # Step 2: Update the profile object with data from variables
            profile.company_name = company_name
            profile.vat_id = vat_id
            profile.address_street = address_street
            profile.address_zipcode = address_zipcode
            profile.address_city = address_city
            profile.bank_account_number = bank_account_number
            profile.additional_info = additional_info

            # If the profile is new, add it to the session
            if not profile.id:
                db.add(profile)

            db.commit()
            st.toast("Company profile saved successfully!", icon="✅")
            st.rerun()

# --- End of Page ---
db.close()
