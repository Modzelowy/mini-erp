# tests/test_models.py (CLEANED VERSION)

from app.models import Client, ClientCategory


def test_client_creation():
    """
    Tests that a Client object can be created with correct attributes.
    """
    client = Client(
        category=ClientCategory.COMPANY,
        company_name="Test Corp",
        vat_id="PL9999999999",
    )
    assert client.company_name == "Test Corp"
    assert client.category == ClientCategory.COMPANY


def test_client_repr():
    """
    Tests the string representation (__repr__) of the Client model.
    """
    client = Client(
        category=ClientCategory.INDIVIDUAL,
        first_name="Jan",
        last_name="Kowalski",
    )
    expected_repr = "<Client(id=None, name='Jan Kowalski')>"
    assert repr(client) == expected_repr
