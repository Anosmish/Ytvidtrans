# backend/app.py

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import os
import uuid
from googletrans import Translator
import time

# ----------------- CONFIG -----------------
TEMP_FOLDER = "temp_audio"
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)  # Allow all origins; you can restrict to your frontend URL if desired

translator = Translator()

# ----------------- HELPERS -----------------
async def text_to_speech(text, voice="en-US-AriaNeural"):
    """Convert text to speech using edge-tts"""
    filename = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.mp3")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)  # correct usage
    return filename

def translate_text(text, dest_lang):
    """Translate text to the target language"""
    return translator.translate(text, dest=dest_lang).text

def cleanup_temp():
    """Delete files older than 60 minutes"""
    now = time.time()
    for f in os.listdir(TEMP_FOLDER):
        path = os.path.join(TEMP_FOLDER, f)
        if os.path.isfile(path) and now - os.path.getctime(path) > 3600:
            os.remove(path)

# ----------------- ROUTES -----------------
@app.route("/wake", methods=["GET"])
def wake():
    """Simple endpoint to keep Render awake"""
    return jsonify({"status": "awake"}), 200

@app.route("/generate", methods=["POST"])
def generate_audio():
    data = request.json
    text = data.get("text")
    voice = data.get("voice", "en-US-AriaNeural")  # full voice string
    pitch = data.get("pitch", 0)                  # in percent
    rate = data.get("rate", 0)                    # in percent

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Apply pitch/rate via SSML
    ssml_text = f'<speak><prosody pitch="{pitch}%" rate="{rate}%">{text}</prosody></speak>'

    try:
        filename = asyncio.run(text_to_speech(ssml_text, voice=voice))
    except Exception as e:
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

    cleanup_temp()
    return send_file(filename, as_attachment=True, download_name="speech.mp3")

    # Translate if requested language != English
    if language != "en":
        try:
            text = translate_text(text, language)
        except Exception as e:
            return jsonify({"error": f"Translation failed: {str(e)}"}), 400

    # Generate TTS audio
    try:
        filename = asyncio.run(text_to_speech(text, voice=f"{language}-US-AriaNeural"))
    except Exception as e:
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

    # Cleanup old files
    cleanup_temp()

    # Send audio file
    return send_file(filename, as_attachment=True, download_name="speech.mp3")

# ----------------- MAIN -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
