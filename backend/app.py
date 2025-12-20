# backend/app.py

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import os
import uuid
from googletrans import Translator  # For translation

# ----------------- CONFIG -----------------
TEMP_FOLDER = "temp_audio"
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)  # Allow all origins; replace with origins=[your_frontend_url] for security

translator = Translator()

# ----------------- HELPERS -----------------
async def text_to_speech(text, voice="en-US-AriaNeural"):
    """Convert text to speech using edge-tts."""
    filename = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.mp3")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)
    return filename

def translate_text(text, dest_lang):
    """Translate text to destination language."""
    return translator.translate(text, dest=dest_lang).text

# ----------------- ROUTES -----------------
@app.route("/wake", methods=["GET"])
def wake():
    """Simple endpoint to keep Render awake."""
    return jsonify({"status": "awake"}), 200

@app.route("/generate", methods=["POST"])
def generate_tts():
    """Generate TTS from user text."""
    data = request.json
    text = data.get("text")
    language = data.get("language", "en")  # Default voice: English

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Translate if requested language != English
    if language != "en":
        try:
            text = translate_text(text, language)
        except Exception as e:
            return jsonify({"error": f"Translation failed: {str(e)}"}), 400

    # Generate TTS
    try:
        filename = asyncio.run(text_to_speech(text, voice=f"{language}-US-AriaNeural"))
    except Exception as e:
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

    # Return audio file
    return send_file(filename, as_attachment=True, download_name="speech.mp3")

# ----------------- CLEANUP -----------------
import time
def cleanup_temp():
    """Delete files older than 60 minutes."""
    now = time.time()
    for f in os.listdir(TEMP_FOLDER):
        path = os.path.join(TEMP_FOLDER, f)
        if os.path.isfile(path) and now - os.path.getctime(path) > 3600:
            os.remove(path)

cleanup_temp()

# ----------------- MAIN -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
