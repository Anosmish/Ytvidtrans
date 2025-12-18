# backend/Dockerfile

# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (Java for language-tool-python)
RUN apt-get update && \
    apt-get install -y default-jre wget git build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files into the container
COPY . .

# Expose port (Flask default or your app port)
EXPOSE 10000

# Run the app with Gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:10000"]
