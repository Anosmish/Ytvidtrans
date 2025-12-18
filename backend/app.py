import os
import uuid
import asyncio
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import edge_tts
import googletrans
import language_tool_python
import nltk
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["200 per day", "50 per hour"]
)

# Configuration
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
    OUTPUT_DIR="outputs",
    UPLOAD_DIR="uploads",
    CACHE_DIR="cache",
    TEMP_DIR="temp"
)

# Create directories
for directory in [app.config['OUTPUT_DIR'], app.config['UPLOAD_DIR'], 
                  app.config['CACHE_DIR'], app.config['TEMP_DIR']]:
    os.makedirs(directory, exist_ok=True)

# Initialize services
translator = googletrans.Translator()
grammar_tool = language_tool_python.LanguageTool('en-US')

# Voice catalog
VOICE_CATALOG = {
    "english": {
        "en-US-JennyNeural": {"name": "Jenny (Female)", "language": "English", "gender": "Female"},
        "en-US-GuyNeural": {"name": "Guy (Male)", "language": "English", "gender": "Male"},
        "en-US-AriaNeural": {"name": "Aria (Female)", "language": "English", "gender": "Female"},
        "en-US-DavisNeural": {"name": "Davis (Male)", "language": "English", "gender": "Male"}
    },
    "spanish": {
        "es-ES-ElviraNeural": {"name": "Elvira (Female)", "language": "Spanish", "gender": "Female"},
        "es-ES-AlvaroNeural": {"name": "Alvaro (Male)", "language": "Spanish", "gender": "Male"}
    },
    "french": {
        "fr-FR-DeniseNeural": {"name": "Denise (Female)", "language": "French", "gender": "Female"},
        "fr-FR-HenriNeural": {"name": "Henri (Male)", "language": "French", "gender": "Male"}
    },
    "german": {
        "de-DE-KatjaNeural": {"name": "Katja (Female)", "language": "German", "gender": "Female"},
        "de-DE-ConradNeural": {"name": "Conrad (Male)", "language": "German", "gender": "Male"}
    },
    "hindi": {
        "hi-IN-SwaraNeural": {"name": "Swara (Female)", "language": "Hindi", "gender": "Female"},
        "hi-IN-MadhurNeural": {"name": "Madhur (Male)", "language": "Hindi", "gender": "Male"}
    },
    "japanese": {
        "ja-JP-NanamiNeural": {"name": "Nanami (Female)", "language": "Japanese", "gender": "Female"},
        "ja-JP-KeitaNeural": {"name": "Keita (Male)", "language": "Japanese", "gender": "Male"}
    },
    "chinese": {
        "zh-CN-XiaoxiaoNeural": {"name": "Xiaoxiao (Female)", "language": "Chinese", "gender": "Female"},
        "zh-CN-YunxiNeural": {"name": "Yunxi (Male)", "language": "Chinese", "gender": "Male"}
    },
    "arabic": {
        "ar-SA-ZariyahNeural": {"name": "Zariyah (Female)", "language": "Arabic", "gender": "Female"},
        "ar-SA-HamedNeural": {"name": "Hamed (Male)", "language": "Arabic", "gender": "Male"}
    },
    "russian": {
        "ru-RU-SvetlanaNeural": {"name": "Svetlana (Female)", "language": "Russian", "gender": "Female"},
        "ru-RU-DmitryNeural": {"name": "Dmitry (Male)", "language": "Russian", "gender": "Male"}
    }
}

# Language mapping for translation
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'hi': 'Hindi',
    'ja': 'Japanese',
    'zh-cn': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'ru': 'Russian',
    'pt': 'Portuguese',
    'it': 'Italian',
    'ko': 'Korean',
    'tr': 'Turkish',
    'nl': 'Dutch'
}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- HELPER FUNCTIONS ----------
def clamp(value: float, min_v: float, max_v: float) -> float:
    """Clamp value between min and max."""
    return max(min_v, min(value, max_v))

def cleanup_old_files(directory: str, max_age_hours: int = 1):
    """Clean up old files in directory."""
    try:
        now = time.time()
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_age = now - os.path.getmtime(filepath)
                if file_age > max_age_hours * 3600:
                    os.remove(filepath)
                    logger.info(f"Cleaned up old file: {filename}")
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")

