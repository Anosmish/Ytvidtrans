from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import os
import uuid
import time
import threading
import re

# ----------------- CONFIG -----------------
TEMP_FOLDER = "temp_audio"
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

# ----------------- VOICE MAPPING -----------------
VOICE_MAP = {
    "en": {"Female": "en-US-AriaNeural", "Male": "en-US-GuyNeural"},
    "hi": {"Female": "hi-IN-SwaraNeural", "Male": "hi-IN-MadhurNeural"},
    "es": {"Female": "es-ES-ElviraNeural", "Male": "es-ES-AlvaroNeural"},
    "fr": {"Female": "fr-FR-DeniseNeural", "Male": "fr-FR-HenriNeural"},
    "de": {"Female": "de-DE-KatjaNeural", "Male": "de-DE-ConradNeural"}
}

# ----------------- HELPERS -----------------
def run_async(coro):
    """Helper to run async functions in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

async def text_to_speech_async(text: str, voice: str, pitch: int, rate: int):
    """Convert text to speech using edge-tts with proper SSML formatting"""
    filename = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.mp3")
    
    # Clean the text
    clean_text = clean_user_text(text)
    
    # Format pitch and rate for SSML
    # SSML expects values like "+10%" or "-10%"
    pitch_percent = pitch
    rate_percent = 100 + rate  # SSML rate: 100% is normal, 150% is 1.5x faster
    
    # Create simple SSML without extra voices
    ssml_text = f'{clean_text}'
    
    communicate = edge_tts.Communicate(ssml_text, voice)
    await communicate.save(filename)
    return filename

def text_to_speech(text: str, voice: str, pitch: int, rate: int):
    """Wrapper to run async TTS function"""
    return run_async(text_to_speech_async(text, voice, pitch, rate))

def clean_user_text(text: str) -> str:
    """Clean user input"""
    if not text:
        return ""
    
    # Remove any existing SSML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape XML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def cleanup_temp():
    """Delete audio files older than 10 minutes"""
    try:
        now = time.time()
        for f in os.listdir(TEMP_FOLDER):
            path = os.path.join(TEMP_FOLDER, f)
            if os.path.isfile(path) and now - os.path.getmtime(path) > 600:
                try:
                    os.remove(path)
                except:
                    pass
    except Exception as e:
        print(f"Cleanup error: {e}")

# ----------------- ROUTES -----------------
@app.route("/wake", methods=["GET"])
def wake():
    return jsonify({"status": "awake"}), 200

@app.route("/generate", methods=["POST"])
def generate_audio():
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        text = data.get("text", "").strip()
        language = data.get("language", "en")
        gender = data.get("gender", "Female")
        pitch = data.get("pitch", 0)
        rate = data.get("rate", 0)

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Validate pitch and rate values
        try:
            pitch = int(pitch)
            rate = int(rate)
        except (ValueError, TypeError):
            pitch = 0
            rate = 0

        # Ensure pitch and rate are within reasonable limits
        pitch = max(-50, min(50, pitch))
        rate = max(-50, min(50, rate))

        # Select the correct voice
        voice_info = VOICE_MAP.get(language, VOICE_MAP["en"])
        voice = voice_info.get(gender, voice_info["Female"])

        # Generate audio file
        filename = text_to_speech(text, voice, pitch, rate)
        
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            return jsonify({"error": "Audio file generation failed"}), 500

        # Start cleanup in background thread
        cleanup_thread = threading.Thread(target=cleanup_temp)
        cleanup_thread.daemon = True
        cleanup_thread.start()

        return send_file(
            filename, 
            as_attachment=True, 
            download_name="speech.mp3",
            mimetype="audio/mpeg"
        )
        
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# ----------------- MAIN -----------------
if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Clean temp folder on startup
    try:
        for f in os.listdir(TEMP_FOLDER):
            path = os.path.join(TEMP_FOLDER, f)
            if os.path.isfile(path):
                os.remove(path)
    except:
        pass
    
    print("Server starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
