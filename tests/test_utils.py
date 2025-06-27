# tests/test_utils.py (FINAL, CLEANED VERSION)

from collections.abc import Generator  # <-- NEW, REQUIRED IMPORT
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Imports must now be explicit from the 'app' package
from app.models import Base, Client, ClientCategory, Order
from app.utils import get_next_invoice_number


# --- Test Setup ---
@pytest.fixture(scope="function")
def db_session() -> Generator[
    Session, None, None
]:  # <-- FIX: Correct return type for a generator
    """
    Pytest fixture to create a temporary, in-memory SQLite database
    for each test function.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


# --- Tests for get_next_invoice_number ---
def test_get_next_invoice_number_on_empty_db(db_session: Session):
    # ... (kod testu bez zmian)
    next_number = get_next_invoice_number(db_session)
    now = datetime.now()
    expected_number = f"FV/1/{now.month}/{now.year}"
    assert next_number == expected_number


def test_get_next_invoice_number_with_existing_invoices(db_session: Session):
    # ... (kod testu bez zmian)
    now = datetime.now()
    dummy_client = Client(
        category=ClientCategory.COMPANY,
        company_name="Test Client",
        vat_id="PL1112223344",
    )
    db_session.add(dummy_client)
    db_session.commit()
    existing_order = Order(
        client_id=dummy_client.id,
        invoice_number=f"FV/5/{now.month}/{now.year}",
        order_date=now,
    )
    db_session.add(existing_order)
    db_session.commit()
    next_number = get_next_invoice_number(db_session)
    expected_number = f"FV/6/{now.month}/{now.year}"
    assert next_number == expected_number