def text_preprocessing(text: str, options: Dict) -> Dict:
    """Apply text preprocessing based on options."""
    result = {
        'original': text,
        'processed': text,
        'changes': []
    }
    
    # Convert to lowercase if requested
    if options.get('lowercase', False):
        result['processed'] = result['processed'].lower()
        result['changes'].append('Converted to lowercase')
    
    # Convert to uppercase if requested
    if options.get('uppercase', False):
        result['processed'] = result['processed'].upper()
        result['changes'].append('Converted to uppercase')
    
    # Remove extra whitespace
    if options.get('clean_spaces', True):
        import re
        result['processed'] = re.sub(r'\s+', ' ', result['processed']).strip()
        result['changes'].append('Cleaned extra spaces')
    
    # Remove special characters
    if options.get('remove_special', False):
        import re
        result['processed'] = re.sub(r'[^\w\s.,!?]', '', result['processed'])
        result['changes'].append('Removed special characters')
    
    # Sort lines
    sort_option = options.get('sort_option', 'none')
    if sort_option != 'none':
        lines = result['processed'].split('\n')
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
    
    # Capitalize sentences
    if options.get('capitalize_sentences', True):
        sentences = nltk.sent_tokenize(result['processed'])
        result['processed'] = ' '.join(s.capitalize() for s in sentences)
        result['changes'].append('Capitalized sentences')
    
    return result

def grammar_check_and_correct(text: str) -> Dict:
    """Check and correct grammar."""
    try:
        matches = grammar_tool.check(text)
        corrected = language_tool_python.utils.correct(text, matches)
        
        return {
            'original': text,
            'corrected': corrected,
            'errors_found': len(matches),
            'corrections': [{'message': m.message, 'replacements': m.replacements[:3]} for m in matches[:10]]
        }
    except Exception as e:
        logger.error(f"Grammar check error: {e}")
        return {
            'original': text,
            'corrected': text,
            'errors_found': 0,
            'corrections': []
        }

def translate_text(text: str, target_lang: str, source_lang: str = 'auto') -> Dict:
    """Translate text to target language."""
    try:
        translation = translator.translate(text, dest=target_lang, src=source_lang)
        
        return {
            'original': text,
            'translated': translation.text,
            'source_language': translation.src,
            'target_language': translation.dest,
            'pronunciation': getattr(translation, 'pronunciation', '')
        }
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return {
            'original': text,
            'translated': text,
            'source_language': source_lang,
            'target_language': target_lang,
            'error': str(e)
        }

async def generate_voice_async(text: str, voice: str, rate: str, pitch: str, volume: str, filename: str):
    """Generate voice asynchronously."""
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch
        )
        await communicate.save(filename)
        logger.info(f"Voice generated: {filename}")
    except Exception as e:
        logger.error(f"Voice generation error: {e}")
        raise

# ---------- BACKGROUND CLEANUP ----------
def start_cleanup_scheduler():
    """Start background thread for file cleanup."""
    def cleanup_job():
        while True:
            try:
                for directory in [app.config['OUTPUT_DIR'], app.config['UPLOAD_DIR'], 
                                 app.config['TEMP_DIR']]:
                    cleanup_old_files(directory, max_age_hours=1)
            except Exception as e:
                logger.error(f"Cleanup scheduler error: {e}")
            time.sleep(3600)  # Run every hour
    
    thread = threading.Thread(target=cleanup_job, daemon=True)
    thread.start()

