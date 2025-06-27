# app/utils.py (FINAL, SIMPLIFIED VERSION)

from datetime import datetime

from jinja2 import Environment, FileSystemLoader

# Import only the models we actually use in this file
from models import CompanyProfile, Order, Product
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
    """Generates the next invoice number for the current month and year."""
    now = datetime.now()
    month = now.month
    year = now.year

    # Find the latest order with an invoice number from the current month/year
    last_invoice_num = (
        db.query(Order.invoice_number)
        .filter(
            Order.invoice_number.isnot(None),
            func.extract("year", Order.order_date) == year,
            func.extract("month", Order.order_date) == month,
        )
        .order_by(Order.id.desc())
        .first()
    )

    if last_invoice_num:
        last_number = int(last_invoice_num[0].split("/")[1])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"FV/{next_number}/{month}/{year}"


def generate_invoice_pdf(order: Order, company: CompanyProfile) -> bytes:
    """Generates a PDF invoice from an HTML template for a given order."""
    env = Environment(loader=FileSystemLoader("app/"))
    template = env.get_template("invoice_template.html")

    total_net = sum(item.quantity * item.price_per_unit for item in order.items)
    total_vat = sum(
        item.quantity * item.price_per_unit * (item.vat_rate / 100)
        for item in order.items
    )
    total_gross = total_net + total_vat

    integer_part = int(total_gross)
    fractional_part = round((total_gross % 1) * 100)
    total_in_words = (
        f"{num2words(integer_part, lang='pl')} złotych "
        f"{num2words(fractional_part, lang='pl')} groszy"
    )

    template_data = {
        "order": order,
        "company": company,
        "summary": {
            "total_net": total_net,
            "total_vat": total_vat,
            "total_gross": total_gross,
            "total_in_words": total_in_words.capitalize(),
        },
    }

    html_out = template.render(template_data)
    pdf_bytes = HTML(string=html_out).write_pdf()

    return pdf_bytes
