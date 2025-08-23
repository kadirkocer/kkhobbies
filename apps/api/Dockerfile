FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/data /app/uploads

# Initialize database on startup
CMD ["sh", "-c", "python -m app.cli init && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

EXPOSE 8000