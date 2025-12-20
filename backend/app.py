# backend/app.py

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
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
def get_transcript(video_id):
    """Fetch transcript from YouTube video ID."""
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([i['text'] for i in transcript])

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
    """Generate TTS from text or YouTube transcript."""
    data = request.json
    text = data.get("text")
    video_id = data.get("video_id")
    language = data.get("language", "en")  # Default voice: English

    # Get text from YouTube if video_id provided
    if video_id:
        try:
            text = get_transcript(video_id)
        except Exception as e:
            return jsonify({"error": f"Failed to get transcript: {str(e)}"}), 400

    if not text:
        return jsonify({"error": "No text or video_id provided"}), 400

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
# Optional: delete old files on startup or via cron job
# Example: delete files older than 60 minutes
import time
def cleanup_temp():
    now = time.time()
    for f in os.listdir(TEMP_FOLDER):
        path = os.path.join(TEMP_FOLDER, f)
        if os.path.isfile(path) and now - os.path.getctime(path) > 3600:
            os.remove(path)

# Run cleanup periodically (you can call this in a separate thread or cron)
cleanup_temp()

# ----------------- MAIN -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
