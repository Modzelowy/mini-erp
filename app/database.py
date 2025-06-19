# app/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Database Configuration from Environment Variables ---
# It's best practice to load sensitive data like this from the environment
# rather than hardcoding it. This makes the app more secure and portable.

# We provide default values that match the docker-compose setup for easy local development.
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "erp_db")

# The connection string for our PostgreSQL database.
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# The engine is the entry point to the database.
engine = create_engine(DATABASE_URL)

# A sessionmaker object is a factory for creating new Session objects.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our declarative models. All our models will inherit from this.
Base = declarative_base()