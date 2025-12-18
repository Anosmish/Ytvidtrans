import os
import uuid
import re
import json
import tempfile
import time
from datetime import datetime
from typing import Dict, List
from io import BytesIO

import pyttsx3
import googletrans
import nltk
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Try to import Python-based grammar tools
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("TextBlob not available")

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

# Initialize services
translator = googletrans.Translator()

# Initialize spell checkers
if AUTOCORRECT_AVAILABLE:
    autocorrect_speller = Speller()
if SPELLCHECKER_AVAILABLE:
    spell_checker = SpellChecker()

# Initialize pyttsx3 engine (global for better performance)
try:
    tts_engine = pyttsx3.init()
    # Configure default voice properties
    tts_engine.setProperty('rate', 150)  # Normal speech rate
    tts_engine.setProperty('volume', 1.0)  # Maximum volume
    TTS_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not initialize TTS engine: {e}")
    TTS_AVAILABLE = False

# Voice catalog for Web Speech API (browser-native voices)
VOICE_CATALOG = {
    "system": [
        {"id": "default", "name": "System Default", "language": "Auto", "gender": "Auto"},
    ],
    "languages": [
        {"code": "en-US", "name": "English (US)", "voices": ["default"]},
        {"code": "en-GB", "name": "English (UK)", "voices": ["default"]},
        {"code": "es-ES", "name": "Spanish", "voices": ["default"]},
        {"code": "fr-FR", "name": "French", "voices": ["default"]},
        {"code": "de-DE", "name": "German", "voices": ["default"]},
        {"code": "hi-IN", "name": "Hindi", "voices": ["default"]},
        {"code": "ja-JP", "name": "Japanese", "voices": ["default"]}
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
    
    # Sort lines
    sort_option = options.get('sort_option', 'none')
    if sort_option != 'none':
        lines = [line for line in result['processed'].split('\n') if line.strip()]
        if sort_option == 'alphabetical':
            lines.sort()
            result['changes'].append('Sorted alphabetically')
        elif sort_option == 'reverse':
            lines = list(reversed(lines))
            result['changes'].append('Reversed order')
        elif sort_option == 'length':
            lines.sort(key=len)
            result['changes'].append('Sorted by length')
        result['processed'] = '\n'.join(lines)
    
    # Remove duplicate lines
    if options.get('remove_duplicates', False):
        lines = result['processed'].split('\n')
        unique_lines = []
        seen = set()
        for line in lines:
            if line.strip() and line not in seen:
                seen.add(line)
                unique_lines.append(line)
        result['processed'] = '\n'.join(unique_lines)
        result['changes'].append('Removed duplicate lines')
    
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
                if word.spellcheck()[0][1] < 0.8:
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

def generate_tts_mp3(text: str, rate: int = 150, volume: float = 1.0, voice: str = None):
    """Generate MP3 from text using pyttsx3."""
    try:
        if not TTS_AVAILABLE:
            raise Exception("TTS engine not available")
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Configure engine
        engine = pyttsx3.init()
        
        # Set properties
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        
        # Set voice if specified
        if voice:
            voices = engine.getProperty('voices')
            if voice.lower() == 'female':
                # Try to find a female voice
                for v in voices:
                    if 'female' in v.name.lower() or 'woman' in v.name.lower():
                        engine.setProperty('voice', v.id)
                        break
            elif voice.lower() == 'male':
                # Try to find a male voice
                for v in voices:
                    if 'male' in v.name.lower() or 'man' in v.name.lower():
                        engine.setProperty('voice', v.id)
                        break
        
        # Save to file
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        
        # Read the file
        with open(temp_path, 'rb') as f:
            audio_data = f.read()
        
        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass
        
        return audio_data
        
    except Exception as e:
        print(f"TTS generation error: {e}")
        raise

# ---------- API ENDPOINTS ----------
@app.route('/')
def home():
    """Home route - show API info."""
    return jsonify({
        'message': 'Text Processing & TTS API',
        'status': 'running',
        'frontend': 'https://ytvidtrans.netlify.app',
        'api_docs': 'Use /api/* endpoints',
        'features': ['tts_mp3', 'translation', 'spell_check', 'text_processing']
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Text Processing & TTS API',
        'timestamp': datetime.now().isoformat(),
        'backend_url': 'https://ytvidtrans.onrender.com',
        'frontend_url': 'https://ytvidtrans.netlify.app',
        'features': {
            'spell_check': TEXTBLOB_AVAILABLE or AUTOCORRECT_AVAILABLE or SPELLCHECKER_AVAILABLE,
            'translation': True,
            'tts_mp3': TTS_AVAILABLE,
            'text_processing': True
        }
    })

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """Return voice information."""
    voices_info = []
    
    if TTS_AVAILABLE:
        try:
            engine = pyttsx3.init()
            system_voices = engine.getProperty('voices')
            for voice in system_voices[:5]:  # Limit to 5 voices
                voices_info.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': 'Male' if 'male' in voice.name.lower() else 'Female' if 'female' in voice.name.lower() else 'Unknown'
                })
        except:
            pass
    
    return jsonify({
        'system_voices': voices_info,
        'tts_engine': 'pyttsx3' if TTS_AVAILABLE else 'unavailable',
        'note': 'MP3 generation available via /api/tts-mp3 endpoint',
        'browser_tts': 'Use Web Speech API for instant playback'
    })

