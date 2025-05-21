FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for FAISS
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py app.py server.py ./

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV API_PORT=8000

# Expose port for the combined service
EXPOSE $PORT

# Command to run both services
CMD ["python", "server.py"]
