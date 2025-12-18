import os
import re
import json
from datetime import datetime
from typing import Dict

import googletrans
import nltk
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for Netlify frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://ytvidtrans.netlify.app",
            "http://localhost:5500",
            "http://localhost:3000",
            "http://127.0.0.1:5500",
            "http://127.0.0.1:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://",
)

# Initialize translator
translator = googletrans.Translator()

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except:
        pass

# ---------- HELPER FUNCTIONS ----------
def text_preprocessing(text: str, options: Dict) -> Dict:
    """Apply text preprocessing based on options."""
    result = {
        'original': text,
        'processed': text,
        'changes': []
    }
    
    # Clean extra spaces
    if options.get('clean_spaces', True):
        result['processed'] = re.sub(r'\s+', ' ', result['processed']).strip()
        result['changes'].append('Cleaned extra spaces')
    
    # Convert to lowercase
    if options.get('lowercase', False):
        result['processed'] = result['processed'].lower()
        result['changes'].append('Converted to lowercase')
    
    # Convert to uppercase
    if options.get('uppercase', False):
        result['processed'] = result['processed'].upper()
        result['changes'].append('Converted to uppercase')
    
    # Title case
    if options.get('titlecase', False):
        result['processed'] = result['processed'].title()
        result['changes'].append('Converted to title case')
    
    # Capitalize sentences
    if options.get('capitalize_sentences', True):
        try:
            sentences = nltk.sent_tokenize(result['processed'])
            result['processed'] = ' '.join(s.capitalize() for s in sentences)
            result['changes'].append('Capitalized sentences')
        except:
            pass
    
    # Remove special characters
    if options.get('remove_special', False):
        result['processed'] = re.sub(r'[^\w\s.,!?]', '', result['processed'])
        result['changes'].append('Removed special characters')
    
    return result

def spell_check_text(text: str) -> Dict:
    """Basic spell checking using pattern matching."""
    original = text
    corrected = text
    suggestions = []
    
    # Simple common misspellings correction
    common_corrections = {
        'teh': 'the',
        'adn': 'and',
        'thier': 'their',
        'recieve': 'receive',
        'seperate': 'separate',
        'occured': 'occurred',
        'definately': 'definitely',
        'goverment': 'government',
        'seperate': 'separate'
    }
    
    words = text.split()
    corrected_words = []
    
    for word in words:
        lower_word = word.lower()
        if lower_word in common_corrections:
            suggestions.append({
                'word': word,
                'suggestions': [common_corrections[lower_word]]
            })
            corrected_words.append(common_corrections[lower_word])
        else:
            corrected_words.append(word)
    
    corrected = ' '.join(corrected_words)
    
    return {
        'original': original,
        'corrected': corrected,
        'suggestions': suggestions,
        'total_suggestions': len(suggestions)
    }

# ---------- API ENDPOINTS ----------
@app.route('/')
def home():
    """Home route - show API info."""
    return jsonify({
        'message': 'Text Processing API',
        'status': 'running',
        'frontend': 'https://ytvidtrans.netlify.app',
        'api_docs': 'Use /api/* endpoints',
        'features': ['translation', 'spell_check', 'text_processing', 'analysis'],
        'tts_note': 'TTS is browser-based using Web Speech API'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Text Processing API',
        'timestamp': datetime.now().isoformat(),
        'backend_url': 'https://ytvidtrans.onrender.com',
        'frontend_url': 'https://ytvidtrans.netlify.app',
        'features': {
            'spell_check': True,
            'translation': True,
            'text_processing': True,
            'analysis': True,
            'tts_mp3': False,  # No server-side TTS
            'tts_browser': True  # Browser-based TTS available
        },
        'tts_info': 'TTS is browser-based only using Web Speech API. No server-side TTS available.'
    })

@app.route('/api/tts-info', methods=['GET'])
def tts_info():
    """TTS information endpoint."""
    return jsonify({
        'available': False,
        'engine': 'none',
        'message': 'TTS is browser-based only using Web Speech API',
        'browser_requirements': {
            'supported': ['Chrome 33+', 'Edge 14+', 'Safari 7+', 'Firefox 49+'],
            'mobile_support': ['iOS Safari 7+', 'Android Chrome 33+'],
            'api': 'window.speechSynthesis'
        },
        'limitations': {
            'max_chars': 'Unlimited (browser-dependent)',
            'download_mp3': 'Not available (browser limitation)',
            'voice_selection': 'Browser system voices only'
        },
        'implementation': 'Use window.speechSynthesis in JavaScript'
    })

@app.route('/api/preprocess', methods=['POST'])
@limiter.limit("200 per hour")
def preprocess_text():
    """Text preprocessing endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '')
        options = data.get('options', {})
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        result = text_preprocessing(text, options)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spellcheck', methods=['POST'])
@limiter.limit("200 per hour")
def spellcheck_endpoint():
    """Spell checking endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '')
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        result = spell_check_text(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
@limiter.limit("100 per hour")
def translate_endpoint():
    """Translation endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'en')
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        translation = translator.translate(text, dest=target_lang)
        result = {
            'original': text,
            'translated': translation.text,
            'source_language': translation.src,
            'target_language': translation.dest,
            'pronunciation': getattr(translation, 'pronunciation', ''),
            'status': 'success'
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("100 per hour")
def analyze_text():
    """Text analysis endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '')
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        # Basic text analysis
        words = text.split()
        sentences = nltk.sent_tokenize(text) if text else []
        
        word_count = len(words)
        sentence_count = len(sentences)
        char_count = len(text)
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Reading time
        reading_time = word_count / 200
        
        # Calculate readability (simplified Flesch)
        readability = 0
        if word_count > 0 and sentence_count > 0:
            readability = max(0, min(100, 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (avg_word_length / 4)))
        
        return jsonify({
            'metrics': {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'character_count': char_count,
                'average_word_length': round(avg_word_length, 2),
                'average_sentence_length': round(avg_sentence_length, 2),
                'reading_time_minutes': round(reading_time, 1),
                'readability_score': round(readability, 1)
            },
            'readability': get_readability_level(readability),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_readability_level(score):
    """Get readability level based on Flesch score."""
    if score >= 90:
        return "Very Easy (5th grade)"
    elif score >= 80:
        return "Easy (6th grade)"
    elif score >= 70:
        return "Fairly Easy (7th grade)"
    elif score >= 60:
        return "Standard (8th-9th grade)"
    elif score >= 50:
        return "Fairly Difficult (10th-12th grade)"
    elif score >= 30:
        return "Difficult (College level)"
    else:
        return "Very Difficult (College graduate)"

# Error handlers
@app.errorhandler(404)
def not_found(error):
    response = jsonify({'error': 'Endpoint not found'})
    response.status_code = 404
    return response

@app.errorhandler(429)
def ratelimit_handler(e):
    response = jsonify({'error': 'Rate limit exceeded. Please try again later.'})
    response.status_code = 429
    return response

@app.errorhandler(500)
def internal_error(error):
    response = jsonify({'error': 'Internal server error'})
    response.status_code = 500
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
