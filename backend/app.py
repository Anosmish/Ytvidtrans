from flask import Flask, request, send_file, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import edge_tts
import asyncio
import requests
import os
import uuid

app = Flask(__name__)

# ------------------ TRANSCRIPT ------------------
def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([i['text'] for i in transcript])

# ------------------ TRANSLATE ------------------
def translate_text(text, target_lang):
    url = "https://libretranslate.de/translate"
    data = {
        "q": text,
        "source": "en",
        "target": target_lang,
        "format": "text"
    }
    response = requests.post(url, data=data, timeout=30)
    return response.json()["translatedText"]

# ------------------ TTS ------------------
async def generate_voice(text, lang, speed, pitch, filename):
    voice_map = {
        "hi": "hi-IN-SwaraNeural",
        "en": "en-US-JennyNeural",
        "ta": "ta-IN-PallaviNeural"
    }

    voice = voice_map.get(lang, "en-US-JennyNeural")

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=speed,
        pitch=pitch
    )

    await communicate.save(filename)

# ------------------ API ------------------
@app.route("/generate", methods=["POST"])
def generate():
    try:
        video_id = request.form.get("video_id")
        lang = request.form.get("language", "en")
        speed = request.form.get("speed", "+0%")
        pitch = request.form.get("pitch", "+0Hz")

        if not video_id:
            return jsonify({"error": "video_id required"}), 400

        # unique filename (important for Render)
        output_file = f"voice_{uuid.uuid4().hex}.mp3"

        text = get_transcript(video_id)
        translated_text = translate_text(text, lang)

        asyncio.run(
            generate_voice(translated_text, lang, speed, pitch, output_file)
        )

        return send_file(output_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