# ---------- API ENDPOINTS ----------
@app.route('/')
def index():
    """Serve frontend."""
    return send_from_directory('.', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'TTS API'
    })

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """Get available voices."""
    try:
        return jsonify({
            'voices': VOICE_CATALOG,
            'total_count': sum(len(v) for v in VOICE_CATALOG.values())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get available languages for translation."""
    return jsonify({
        'languages': LANGUAGES,
        'total': len(LANGUAGES)
    })

@app.route('/api/preprocess', methods=['POST'])
@limiter.limit("100 per hour")
def preprocess_text():
    """Preprocess text with various options."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        options = data.get('options', {})
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        result = text_preprocessing(text, options)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Preprocessing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
@limiter.limit("50 per hour")
def translate_endpoint():
    """Translate text."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'en')
        source_lang = data.get('source_lang', 'auto')
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        result = translate_text(text, target_lang, source_lang)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Translation endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/grammar', methods=['POST'])
@limiter.limit("100 per hour")
def grammar_check():
    """Check and correct grammar."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        result = grammar_check_and_correct(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Grammar check endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
@limiter.limit("30 per hour")
def generate_voice():
    """Generate voice with all options."""
    try:
        data = request.get_json()
        
        # Extract parameters with defaults
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Voice settings
        voice = data.get('voice', 'en-US-JennyNeural')
        rate_val = clamp(int(data.get('rate', 0)), -100, 100)
        pitch_val = clamp(int(data.get('pitch', 0)), -100, 100)
        volume_val = clamp(int(data.get('volume', 0)), -50, 50)
        
        # Apply voice processing
        rate = f"{rate_val:+d}%"
        pitch = f"{pitch_val:+d}Hz"
        
        # Apply text processing if requested
        if data.get('preprocess', False):
            processed = text_preprocessing(text, data.get('processing_options', {}))
            text = processed['processed']
        
        # Apply grammar correction if requested
        if data.get('correct_grammar', False):
            grammar_result = grammar_check_and_correct(text)
            text = grammar_result['corrected']
        
        # Apply translation if requested
        if data.get('translate', False):
            target_lang = data.get('target_language', 'en')
            translation_result = translate_text(text, target_lang)
            text = translation_result['translated']
        
        # Generate unique filename
        filename = os.path.join(
            app.config['OUTPUT_DIR'],
            f"voice_{uuid.uuid4().hex}_{int(time.time())}.mp3"
        )
        
        # Generate voice asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                generate_voice_async(text, voice, rate, pitch, "+0%", filename)
            )
        finally:
            loop.close()
        
        # Return file with cleanup timer
        response = send_file(
            filename,
            as_attachment=True,
            download_name=f"generated_voice_{int(time.time())}.mp3",
            mimetype='audio/mpeg'
        )
        
        # Schedule cleanup after 10 minutes
        threading.Timer(600, lambda: os.remove(filename) if os.path.exists(filename) else None).start()
        
        return response
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Voice generation endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch', methods=['POST'])
@limiter.limit("10 per hour")
def batch_process():
    """Process multiple texts in batch."""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        options = data.get('options', {})
        
        if not texts or len(texts) > 10:
            return jsonify({'error': 'Please provide 1-10 texts'}), 400
        
        results = []
        for text in texts:
            if text.strip():
                result = text_preprocessing(text, options)
                results.append(result)
        
        return jsonify({
            'total_processed': len(results),
            'results': results
        })
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("50 per hour")
def analyze_text():
    """Analyze text complexity."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        # Basic text analysis
        words = text.split()
        sentences = nltk.sent_tokenize(text)
        
        # Calculate metrics
        word_count = len(words)
        sentence_count = len(sentences)
        char_count = len(text)
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Estimate reading time (assuming 200 words per minute)
        reading_time_minutes = word_count / 200
        
        # Complexity score (simple heuristic)
        complexity = min(100, (avg_word_length * 5) + (avg_sentence_length * 2))
        
        return jsonify({
            'metrics': {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'character_count': char_count,
                'average_word_length': round(avg_word_length, 2),
                'average_sentence_length': round(avg_sentence_length, 2),
                'estimated_reading_time_minutes': round(reading_time_minutes, 2),
                'complexity_score': round(complexity, 1)
            },
            'suggestions': get_suggestions_based_on_analysis(word_count, avg_sentence_length)
        })
        
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        return jsonify({'error': str(e)}), 500

def get_suggestions_based_on_analysis(word_count: int, avg_sentence_length: float) -> List[str]:
    """Get suggestions based on text analysis."""
    suggestions = []
    
    if avg_sentence_length > 25:
        suggestions.append("Consider breaking long sentences into shorter ones for better readability.")
    
    if word_count > 500:
        suggestions.append("Text is quite long. Consider splitting into paragraphs or sections.")
    
    if avg_sentence_length < 8:
        suggestions.append("Sentences are very short. Consider combining some for better flow.")
    
    if not suggestions:
        suggestions.append("Text has good readability. No major suggestions.")
    
    return suggestions

# ---------- ERROR HANDLERS ----------
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ---------- STARTUP ----------
if __name__ == '__main__':
    # Start cleanup scheduler
    start_cleanup_scheduler()
    
    # Log startup
    logger.info("Starting TTS Service...")
    logger.info(f"Output directory: {app.config['OUTPUT_DIR']}")
    
    # Run app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    )
