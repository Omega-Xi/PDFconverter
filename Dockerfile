# Use an official Python runtime image
FROM python:3.10-slim

# Install system-level dependencies for Tesseract OCR AND OpenCV
#RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libgl1 && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy your application files into the container
COPY . .

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Specify the Tesseract command path for pytesseract
ENV TESSERACT_CMD="/usr/bin/tesseract"

# Expose the port your application will listen on (e.g., for a Flask app)
EXPOSE 80

# Define the command to start your application
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
