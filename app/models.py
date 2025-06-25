# app/models.py (THE FINAL, ULTIMATE, CORRECT VERSION)

import enum
from datetime import datetime

from database import Base
from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum

# Mapped_column is the new, correct function for typed columns
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ClientType(enum.Enum):
    RECIPIENT = "Recipient"
    SUPPLIER = "Supplier"


class ProductUnit(enum.Enum):
    PCS = "pcs"
    KG = "kg"
    SET = "set"
    M = "m"


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)

    product: Mapped["Product"] = relationship(lazy="joined")
    order: Mapped["Order"] = relationship(back_populates="items")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))

    client: Mapped["Client"] = relationship(back_populates="orders", lazy="joined")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def total_value(self) -> float:
        return sum(item.quantity * item.price_per_unit for item in self.items)

    def __repr__(self) -> str:
        # Check if client is loaded to prevent errors during certain operations
        if self.client:
            return f"<Order(id={self.id}, client='{self.client.company_name}')>"
        return f"<Order(id={self.id})>"


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    vat_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    client_type: Mapped[ClientType] = mapped_column(SAEnum(ClientType), nullable=False)

    orders: Mapped[list["Order"]] = relationship(back_populates="client")

    def __repr__(self) -> str:
        return f"<Client(company_name='{self.company_name}')>"


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    product_index: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    unit: Mapped[ProductUnit] = mapped_column(SAEnum(ProductUnit), nullable=False)
    stock: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    def __repr__(self) -> str:
        return f"<Product(name='{self.name}')>"


class CompanyProfile(Base):
    __tablename__ = "company_profile"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String, nullable=True)
    vat_id: Mapped[str] = mapped_column(String, nullable=True)
    address_street: Mapped[str] = mapped_column(String, nullable=True)
    address_zipcode: Mapped[str] = mapped_column(String, nullable=True)
    address_city: Mapped[str] = mapped_column(String, nullable=True)
    bank_account_number: Mapped[str | None] = mapped_column(String, nullable=True)
    additional_info: Mapped[str | None] = mapped_column(Text, nullable=True)
