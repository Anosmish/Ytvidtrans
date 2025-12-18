import os
import sys
import uuid
import asyncio
import logging
import threading
import time
import re
import json
from datetime import datetime
from typing import Dict, List

import edge_tts
import googletrans
import nltk
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add parent directory to path to access frontend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import Python-based grammar tools
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("TextBlob not available for grammar checking")

try:
    from autocorrect import Speller
    AUTOCORRECT_AVAILABLE = True
except ImportError:
    AUTOCORRECT_AVAILABLE = False
    print("Autocorrect not available")

try:
    from spellchecker import SpellChecker
    SPELLCHECKER_AVAILABLE = True
except ImportError:
    SPELLCHECKER_AVAILABLE = False
    print("SpellChecker not available")

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except:
        pass

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Initialize services
translator = googletrans.Translator()

# Initialize spell checkers
if AUTOCORRECT_AVAILABLE:
    autocorrect_speller = Speller()
if SPELLCHECKER_AVAILABLE:
    spell_checker = SpellChecker()

# Voice catalog
VOICE_CATALOG = {
    "english": [
        {"id": "en-US-JennyNeural", "name": "Jenny (Female)", "language": "English", "gender": "Female"},
        {"id": "en-US-GuyNeural", "name": "Guy (Male)", "language": "English", "gender": "Male"},
        {"id": "en-US-AriaNeural", "name": "Aria (Female)", "language": "English", "gender": "Female"}
    ],
    "spanish": [
        {"id": "es-ES-ElviraNeural", "name": "Elvira (Female)", "language": "Spanish", "gender": "Female"}
    ],
    "hindi": [
        {"id": "hi-IN-SwaraNeural", "name": "Swara (Female)", "language": "Hindi", "gender": "Female"}
    ],
    "french": [
        {"id": "fr-FR-DeniseNeural", "name": "Denise (Female)", "language": "French", "gender": "Female"}
    ],
    "german": [
        {"id": "de-DE-KatjaNeural", "name": "Katja (Female)", "language": "German", "gender": "Female"}
    ],
    "japanese": [
        {"id": "ja-JP-NanamiNeural", "name": "Nanami (Female)", "language": "Japanese", "gender": "Female"}
    ]
}

# ---------- HELPER FUNCTIONS ----------
def clamp(value: float, min_v: float, max_v: float) -> float:
    """Clamp value between min and max."""
    return max(min_v, min(value, max_v))

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
    """Check and correct spelling using available Python libraries."""
    original = text
    corrected = text
    suggestions = []
    
    try:
        # Use TextBlob if available
        if TEXTBLOB_AVAILABLE:
            blob = TextBlob(text)
            corrected = str(blob.correct())
            
            # Get suggestions for misspelled words
            for word in blob.words:
                if word.spellcheck()[0][1] < 0.8:  # Confidence threshold
                    suggestions.append({
                        'word': str(word),
                        'suggestions': [w[0] for w in word.spellcheck()[:3]]
                    })
        
        # Use autocorrect as fallback
        elif AUTOCORRECT_AVAILABLE and len(text.split()) < 100:
            corrected = autocorrect_speller(text)
        
        # Use pyspellchecker as another option
        elif SPELLCHECKER_AVAILABLE:
            words = text.split()
            misspelled = spell_checker.unknown(words)
            
            for word in misspelled:
                suggestions.append({
                    'word': word,
                    'suggestions': list(spell_checker.candidates(word))[:3]
                })
            
            # Auto-correct if requested
            if suggestions and len(words) < 50:
                corrected_words = []
                for word in words:
                    if word in misspelled:
                        corrected_words.append(spell_checker.correction(word))
                    else:
                        corrected_words.append(word)
                corrected = ' '.join(corrected_words)
        
        # Basic autocorrect using regex patterns
        else:
            # Common spelling corrections
            common_corrections = {
                r'\bteh\b': 'the',
                r'\badn\b': 'and',
                r'\bwhta\b': 'what',
                r'\bwhith\b': 'with',
                r'\brealy\b': 'really',
                r'\blike\b': 'like',
                r'\bthier\b': 'their',
                r'\byuo\b': 'you',
                r'\bcoudl\b': 'could',
                r'\bshoudl\b': 'should',
                r'\bwoudl\b': 'would',
            }
            
            for pattern, replacement in common_corrections.items():
                if re.search(pattern, text, re.IGNORECASE):
                    text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                    suggestions.append({
                        'pattern': pattern,
                        'replacement': replacement
                    })
            corrected = text
        
        return {
            'original': original,
            'corrected': corrected,
            'suggestions': suggestions,
            'total_suggestions': len(suggestions)
        }
        
    except Exception as e:
        return {
            'original': original,
            'corrected': original,
            'suggestions': [],
            'error': str(e),
            'total_suggestions': 0
        }

