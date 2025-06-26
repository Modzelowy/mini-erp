# Dockerfile (FINAL, CORRECTED VERSION)

# Step 1: Base image
FROM python:3.12-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Install Poetry - system-level dependency
RUN pip install --no-cache-dir poetry

# Step 4: Copy only dependency configuration files
COPY poetry.lock pyproject.toml ./

# Step 5: Install project dependencies (without creating a venv)
# This is cached and will only re-run if poetry.lock/pyproject.toml change
RUN poetry config virtualenvs.create false && poetry install --no-root --without dev

# Step 6: Copy ALL required application assets and code
# This is the crucial fix. We copy assets first.
COPY ./assets ./assets
# Then, we copy the application source code.
COPY ./app .

# Step 7: The command to run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
