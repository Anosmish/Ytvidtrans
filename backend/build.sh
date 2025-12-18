#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt', quiet=True); print('✓ NLTK data downloaded')"

# Test Edge TTS installation
python -c "import edge_tts; print('✓ Edge TTS version:', edge_tts.__version__)"
