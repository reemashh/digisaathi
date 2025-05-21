FROM python:3.9-slim

# Install system deps for faiss (Debian based)
RUN apt-get update && apt-get install -y build-essential cmake

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Run the app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

