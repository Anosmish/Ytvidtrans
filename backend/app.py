from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import os
import uuid
import time
import threading
import re
import xml.etree.ElementTree as ET

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

# ----------------- HELPERS -----------------

def run_async(coro):
    """Run async function in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def clean_user_text(text: str) -> str:
    """Clean user input text while preserving SSML structure"""
    if not text:
        return ""

    # Check if input contains SSML tags
    ssml_pattern = r'<speak.*?>.*?</speak>'
    has_ssml = re.search(ssml_pattern, text, re.DOTALL | re.IGNORECASE)
    
    if has_ssml:
        # For SSML content, we need to parse and clean it properly
        try:
            # Remove potential XML declarations and comments first
            text = re.sub(r'<\?xml.*?\?>', '', text, flags=re.DOTALL)
            text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
            
            # Ensure proper <speak> tag structure
            if not re.search(r'<speak.*?>', text, re.IGNORECASE):
                text = f'<speak>{text}</speak>'
            elif not re.search(r'</speak>', text, re.IGNORECASE):
                # Find opening speak tag and close it
                match = re.search(r'<speak.*?>', text, re.IGNORECASE)
                if match:
                    text = text + '</speak>'
            
            # Clean SSML: remove potentially dangerous tags but keep safe ones
            # Keep common SSML tags: speak, voice, prosody, break, say-as, phoneme, sub, emphasis
            # Remove script, object, iframe, etc.
            dangerous_patterns = [
                r'<script.*?>.*?</script>',
                r'<object.*?>.*?</object>',
                r'<iframe.*?>.*?</iframe>',
                r'<applet.*?>.*?</applet>',
                r'<embed.*?>.*?</embed>',
                r'on\w+\s*=',
                r'javascript:',
                r'vbscript:',
                r'data:'
            ]
            
            for pattern in dangerous_patterns:
                text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
            
            # Escape characters between tags but preserve tag structure
            # Split text into tags and content
            parts = re.split(r'(<[^>]+>)', text)
            cleaned_parts = []
            
            for part in parts:
                if re.match(r'<[^>]+>$', part):
                    # This is a tag, keep it as is
                    cleaned_parts.append(part)
                else:
                    # This is text content, escape XML special characters
                    escaped = (
                        part.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                            .replace('"', "&quot;")
                            .replace("'", "&apos;")
                    )
                    cleaned_parts.append(escaped)
            
            text = ''.join(cleaned_parts)
            
            # Validate the SSML structure
            try:
                # Remove XML declaration if present and parse
                clean_xml = re.sub(r'<\?xml.*?\?>', '', text, flags=re.DOTALL).strip()
                ET.fromstring(clean_xml)
            except ET.ParseError as e:
                # If SSML is malformed, fall back to plain text
                print(f"SSML parse error: {e}")
                # Extract text content from SSML
                text_only = re.sub(r'<[^>]+>', '', text)
                text = f'<speak>{text_only}</speak>'
            
        except Exception as e:
            print(f"SSML processing error: {e}")
            # Fallback: extract text from SSML and wrap in speak tags
            text_only = re.sub(r'<[^>]+>', '', text)
            text = f'<speak>{text_only}</speak>'
    else:
        # For plain text, escape and wrap in SSML
        text = (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;")
        )
        # Remove multiple spaces and trim
        text = " ".join(text.split()).strip()
        if text:
            text = f'<speak>{text}</speak>'
    
    return text

async def text_to_speech_async(text: str, voice: str, pitch: int, rate: int):
    """Convert text to speech using edge-tts"""
    filename = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.mp3")

    clean_text = clean_user_text(text)
    
    if not clean_text or clean_text == "<speak></speak>":
        # Create empty audio file or default message
        default_text = "<speak>No text provided.</speak>"
        communicate = edge_tts.Communicate(text=default_text, voice=voice)
    else:
        # Check if we need to apply pitch/rate adjustments
        if pitch != 0 or rate != 0:
            # Parse the SSML and add prosody tag
            try:
                # Remove XML declaration if present
                clean_xml = re.sub(r'<\?xml.*?\?>', '', clean_text, flags=re.DOTALL).strip()
                root = ET.fromstring(clean_xml)
                
                # Create prosody element with adjustments
                prosody = ET.Element('prosody')
                
                # Apply rate adjustment (-50 to 50 maps to 50% to 150%)
                if rate != 0:
                    # Convert -50..50 to 0.5x..1.5x (50%..150%)
                    rate_percent = 100 + rate * 1
                    prosody.set('rate', f'{rate_percent}%')
                
                # Apply pitch adjustment (-50 to 50 maps to -12st to +12st)
                if pitch != 0:
                    # Convert -50..50 to -12st..+12st
                    pitch_st = pitch * 12 / 50
                    prosody.set('pitch', f'{pitch_st:+}st')
                
                # Move all existing content into prosody tag
                for child in list(root):
                    prosody.append(child)
                
                # Clear root and add prosody
                root.clear()
                root.append(prosody)
                
                # Convert back to string
                clean_text = ET.tostring(root, encoding='unicode')
                
            except Exception as e:
                print(f"Error applying pitch/rate: {e}")
                # Fallback: wrap existing SSML in prosody tag using regex
                if pitch != 0 or rate != 0:
                    pitch_st = pitch * 12 / 50
                    rate_percent = 100 + rate * 1
                    
                    # Extract content between speak tags
                    match = re.search(r'<speak.*?>(.*?)</speak>', clean_text, re.DOTALL)
                    if match:
                        content = match.group(1)
                        clean_text = f'<speak><prosody pitch="{pitch_st:+}st" rate="{rate_percent}%">{content}</prosody></speak>'
        
        communicate = edge_tts.Communicate(text=clean_text, voice=voice)

    await communicate.save(filename)
    
    # Verify file was created
    if not os.path.exists(filename):
        raise Exception("Audio file was not created")
    
    return filename

def text_to_speech(text: str, voice: str, pitch: int, rate: int):
    """Sync wrapper"""
    return run_async(text_to_speech_async(text, voice, pitch, rate))

def cleanup_temp():
    """Delete audio files older than 10 minutes"""
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

# ----------------- ROUTES -----------------

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
            return jsonify({"error": "No text provided"}), 400

        # validate pitch & rate
        try:
            pitch = int(pitch)
            rate = int(rate)
        except:
            pitch = 0
            rate = 0

        pitch = max(-50, min(50, pitch))
        rate = max(-50, min(50, rate))

        # select voice
        voice_info = VOICE_MAP.get(language, VOICE_MAP["en"])
        voice = voice_info.get(gender, voice_info["Female"])

        # generate audio
        filename = text_to_speech(text, voice, pitch, rate)

        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            return jsonify({"error": "Audio file generation failed"}), 500

        threading.Thread(target=cleanup_temp, daemon=True).start()

        return send_file(
            filename,
            as_attachment=True,
            download_name="speech.mp3",
            mimetype="audio/mpeg"
        )

    except Exception as e:
        print("Server error:", e)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ----------------- MAIN -----------------

if __name__ == "__main__":
    # Set asyncio policy for Windows if needed
    if os.name == "nt":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except:
            pass

    # Clean temp folder on startup
    try:
        for f in os.listdir(TEMP_FOLDER):
            try:
                os.remove(os.path.join(TEMP_FOLDER, f))
            except:
                pass
    except:
        pass

    print("Server starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=true, threaded=True)
