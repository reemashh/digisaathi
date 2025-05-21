# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port available to the world outside this container
EXPOSE 8000
EXPOSE 8501

# Define environment variables with defaults
ENV API_PORT=8000
ENV PORT=8501
# HF_API_TOKEN should be set through Render's environment variables
# ENV HF_API_TOKEN=""

# Run server.py when the container launches
CMD ["python", "server.py"]
