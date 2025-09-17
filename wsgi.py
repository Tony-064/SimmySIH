from flask im# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure Gemini API endpoint
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-1.0-pro:generateContent"send_from_directory, request, jsonify
from flask_cors import CORS
import os
import requests
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

# Initialize Gemini with API key and correct version
genai.configure(
    api_key=api_key,
    client_options={
        "api_endpoint": "https://generativelanguage.googleapis.com",
        "universe_domain": "googleapis.com"
    }
)

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('query')
        if not user_message:
            return jsonify({"response": "No message received"}), 400
            
        # Prepare request to Gemini API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": user_message
                }]
            }]
        }
        
        # Make request to Gemini API
        response = requests.post(
            GEMINI_API_ENDPOINT,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            print(f"Gemini API error: {response.status_code} - {response.text}")
            return jsonify({
                "response": "Sorry, there was an error getting a response from the AI.",
                "error": f"API Error {response.status_code}"
            }), 500
            
        # Extract answer from response
        response_data = response.json()
        answer = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Sorry, I couldn't get an answer.")
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "response": "Sorry, there was an error processing your request. Please try again.",
            "error": str(e)
        }), 500
    
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