# The sys.path hack is no longer needed thanks to the pytest configuration.

# We now import directly from 'models' because pytest treats the 'app' directory as a source root.
from models import Client, ClientType


def test_client_creation():
    """
    Tests that a Client object can be created with correct attributes.
    """
    # 1. Setup: Create a new client instance
    client = Client(
        company_name="Test Corp",
        vat_id="PL9999999999",
        client_type=ClientType.RECIPIENT,
    )

    # 2. Assertions: Check if the attributes are set correctly
    assert client.company_name == "Test Corp"
    assert client.vat_id == "PL9999999999"
    assert client.client_type == ClientType.RECIPIENT


def test_client_repr():
    """
    Tests the string representation (__repr__) of the Client model.
    """
    # 1. Setup
    client = Client(
        company_name="Test Corp",
        vat_id="PL9999999999",
        client_type=ClientType.RECIPIENT,
    )

    # 2. Assertion
    expected_repr = "<Client(company_name='Test Corp')>"
    assert repr(client) == expected_repr
