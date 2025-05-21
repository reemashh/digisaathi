# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files into the container
COPY . .

# Create .streamlit/config.toml inside container
RUN mkdir -p ~/.streamlit && \
    echo "[server]\n\
headless = true\n\
port = 10000\n\
enableCORS = false\n\
\n" > ~/.streamlit/config.toml

# Expose the port Render expects
EXPOSE 10000

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]

