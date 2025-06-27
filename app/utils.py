# app/utils.py

from datetime import datetime

from jinja2 import Environment, FileSystemLoader

# Importujmy modele na górze, aby mypy był zadowolony
from models import Order, Product
from num2words import num2words
from sqlalchemy import func
from sqlalchemy.orm import Session
from weasyprint import HTML


def get_next_product_index(db: Session) -> int:
    """Finds the highest product_index and returns the next integer."""
    max_index = db.query(func.max(Product.product_index)).scalar()
    if max_index is None:
        return 1
    return max_index + 1


def get_next_invoice_number(db: Session) -> str:
    """
    Generates the next invoice number for the current month and year.
    Format: FV/Number/Month/Year
    """
    now = datetime.now()
    month = now.month
    year = now.year

    # Find the latest order with an invoice number from the current month and year
    last_invoice = (
        db.query(Order.invoice_number)
        .filter(
            Order.invoice_number.isnot(None),
            func.extract("year", Order.order_date) == year,
            func.extract("month", Order.order_date) == month,
        )
        .order_by(Order.id.desc())
        .first()
    )

    if last_invoice:
        # Extract number from e.g. "FV/12/6/2024" -> 12
        last_number_str = last_invoice[0].split("/")[1]
        next_number = int(last_number_str) + 1
    else:
        # It's the first invoice this month
        next_number = 1

    return f"FV/{next_number}/{month}/{year}"


def generate_invoice_pdf(order, company_profile, issued_document) -> bytes:
    """
    Generates a PDF invoice from an HTML template for a given order.
    """
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader("app/"))
    template = env.get_template("invoice_template.html")

    # Prepare data for the template
    total_net = sum(item.quantity * item.price_per_unit for item in order.items)
    total_vat = sum(
        item.quantity * item.price_per_unit * (item.vat_rate / 100)
        for item in order.items
    )
    total_gross = total_net + total_vat

    # Convert amount to words for the invoice
    integer_part = int(total_gross)
    fractional_part = round((total_gross % 1) * 100)
    total_in_words = (
        f"{num2words(integer_part, lang='pl')} złotych "
        f"{num2words(fractional_part, lang='pl')} groszy"
    )

    template_data = {
        "order": order,
        "company": company_profile,
        "doc": issued_document,
        "summary": {
            "total_net": total_net,
            "total_vat": total_vat,
            "total_gross": total_gross,
            "total_in_words": total_in_words.capitalize(),
        },
    }

    # Render the HTML template with data
    html_out = template.render(template_data)

    # Convert HTML to PDF using WeasyPrint
    pdf_bytes = HTML(string=html_out).write_pdf()

    return pdf_bytes
