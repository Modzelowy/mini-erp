# app/models.py (NOWA, PEŁNA WERSJA)

import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum as SAEnum,
    DateTime,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from database import Base


# --- Enums ---
class ClientType(enum.Enum):
    RECIPIENT = "Recipient"
    SUPPLIER = "Supplier"


class ProductUnit(enum.Enum):
    PCS = "szt"
    KG = "kg"
    SET = "kpl"
    M = "m"


# --- Association Object for Many-to-Many relationship ---
# This class links an Order with a Product and stores extra data like quantity and price.
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    price_per_unit = Column(Float, nullable=False)

    # Relationships to easily access the linked Order and Product objects
    product = relationship("Product")
    order = relationship("Order", back_populates="items")


# --- Main Models ---
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True, nullable=False)
    vat_id = Column(String, unique=True, index=True, nullable=False)
    client_type = Column(SAEnum(ClientType), nullable=False)

    # This relationship links a Client to their Orders
    orders = relationship("Order", back_populates="client")

    def __repr__(self):
        return f"<Client(company_name='{self.company_name}')>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    product_index = Column(String, unique=True, index=True, nullable=False)
    unit = Column(SAEnum(ProductUnit), nullable=False)

    def __repr__(self):
        return f"<Product(name='{self.name}')>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    # This relationship links an Order back to its Client
    client = relationship("Client", back_populates="orders")

    # This relationship links an Order to its OrderItem objects
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    # A helper property to easily calculate the total value of the order
    @property
    def total_value(self):
        return sum(item.quantity * item.price_per_unit for item in self.items)

    def __repr__(self):
        return f"<Order(id={self.id}, client='{self.client.company_name}')>"
