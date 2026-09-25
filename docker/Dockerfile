# Multi-stage Dockerfile for YouTube Channel Growth Analysis Platform
FROM python:3.13-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run data quality tests to verify container integrity
RUN python -m pytest tests/

# Expose FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Entrypoint default command
CMD ["python", "run.py"]
