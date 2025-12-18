# Use official Python slim image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y default-jre wget git maven unzip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend code
COPY backend/ .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install LanguageTool server using install.sh
RUN curl -L https://raw.githubusercontent.com/languagetool-org/languagetool/master/install.sh | bash -s -- -b

# Expose Flask app port
EXPOSE 10000

# Start Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
