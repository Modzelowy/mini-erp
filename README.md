# Mini ERP with Streamlit and Docker

A comprehensive web-based Enterprise Resource Planning (ERP) system built with Streamlit, SQLAlchemy, and PostgreSQL, designed to manage company operations including client management, product catalog, and order processing.

## ✨ Key Features

### Company Profile
- Manage your company's profile information
- Centralized company details management

### Client Management
- Add and manage clients (suppliers/recipients)
- View and search through client database
- Track client interactions and history

### Product Database
- Comprehensive product catalog management
- Track products with unique indexes and units
- Categorize and organize products efficiently

### Order Management
- Create and manage sales/purchase orders
- Interactive shopping cart for order assembly
- View order history with detailed breakdowns
- Calculate order totals and track order status

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.10+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Data Handling**: Pandas for data manipulation
- **Containerization**: Docker & Docker Compose
- **Dependency Management**: Poetry
- **Code Quality**: pre-commit hooks, mypy, ruff, black
- **Testing**: pytest

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose installed on your system
- Python 3.10+ (for local development)
- Poetry (for dependency management)

### Running with Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd mini-erp
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```
   This will build the Docker image and start both the Streamlit app and PostgreSQL database containers.

3. **Access the application:**
   Open your web browser and navigate to:
   ```
   http://localhost:8501
   ```

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

## ⚙️ Configuration

The application is configured using environment variables, which can be set in the `docker-compose.yml` file or in a `.env` file.

### Environment Variables

- `POSTGRES_USER`: Database username (default: `postgres`)
- `POSTGRES_PASSWORD`: Database password (default: `postgres`)
- `POSTGRES_DB`: Database name (default: `erp_db`)
- `POSTGRES_HOST`: Database host (default: `db`)
- `STREAMLIT_SERVER_PORT`: Port to run the Streamlit app (default: `8501`)

## 📂 Project Structure

```
mini-erp/
├── app/                     # Main application package
│   ├── pages/               # Streamlit page modules
│   │   ├── 1_Company_Profile.py
│   │   ├── 2_Client_Management.py
│   │   ├── 3_Product_Database.py
│   │   └── 4_Orders.py
│   ├── __init__.py
│   ├── database.py          # Database connection and session management
│   ├── main.py              # Main Streamlit application
│   ├── models.py            # SQLAlchemy models
│   └── style_loader.py      # CSS styling utilities
├── assets/                  # Static assets (CSS, images, etc.)
├── tests/                   # Test files
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
