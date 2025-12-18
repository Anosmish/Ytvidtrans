# Base image with Python 3.9
FROM python:3.9-slim

# Install Java (default JRE) and other required tools
RUN apt-get update && \
    apt-get install -y default-jre wget git build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of your backend code
COPY backend/ .

# Expose the port that Render will use
EXPOSE 10000

# Run Gunicorn to serve the app
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:10000"]

