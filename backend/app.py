import os
import uuid
import asyncio
import logging
import threading
import time
import re
from datetime import datetime
from typing import Dict, List, Optional

import edge_tts
import googletrans
import nltk
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

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
if TEXTBLOB_AVAILABLE:
    textblob_speller = TextBlob("")
if AUTOCORRECT_AVAILABLE:
    autocorrect_speller = Speller()
if SPELLCHECKER_AVAILABLE:
    spell_checker = SpellChecker()

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
    "hindi": {
        "hi-IN-SwaraNeural": {"name": "Swara (Female)", "language": "Hindi", "gender": "Female"},
        "hi-IN-MadhurNeural": {"name": "Madhur (Male)", "language": "Hindi", "gender": "Male"}
    },
    "japanese": {
        "ja-JP-NanamiNeural": {"name": "Nanami (Female)", "language": "Japanese", "gender": "Female"},
        "ja-JP-KeitaNeural": {"name": "Keita (Male)", "language": "Japanese", "gender": "Male"}
    },
    "french": {
        "fr-FR-DeniseNeural": {"name": "Denise (Female)", "language": "French", "gender": "Female"},
        "fr-FR-HenriNeural": {"name": "Henri (Male)", "language": "French", "gender": "Male"}
    },
    "german": {
        "de-DE-KatjaNeural": {"name": "Katja (Female)", "language": "German", "gender": "Female"},
        "de-DE-ConradNeural": {"name": "Conrad (Male)", "language": "German", "gender": "Male"}
    }
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
                if word.spellcheck()[0][1] < 0.8:  # Confidence threshold
                    suggestions.append({
                        'word': str(word),
                        'suggestions': [w[0] for w in word.spellcheck()[:3]]
                    })
        
        # Use autocorrect as fallback
        elif AUTOCORRECT_AVAILABLE and len(text.split()) < 100:  # Limit for performance
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

def grammar_check_basic(text: str) -> Dict:
    """Basic grammar checking using regex patterns."""
    original = text
    corrected = text
    issues = []
    
    # Common grammar patterns to check
    grammar_patterns = [
        # a vs an
        (r'\ba [aeiouAEIOU][a-z]*\b', 'Should use "an" before vowel sounds', 
         lambda m: f"an {m.group(0)[2:]}" if len(m.group(0)) > 2 else "an"),
        
        # your vs you're
        (r'\byour (am|are|is|was|were|being|been)\b', 'Should be "you\'re"', 
         lambda m: f"you're {m.group(1)}"),
        
        # its vs it's
        (r'\bits (is|was|has)\b', 'Should be "it\'s"', 
         lambda m: f"it's {m.group(1)}"),
        
        # their vs they're vs there
        (r'\btheir (am|are|is|was|were)\b', 'Should be "they\'re"', 
         lambda m: f"they're {m.group(1)}"),
        
        # Double words
        (r'\b(\w+) \1\b', 'Repeated word', 
         lambda m: m.group(1)),
        
        # Missing apostrophe in contractions
        (r'\b(cant|dont|wont|isnt|arent|wasnt|werent|hasnt|havent|hadnt|doesnt|didnt)\b',
         'Missing apostrophe in contraction',
         lambda m: {
             'cant': "can't", 'dont': "don't", 'wont': "won't",
             'isnt': "isn't", 'arent': "aren't", 'wasnt': "wasn't",
             'werent': "weren't", 'hasnt': "hasn't", 'havent': "haven't",
             'hadnt': "hadn't", 'doesnt': "doesn't", 'didnt': "didn't"
         }.get(m.group(1).lower(), m.group(1))),
        
        # Capitalize first word of sentence
        (r'(?:^|\.\s+)([a-z])', 'Sentence should start with capital letter',
         lambda m: m.group(0).upper()),
    ]
    
    for pattern, message, correction_func in grammar_patterns:
        matches = list(re.finditer(pattern, corrected, re.IGNORECASE))
        for match in matches:
            issues.append({
                'position': match.start(),
                'message': message,
                'matched_text': match.group(0),
                'suggestion': correction_func(match)
            })
    
    # Apply corrections
    if issues:
        # Sort issues by position in reverse to avoid position shifts
        issues.sort(key=lambda x: x['position'], reverse=True)
        
        text_list = list(corrected)
        for issue in issues:
            if 'suggestion' in issue and isinstance(issue['suggestion'], str):
                start = issue['position']
                end = start + len(issue['matched_text'])
                text_list[start:end] = issue['suggestion']
        
        corrected = ''.join(text_list)
    
    return {
        'original': original,
        'corrected': corrected,
        'issues': issues,
        'total_issues': len(issues)
    }

def translate_text(text: str, target_lang: str) -> Dict:
    """Translate text to target language."""
    try:
        translation = translator.translate(text, dest=target_lang)
        return {
            'original': text,
            'translated': translation.text,
            'source_language': translation.src,
            'target_language': translation.dest,
            'pronunciation': getattr(translation, 'pronunciation', '')
        }
    except Exception as e:
        return {
            'original': text,
            'translated': text,
            'error': str(e)
        }

# ---------- API ENDPOINTS ----------
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

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

@app.route('/api/grammar', methods=['POST'])
@limiter.limit("100 per hour")
def grammar_check():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        
        # First spell check
        spell_result = spell_check_text(text)
        
        # Then basic grammar check
        grammar_result = grammar_check_basic(spell_result['corrected'])
        
        # Combine results
        result = {
            'original': text,
            'corrected': grammar_result['corrected'],
            'spell_suggestions': spell_result.get('suggestions', []),
            'grammar_issues': grammar_result.get('issues', []),
            'total_spelling_suggestions': spell_result.get('total_suggestions', 0),
            'total_grammar_issues': grammar_result.get('total_issues', 0),
            'total_issues': spell_result.get('total_suggestions', 0) + grammar_result.get('total_issues', 0)
        }
        
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
        
        result = translate_text(text, target_lang)
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
        
        # Reading level (Flesch Reading Ease approximation)
        readability_score = 0
        if word_count > 0 and sentence_count > 0:
            # Simplified Flesch Reading Ease
            readability_score = max(0, min(100, 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (avg_word_length / 4)))
        
        return jsonify({
            'metrics': {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'character_count': char_count,
                'average_word_length': round(avg_word_length, 2),
                'average_sentence_length': round(avg_sentence_length, 2),
                'reading_time_minutes': round(word_count / 200, 1),
                'readability_score': round(readability_score, 1)
            },
            'readability_level': get_readability_level(readability_score)
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
        
        # Apply grammar check if requested
        if data.get('grammar_check', False):
            grammar_result = grammar_check_basic(text)
            text = grammar_result['corrected']
        
        # Apply translation if requested
        if data.get('translate', False):
            target_lang = data.get('target_language', 'en')
            translation_result = translate_text(text, target_lang)
            text = translation_result['translated']
        
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
        
        threading.Timer(30, cleanup).start()  # Keep file for 30 seconds
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch', methods=['POST'])
@limiter.limit("10 per hour")
def batch_process():
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        options = data.get('options', {})
        
        if not texts or len(texts) > 5:
            return jsonify({'error': 'Please provide 1-5 texts'}), 400
        
        results = []
        for text in texts:
            if text and text.strip():
                result = text_preprocessing(text, options)
                results.append(result)
        
        return jsonify({
            'total_processed': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
