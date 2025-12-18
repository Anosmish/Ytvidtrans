#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip to latest version
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt', quiet=True); print('NLTK data downloaded successfully')"

# Create necessary directories
mkdir -p temp_outputs
