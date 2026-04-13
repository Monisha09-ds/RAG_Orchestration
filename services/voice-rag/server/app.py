from flask import Flask, request, jsonify, send_file
import requests
import os
from dotenv import load_dotenv
import io
import tempfile
from groq import Groq
from rag_service import rag_service
from prompts import RAG_SYSTEM_PROMPT
from werkzeug.utils import secure_filename

# Load environment variables                           
load_dotenv()

app = Flask(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
UPLOAD_FOLDER = 'documents'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

VOICE_ID = "21m00Tcm4TlvDq8ikWAM" # Rachel
DEFAULT_MODEL_ID = "eleven_multilingual_v2"

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Expose port (Moved to Dockerfile)
# Port is already exposed in server/Dockerfile

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Index the PDF
        try:
            num_chunks = rag_service.index_pdf(file_path)
            return jsonify({"message": f"File '{filename}' indexed successfully into {num_chunks} chunks."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Only PDF files are supported"}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    if not groq_client:
        return jsonify({"error": "GROQ_API_KEY not set"}), 500

    data = request.json
    messages = data.get('messages', [])
    
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    user_query = messages[-1].get('content')
    
    # Retrieve context
    context = rag_service.query(user_query)
    
    # Prepare prompt with context
    formatted_system_prompt = RAG_SYSTEM_PROMPT.format(context=context)
    
    # Prepare messages for LLM
    llm_messages = [{"role": "system", "content": formatted_system_prompt}]
    
    # Capture relevant message history (last 5 messages for context window efficiency)
    history = messages[-6:-1] if len(messages) > 1 else []
    llm_messages.extend(history)
    
    # Add current user query
    llm_messages.append({"role": "user", "content": user_query})

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=llm_messages,
            temperature=0, # Lower temperature for factual RAG
            max_tokens=1024,
            stream=False
        )
        ai_message = completion.choices[0].message.content
        return jsonify({"message": ai_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if not groq_client:
        return jsonify({"error": "GROQ_API_KEY not set"}), 500
    
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        audio_file.save(temp.name)
        temp_path = temp.name

    try:
        with open(temp_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(temp_path, file.read()),
                model="distil-whisper-large-v3-en",
            )
        return jsonify({"text": transcription.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/api/models', methods=['GET'])
def get_models():
    if not ELEVENLABS_API_KEY:
        return jsonify({"error": "ELEVENLABS_API_KEY not set"}), 500
    
    url = "https://api.elevenlabs.io/v1/models"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Failed to fetch models: {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def speak():
    if not ELEVENLABS_API_KEY:
        return jsonify({"error": "ELEVENLABS_API_KEY not set in .env"}), 500

    data = request.json
    text = data.get('text')
    model_id = data.get('model_id', DEFAULT_MODEL_ID)

    if not text:
        return jsonify({"error": "Text is required"}), 400

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return send_file(
                io.BytesIO(response.content),
                mimetype="audio/mpeg",
                as_attachment=False,
                download_name="output.mp3"
            )
        else:
            return jsonify({"error": f"ElevenLabs API Error: {response.text}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on port 5000, listening on all interfaces (required for Docker)
    app.run(host='0.0.0.0', port=5000, debug=True)
