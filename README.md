# Mini ERP with Streamlit and Docker

A comprehensive web-based Enterprise Resource Planning (ERP) system built with Streamlit, SQLAlchemy, and PostgreSQL, designed to manage company operations including client management, product catalog, order processing, and professional invoicing.

## ✨ Key Features

### Company Profile
- Manage company details (name, address, VAT ID)
- Configure bank account information
- Centralized company settings for professional invoicing

### Client Management
- Support for both companies and individuals
- VAT ID validation
- Track client interactions and order history
- Advanced search and filtering capabilities

### Product Database
- Comprehensive product catalog with unique indexes/SKUs
- Multiple unit types support (pcs, kg, set, m)
- Automatic product index generation
- Configurable VAT rates (23%, 8%, 5%, 0%)

### Order & Invoice Management
- Intuitive order creation with shopping cart interface
- Automatic invoice number generation (FV/Number/Month/Year)
- Professional PDF invoice generation with company branding
- Multiple payment methods (Bank Transfer, Cash, Card)
- Payment status tracking (Paid/Unpaid/Overdue)
- Automatic calculation of payment due dates
- Support for both gross and net pricing

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.12
- **Database**: PostgreSQL with SQLAlchemy ORM
- **PDF Generation**: WeasyPrint
- **Containerization**: Docker & Docker Compose
- **Dependency Management**: Poetry
- **Code Quality**: pre-commit, mypy, ruff, black
- **Testing**: pytest

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.12 (for development)
- Poetry (for dependency management)

### Running with Docker (Recommended)

```bash
git clone <your-repo-url>
cd mini-erp
docker-compose up --build
```

The application will be available at: `http://localhost:8501`

### Local Development

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

3. **Run the application:**
   ```bash
   poetry run streamlit run app/main.py
   ```

## 📂 Project Structure

```
mini-erp/
├── app/                     # Main application package
│   ├── pages/               # Streamlit page modules
│   │   ├── 1_Company_Profile.py
│   │   ├── 2_Client_Management.py
│   │   ├── 3_Product_Database.py
│   │   └── 4_Orders.py      # Order and invoice management
│   ├── __init__.py
│   ├── database.py          # Database connection and session management
│   ├── invoice_template.html # Professional HTML template for invoices
│   ├── main.py              # Main Streamlit application
│   ├── models.py            # SQLAlchemy models
│   ├── style_loader.py      # CSS styling utilities
│   └── utils.py             # Utility functions including invoice generation
├── assets/                  # Static assets (CSS, images, fonts)
│   └── DejaVuSans.ttf      # Font for PDF generation
├── tests/                   # Test files
│   ├── __pycache__/
│   ├── test_models.py
│   └── test_utils.py
├── .pre-commit-config.yaml  # pre-commit hooks configuration
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Dockerfile for the application
├── poetry.lock             # Poetry lock file
└── pyproject.toml          # Project metadata and dependencies
```

## 🧪 Testing

Run tests using pytest:
```bash
poetry run pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Lezdom
