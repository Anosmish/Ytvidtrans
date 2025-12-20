from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import os
import uuid
import time
import threading

# ----------------- CONFIG -----------------
TEMP_FOLDER = "temp_audio"
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

# ----------------- VOICE MAPPING -----------------
VOICE_MAP = {
    "en": {"Female": "en-US-AriaNeural", "Male": "en-US-GuyNeural"},
    "hi": {"Female": "hi-IN-SwaraNeural", "Male": "hi-IN-MadhurNeural"},  # Fixed: Changed to correct male voice
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

async def text_to_speech_async(ssml: str, voice: str):
    """Convert text to speech using edge-tts"""
    filename = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.mp3")
    communicate = edge_tts.Communicate(ssml, voice)
    await communicate.save(filename)
    return filename

def text_to_speech(ssml: str, voice: str):
    """Wrapper to run async TTS function"""
    return run_async(text_to_speech_async(ssml, voice))

def cleanup_temp():
    """Delete audio files older than 60 minutes"""
    try:
        now = time.time()
        for f in os.listdir(TEMP_FOLDER):
            path = os.path.join(TEMP_FOLDER, f)
            if os.path.isfile(path) and now - os.path.getmtime(path) > 3600:
                os.remove(path)
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

        # Ensure pitch and rate are within bounds
        pitch = max(-50, min(50, pitch))
        rate = max(-50, min(50, rate))

        # Select the correct voice
        voice_info = VOICE_MAP.get(language, VOICE_MAP["en"])
        voice = voice_info.get(gender, voice_info["Female"])

        # Create SSML with proper escaping
        import html
        safe_text = html.escape(text)
        ssml_text = f'<speak><prosody pitch="{pitch}%" rate="{rate}%">{safe_text}</prosody></speak>'

        # Generate audio file
        filename = text_to_speech(ssml_text, voice=voice)
        
        if not os.path.exists(filename):
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
    # Handle asyncio issues in Windows/Linux
    if os.name == 'nt':  # Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    app.run(host="0.0.0.0", port=5000, debug=False)  # Set debug=False for production
