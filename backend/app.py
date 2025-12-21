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

# ----------------- ASYNC HELPER -----------------
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# ----------------- TEXT CLEANER -----------------
def clean_user_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r'<[^>]+>', '', text)

    text = (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )

    text = " ".join(text.split())
    return text.strip()

# ----------------- EDGE TTS CORE -----------------
async def text_to_speech_async(text: str, voice: str, pitch: int, rate: int):
    filename = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.mp3")

    clean_text = clean_user_text(text)

    # Edge TTS expects % based prosody
    pitch_ssml = f"{pitch:+d}%"
    rate_ssml = f"{rate:+d}%"

    ssml = f"""
<speak version="1.0">
  <voice name="{voice}">
    <prosody pitch="{pitch_ssml}" rate="{rate_ssml}">
      {clean_text}
    </prosody>
  </voice>
</speak>
"""

    communicate = edge_tts.Communicate(ssml, voice)
    await communicate.save(filename)

    return filename

def text_to_speech(text: str, voice: str, pitch: int, rate: int):
    return run_async(text_to_speech_async(text, voice, pitch, rate))

# ----------------- CLEANUP -----------------
def cleanup_temp():
    now = time.time()
    for f in os.listdir(TEMP_FOLDER):
        path = os.path.join(TEMP_FOLDER, f)
        if os.path.isfile(path) and now - os.path.getmtime(path) > 600:
            try:
                os.remove(path)
            except:
                pass

# ----------------- ROUTES -----------------
@app.route("/wake", methods=["GET"])
def wake():
    return jsonify({"status": "awake"}), 200

@app.route("/generate", methods=["POST"])
def generate_audio():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON provided"}), 400

        text = data.get("text", "").strip()
        language = data.get("language", "en")
        gender = data.get("gender", "Female")
        pitch = data.get("pitch", 0)
        rate = data.get("rate", 0)

        if not text:
            return jsonify({"error": "Text is empty"}), 400

        try:
            pitch = int(pitch)
            rate = int(rate)
        except:
            pitch = 0
            rate = 0

        # Safe limits for Edge-TTS
        pitch = max(-50, min(50, pitch))
        rate = max(-50, min(50, rate))

        voice_pack = VOICE_MAP.get(language, VOICE_MAP["en"])
        voice = voice_pack.get(gender, voice_pack["Female"])

        audio_file = text_to_speech(text, voice, pitch, rate)

        if not os.path.exists(audio_file):
            return jsonify({"error": "Audio generation failed"}), 500

        threading.Thread(target=cleanup_temp, daemon=True).start()

        return send_file(
            audio_file,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="speech.mp3"
        )

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Internal Server Error"}), 500

# ----------------- MAIN -----------------
if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Clean temp on startup
    for f in os.listdir(TEMP_FOLDER):
        try:
            os.remove(os.path.join(TEMP_FOLDER, f))
        except:
            pass

    print("✅ Edge-TTS Server running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
