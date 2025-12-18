from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import uuid
import os


app = Flask(__name__)
CORS(app)


OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ------------------ TTS ENGINE ------------------
async def generate_voice(text, voice, rate, pitch, style, filename):
communicate = edge_tts.Communicate(
text=text,
voice=voice,
rate=rate,
pitch=pitch,
style=style
)
await communicate.save(filename)


# ------------------ API ------------------
@app.route("/generate", methods=["POST"])
def generate():
try:
text = request.form.get("text")
voice = request.form.get("voice", "en-US-JennyNeural")
rate = request.form.get("rate", "+0%")
pitch = request.form.get("pitch", "+0Hz")
style = request.form.get("style", "default")


if not text:
return jsonify({"error": "Text is required"}), 400


filename = os.path.join(OUTPUT_DIR, f"voice_{uuid.uuid4().hex}.mp3")


asyncio.run(
generate_voice(text, voice, rate, pitch, style, filename)
)


return send_file(filename, as_attachment=True)


except Exception as e:
return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000)