# ---------- API ENDPOINTS ----------
@app.route('/')
def serve_frontend():
    """Serve the frontend HTML file."""
    # Go up one level from backend to root, then to frontend
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'TTS API',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'spell_check': TEXTBLOB_AVAILABLE or AUTOCORRECT_AVAILABLE or SPELLCHECKER_AVAILABLE,
            'translation': True,
            'tts': True,
            'text_processing': True
        }
    })

@app.route('/api/voices', methods=['GET'])
def get_voices():
    return jsonify({
        'voices': VOICE_CATALOG,
        'total_count': sum(len(v) for v in VOICE_CATALOG.values())
    })

@app.route('/api/preprocess', methods=['POST'])
@limiter.limit("100 per hour")
def preprocess_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        options = data.get('options', {})
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        result = text_preprocessing(text, options)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spellcheck', methods=['POST'])
@limiter.limit("100 per hour")
def spellcheck_endpoint():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        result = spell_check_text(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
@limiter.limit("50 per hour")
def translate_endpoint():
    try:
        data = request.get_json()
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
            'pronunciation': getattr(translation, 'pronunciation', '')
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("50 per hour")
def analyze_text():
    try:
        data = request.get_json()
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
        
        return jsonify({
            'metrics': {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'character_count': char_count,
                'average_word_length': round(avg_word_length, 2),
                'average_sentence_length': round(avg_sentence_length, 2),
                'reading_time_minutes': round(reading_time, 1)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
@limiter.limit("30 per hour")
def generate_voice():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long (max 5000 characters)'}), 400
        
        voice = data.get('voice', 'en-US-JennyNeural')
        rate_val = clamp(int(data.get('rate', 0)), -100, 100)
        pitch_val = clamp(int(data.get('pitch', 0)), -100, 100)
        
        rate = f"{rate_val:+d}%"
        pitch = f"{pitch_val:+d}Hz"
        
        # Apply text processing if requested
        if data.get('preprocess', False):
            processed = text_preprocessing(text, data.get('processing_options', {}))
            text = processed['processed']
        
        # Apply spell check if requested
        if data.get('spell_check', False):
            spell_result = spell_check_text(text)
            text = spell_result['corrected']
        
        # Generate unique filename
        filename = f"temp_voice_{uuid.uuid4().hex}.mp3"
        
        # Generate voice asynchronously
        async def generate():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                pitch=pitch
            )
            await communicate.save(filename)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(generate())
        finally:
            loop.close()
        
        # Send file and schedule deletion
        response = send_file(
            filename,
            as_attachment=True,
            download_name=f"voice_{int(time.time())}.mp3",
            mimetype='audio/mpeg'
        )
        
        # Clean up file after sending
        def cleanup():
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except:
                pass
        
        threading.Timer(30, cleanup).start()
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files from frontend directory
@app.route('/<path:filename>')
def serve_static(filename):
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
    return send_from_directory(frontend_path, filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
