# Mini ERP with Streamlit and Docker

A simple, containerized web application for managing clients, products, and orders, built with Streamlit, SQLAlchemy, and PostgreSQL.

## ✨ Key Features

- **Client Management**: Add new clients (suppliers/recipients) and view the existing client list.
- **Product Database**: Manage a list of products, including their names, unique indexes, and units.
- **Order Management**:
    - Create new orders for clients.
    - Add multiple products to an order using an interactive shopping cart.
    - View a list of all past orders with detailed item breakdowns and total values.
- **Intuitive UI**: A clean and user-friendly interface built with [Streamlit](https://streamlit.io/).
- **Containerized**: Fully containerized with Docker and Docker Compose for easy setup and deployment.
- **Persistent Data**: Uses a PostgreSQL database with a persistent volume to ensure your data is saved across container restarts.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend/ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Data Handling**: Pandas
- **Containerization**: Docker & Docker Compose
- **Dependency Management**: Poetry

## 🚀 How to Run

This project is designed to be run with Docker. Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your system.

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd mini-erp
    ```

2.  **Run the application:**
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker image for the application and start both the Streamlit app and the PostgreSQL database containers.

3.  **Access the application:**
    Open your web browser and navigate to:
    [http://localhost:8501](http://localhost:8501)

## ⚙️ Configuration

The application is configured using environment variables, which are defined in the `docker-compose.yml` file. You can customize the database credentials there if needed.

- `POSTGRES_USER`: The username for the database.
- `POSTGRES_PASSWORD`: The password for the database.
- `POSTGRES_DB`: The name of the database.
- `POSTGRES_HOST`: The hostname of the database service (should be `db` as defined in `docker-compose.yml`).
