from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import os
import uuid
import time

# ----------------- CONFIG -----------------
TEMP_FOLDER = "temp_audio"
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)  # Allow all origins; restrict if needed

# ----------------- HELPERS -----------------
async def text_to_speech(ssml, voice="en-US-AriaNeural"):
    """Convert text to speech using edge-tts (SSML supported)"""
    filename = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.mp3")
    communicate = edge_tts.Communicate(ssml, voice)
    await communicate.save(filename)
    return filename

def cleanup_temp():
    """Delete audio files older than 60 minutes"""
    now = time.time()
    for f in os.listdir(TEMP_FOLDER):
        path = os.path.join(TEMP_FOLDER, f)
        if os.path.isfile(path) and now - os.path.getctime(path) > 3600:
            os.remove(path)

# ----------------- ROUTES -----------------
@app.route("/wake", methods=["GET"])
def wake():
    return jsonify({"status": "awake"}), 200

@app.route("/generate", methods=["POST"])
def generate_audio():
    data = request.json
    text = data.get("text")
    voice = data.get("voice", "en-US-AriaNeural")
    pitch = data.get("pitch", 0)
    rate = data.get("rate", 0)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # SSML with prosody for pitch and rate
    ssml_text = f'<speak><prosody pitch="{pitch}%" rate="{rate}%">{text}</prosody></speak>'

    try:
        filename = asyncio.run(text_to_speech(ssml_text, voice=voice))
    except Exception as e:
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

    cleanup_temp()
    return send_file(filename, as_attachment=True, download_name="speech.mp3")

# ----------------- MAIN -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
