#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install system dependencies (for pyttsx3)
sudo apt-get update && sudo apt-get install -y espeak ffmpeg

# Install Python dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt', quiet=True); print('✓ NLTK data downloaded')"

# Test imports
python -c "import flask; print('✓ Flask version:', flask.__version__)"
python -c "import googletrans; print('✓ Googletrans imported')"
python -c "import pyttsx3; print('✓ Pyttsx3 version:', pyttsx3.__version__)"
python -c "engine = pyttsx3.init(); voices = engine.getProperty('voices'); print(f'✓ Found {len(voices)} TTS voices')"

# Create temp directory
mkdir -p temp_audio
echo "✓ Build completed successfully"
