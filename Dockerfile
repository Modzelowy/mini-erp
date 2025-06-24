FROM python:3.12-slim

WORKDIR /app


# Step 3: Install Poetry
RUN pip install poetry

# Step 4: Copy dependency files and install them, without installing the app code.
# This is an optimization - this step will only re-run if dependencies change.
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy the application code into the container's /app directory
COPY ./app /app

# Step 6: The command that will be executed when the container starts
CMD ["poetry", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
