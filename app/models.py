# app/models.py (Version with ONLY the Client refactor)
import enum
from datetime import datetime

from database import Base
from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


# --- Enums ---
class ClientCategory(enum.Enum):
    COMPANY = "Company"
    INDIVIDUAL = "Individual"


class ClientType(enum.Enum):
    RECIPIENT = "Recipient"
    SUPPLIER = "Supplier"


class ProductUnit(enum.Enum):
    PCS = "pcs"
    KG = "kg"
    SET = "set"
    M = "m"


class PaymentStatus(enum.Enum):
    UNPAID = "Unpaid"
    PAID = "Paid"
    OVERDUE = "Overdue"


# --- Models ---
class OrderItem(Base):
    __tablename__ = "order_items"
    # ... (no changes in this class body)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    vat_rate: Mapped[float] = mapped_column(Float, nullable=False)
    product: Mapped["Product"] = relationship(lazy="joined")
    order: Mapped["Order"] = relationship(back_populates="items")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_number: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    payment_due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.UNPAID
    )
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
        if self.client:
            return f"<Order(id={self.id}, client='{self.client.display_name}')>"
        return f"<Order(id={self.id})>"


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[ClientCategory] = mapped_column(
        SAEnum(ClientCategory), nullable=False
    )
    company_name: Mapped[str | None] = mapped_column(String, index=True)
    vat_id: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String)
    phone_number: Mapped[str | None] = mapped_column(String)
    address_street: Mapped[str | None] = mapped_column(String)
    address_zipcode: Mapped[str | None] = mapped_column(String)
    address_city: Mapped[str | None] = mapped_column(String)
    client_type: Mapped[ClientType] = mapped_column(
        SAEnum(ClientType), nullable=False, default=ClientType.RECIPIENT
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="client")

    @property
    def display_name(self) -> str:
        if self.category == ClientCategory.COMPANY:
            return self.company_name or "Unnamed Company"
        else:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.display_name}')>"


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    product_index: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    unit: Mapped[ProductUnit] = mapped_column(SAEnum(ProductUnit), nullable=False)
    stock: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # --- ADD THIS LINE ---
    vat_rate: Mapped[float] = mapped_column(Float, nullable=False, default=23.0)

    def __repr__(self) -> str:
        return f"<Product(name='{self.name}')>"


class CompanyProfile(Base):
    __tablename__ = "company_profile"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str | None] = mapped_column(String)
    vat_id: Mapped[str | None] = mapped_column(String)
    address_street: Mapped[str | None] = mapped_column(String)
    address_zipcode: Mapped[str | None] = mapped_column(String)
    address_city: Mapped[str | None] = mapped_column(String)
    bank_account_number: Mapped[str | None] = mapped_column(String)
    additional_info: Mapped[str | None] = mapped_column(Text)
