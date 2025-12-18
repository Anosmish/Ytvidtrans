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

# ---------- HELPERS ----------
def clamp(value, min_v, max_v):
    return max(min_v, min(value, max_v))

# ---------- TTS ----------
async def generate_voice(text, voice, rate, pitch, filename):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch
    )
    await communicate.save(filename)

# ---------- API ----------
@app.route("/generate", methods=["POST"])
def generate():
    try:
        text = request.form.get("text")
        voice = request.form.get("voice", "en-US-JennyNeural")

        # frontend sends raw numbers (e.g. -30, 0, 25)
        rate_val = int(request.form.get("rate", 0))
        pitch_val = int(request.form.get("pitch", 0))

        # clamp to safe ranges
        rate_val = clamp(rate_val, -50, 50)
        pitch_val = clamp(pitch_val, -10, 10)

        # edge-tts REQUIRES signed values WITH units
        rate = f"{rate_val:+d}%"     # e.g. -30% , +0% , +25%
        pitch = f"{pitch_val:+d}Hz"  # e.g. -5Hz , +0Hz

        if not text:
            return jsonify({"error": "Text required"}), 400

        filename = os.path.join(
            OUTPUT_DIR, f"voice_{uuid.uuid4().hex}.mp3"
        )

        asyncio.run(generate_voice(text, voice, rate, pitch, filename))

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
