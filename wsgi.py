from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize Gemini with API key and defaults
genai.configure(
    api_key=api_key,
    transport='rest'  # Ensure REST transport is used
)

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('query')
        if not user_message:
            return jsonify({"response": "No message received"}), 400
            
        # Configure generation parameters
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        # Create model instance with configuration
        model = genai.GenerativeModel(model_name='gemini-pro',
                                    generation_config=generation_config)
        
        # Generate response with safety settings
        safety_settings = {
            "harassment": "block_none",
            "hate_speech": "block_none",
            "sexually_explicit": "block_none",
            "dangerous_content": "block_none",
        }
        
        response = model.generate_content(
            contents=user_message,
            safety_settings=safety_settings,
            stream=False
        )
        
        answer = response.text if response.text else "Sorry, I couldn't get an answer."
    except Exception as e:
        answer = f"Error: {str(e)}"
    return jsonify({"response": answer})

# Serve React build
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# React Router fallback
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

# Health check (Render uses this)
@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)