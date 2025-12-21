from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import os
import uuid
import time
import threading
import re

# ---------------- CONFIG ----------------
TEMP_FOLDER = "temp_audio"
os.makedirs(TEMP_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

# ---------------- VOICE MAPPING ----------------
VOICE_MAP = {
    "en": {"Female": "en-US-AriaNeural", "Male": "en-US-GuyNeural"},
    "hi": {"Female": "hi-IN-SwaraNeural", "Male": "hi-IN-MadhurNeural"},
    "es": {"Female": "es-ES-ElviraNeural", "Male": "es-ES-AlvaroNeural"},
    "fr": {"Female": "fr-FR-DeniseNeural", "Male": "fr-FR-HenriNeural"},
    "de": {"Female": "de-DE-KatjaNeural", "Male": "de-DE-ConradNeural"}
}

# ---------------- HELPERS ----------------
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def clean_user_text(text: str) -> str:
    if not text:
        return ""
    # Remove any tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra spaces
    text = ' '.join(text.split())
    return text.strip()

async def text_to_speech_async(text: str, voice: str, pitch: int, rate: int):
    filename = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.mp3")
    clean_text = clean_user_text(text)

    # Edge-TTS expects strings like "+10%" and "+2Hz"
    rate_str = f"{rate:+d}%"
    pitch_str = f"{pitch:+d}Hz"

    # Communicate without SSML
    communicate = edge_tts.Communicate(
        text=clean_text,
        voice=voice,
        rate=rate_str,
        pitch=pitch_str
    )

    await communicate.save(filename)
    return filename

def text_to_speech(text: str, voice: str, pitch: int, rate: int):
    return run_async(text_to_speech_async(text, voice, pitch, rate))

def cleanup_temp():
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
        print("Cleanup error:", e)

# ---------------- ROUTES ----------------
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
            return jsonify({"error": "Text is empty"}), 400

        # Validate pitch and rate
        try:
            pitch = int(pitch)
            rate = int(rate)
        except:
            pitch = 0
            rate = 0

        # Limit values
        pitch = max(-50, min(50, pitch))
        rate = max(-50, min(50, rate))

        voice_info = VOICE_MAP.get(language, VOICE_MAP["en"])
        voice = voice_info.get(gender, voice_info["Female"])

        filename = text_to_speech(text, voice, pitch, rate)

        if not os.path.exists(filename):
            return jsonify({"error": "Audio generation failed"}), 500

        # Cleanup in background
        threading.Thread(target=cleanup_temp, daemon=True).start()

        return send_file(
            filename,
            as_attachment=True,
            download_name="speech.mp3",
            mimetype="audio/mpeg"
        )

    except Exception as e:
        print("Server error:", e)
        return jsonify({"error": str(e)}), 500

# ---------------- MAIN ----------------
if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Clean temp folder on startup
    try:
        for f in os.listdir(TEMP_FOLDER):
            os.remove(os.path.join(TEMP_FOLDER, f))
    except:
        pass

    print("Server running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)
