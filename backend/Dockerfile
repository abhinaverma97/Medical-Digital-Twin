# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for some Python packages like psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file explicitly
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code, scripts, documents, and .env
# We copy the entire project into /app so that paths like backend/app/... work
COPY . .

# Expose the API port
EXPOSE 8000

# Set PYTHONPATH so that absolute imports (e.g., from backend.app.api import ...) work
ENV PYTHONPATH="/"

# Start the application using Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
