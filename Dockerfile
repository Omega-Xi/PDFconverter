# Use official Python base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Environment variable for Flask
ENV FLASK_ENV=production

# Start the app using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
