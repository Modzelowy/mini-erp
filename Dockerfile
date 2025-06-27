# Dockerfile (FINAL VERSION WITH SYSTEM DEPENDENCIES FOR PDF)

FROM python:3.12-slim

# Step 1: Install system dependencies required by WeasyPrint for PDF generation
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-cffi \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --no-root --without dev

COPY ./assets ./assets
COPY ./app .

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