@app.route('/api/preprocess', methods=['POST'])
@limiter.limit("200 per hour")
def preprocess_text():
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

@app.route('/api/batch', methods=['POST'])
@limiter.limit("50 per hour")
def batch_process():
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        options = data.get('options', {})
        
        if not texts or len(texts) > 10:
            return jsonify({'error': 'Please provide 1-10 texts'}), 400
        
        results = []
        for text in texts:
            if text and text.strip():
                result = text_preprocessing(text, options)
                results.append(result)
        
        return jsonify({
            'total_processed': len(results),
            'results': results,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tts-mp3', methods=['POST'])
@limiter.limit("50 per hour")
def tts_mp3():
    """Generate MP3 using pyttsx3."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '').strip()
        rate = data.get('rate', 150)
        volume = data.get('volume', 1.0)
        voice = data.get('voice', None)
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text) > 2000:
            return jsonify({'error': 'Text too long (max 2000 characters)'}), 400
        
        if not TTS_AVAILABLE:
            return jsonify({'error': 'TTS service unavailable'}), 503
        
        # Clamp values
        rate = clamp(rate, 50, 300)
        volume = clamp(volume, 0.1, 1.0)
        
        # Apply text processing if requested
        if data.get('preprocess', False):
            processed = text_preprocessing(text, data.get('processing_options', {}))
            text = processed['processed']
        
        # Apply spell check if requested
        if data.get('spell_check', False):
            spell_result = spell_check_text(text)
            text = spell_result['corrected']
        
        # Generate MP3
        audio_data = generate_tts_mp3(text, rate, volume, voice)
        
        # Return as downloadable file
        return send_file(
            BytesIO(audio_data),
            as_attachment=True,
            download_name=f"speech_{int(time.time())}.mp3",
            mimetype='audio/mpeg'
        )
        
    except Exception as e:
        print(f"TTS MP3 error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tts-info', methods=['GET'])
def tts_info():
    """Get TTS engine information."""
    info = {
        'engine': 'pyttsx3',
        'available': TTS_AVAILABLE,
        'max_chars': 2000,
        'rate_range': {'min': 50, 'max': 300, 'default': 150},
        'volume_range': {'min': 0.1, 'max': 1.0, 'default': 1.0},
        'supported_formats': ['mp3'],
        'rate_limit': '50 requests per hour'
    }
    
    if TTS_AVAILABLE:
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            info['available_voices'] = len(voices)
            info['sample_voices'] = [v.name for v in voices[:3]]
        except:
            pass
    
    return jsonify(info)

# CORS preflight requests
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', 'https://ytvidtrans.netlify.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response, 200

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    """Add CORS headers to all responses."""
    response.headers.add('Access-Control-Allow-Origin', 'https://ytvidtrans.netlify.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

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
