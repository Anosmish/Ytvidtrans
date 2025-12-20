from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import edge_tts
import asyncio
import uuid
import os
import threading
import time
from deep_translator import GoogleTranslator  # Python translation library

app = Flask(__name__)
CORS(app)

AUDIO_FOLDER = "audio_files"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

VOICES = {
    "English US": {"Female": "en-US-AriaNeural", "Male": "en-US-GuyNeural"},
    "English UK": {"Female": "en-GB-LibbyNeural", "Male": "en-GB-RyanNeural"},
    "French": {"Female": "fr-FR-DeniseNeural", "Male": "fr-FR-HenriNeural"},
    "German": {"Female": "de-DE-KatjaNeural", "Male": "de-DE-ConradNeural"},
    "Hindi": {"Female": "hi-IN-SwaraNeural", "Male": "hi-IN-RaviNeural"},
}

# ---------------- Auto-cleanup ----------------
def cleanup_old_files():
    while True:
        now = time.time()
        for f in os.listdir(AUDIO_FOLDER):
            path = os.path.join(AUDIO_FOLDER, f)
            if os.path.isfile(path) and now - os.path.getmtime(path) > 3600:  # 60 mins
                os.remove(path)
        time.sleep(600)

threading.Thread(target=cleanup_old_files, daemon=True).start()

# ---------------- Routes ----------------
@app.route("/wake", methods=["GET"])
def wake_service():
    return jsonify({"status": "Service is awake!"})

@app.route("/generate", methods=["POST"])
def generate_audio():
    data = request.json
    text = data.get("text")
    language = data.get("language")
    gender = data.get("gender")
    rate = data.get("rate", 0)
    pitch = data.get("pitch", 0)
    translate_to = data.get("translate_to")

    if not all([text, language, gender]):
        return jsonify({"error": "Missing parameters"}), 400

    # Translate if required
    if translate_to and translate_to != "None":
        try:
            text = GoogleTranslator(source='auto', target=translate_to).translate(text)
        except Exception as e:
            return jsonify({"error": f"Translation failed: {str(e)}"}), 500

    voice = VOICES[language][gender]
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_FOLDER, filename)

    ssml = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
           xmlns:mstts="http://www.w3.org/2001/mstts"
           xml:lang="en-US">
        <voice name="{voice}">
            <prosody rate="{rate}%" pitch="{pitch}%">
                {text}
            </prosody>
        </voice>
    </speak>
    """

    async def text_to_speech():
        communicate = edge_tts.Communicate(ssml, output=filepath)
        await communicate.save()

    asyncio.run(text_to_speech())

    return jsonify({"audio_url": f"/download/{filename}"})


@app.route("/download/<filename>")
def download_file(filename):
    path = os.path.join(AUDIO_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
