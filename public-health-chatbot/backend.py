# Flask backend that serves React build and exposes API endpoints (including /chat)
import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini with API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

# Paths
BASE_DIR = os.path.dirname(__file__)
BUILD_DIR = os.path.join(BASE_DIR, "build")  # build lives next to this backend.py

# Serve static assets from React build
app = Flask(__name__, static_folder=BUILD_DIR, static_url_path="/")
# In production, set FRONTEND_URL to your deployed frontend origin to restrict CORS
CORS(app, origins=os.environ.get("FRONTEND_URL", "*"))  # Same service serves API + static
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")


# Health check
@app.route("/api/health")
def health():
    return jsonify({"ok": True})


# Example API endpoint
@app.route("/api/echo", methods=["POST"])
def echo():
    data = request.get_json() or {}
    return jsonify({"you_sent": data})


# Chat endpoint using Gemini
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("query")
        if not user_message:
            return jsonify({"response": "No message received"}), 400

        system_prompt = (
            "You are a public health assistant. When the user asks about a disease, symptoms, or treatment, "
            "respond in clear sections as HTML with headings and lists. Sections must include: "
            "<h3>Possible Causes</h3>, <h3>Prevention</h3>, <h3>Home Remedies</h3>, <h3>Basic Medications</h3>, "
            "<h3>When to See a Doctor</h3>, and a <h3>Disclaimer</h3>. Use simple <p> and <ul><li> elements. "
            "Bold key terms with <strong>. Do not add outer html/body tags."
        )

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"{system_prompt}\n\nUser: {user_message}")
        answer_text = response.text or "Sorry, I couldn't get an answer."

        html = f'''
        <div style="line-height:1.6;">
          {answer_text}
          <style>
            .badge {{ display:inline-block;padding:2px 6px;border-radius:6px;background:#e8f0fe;color:#1a73e8;font-weight:600; }}
            .badge-warn {{ background:#fdecea;color:#d93025; }}
            h3 {{ color:#1f4d3a;font-weight:700;margin-top:8px; }}
            ul {{ padding-left:1rem; }}
          </style>
        </div>
        '''
        return jsonify({"response": answer_text, "html": html})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500


# Serve React app for all other routes (supports client-side routing)
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    file_path = os.path.join(BUILD_DIR, path)
    if path and os.path.exists(file_path):
        return send_from_directory(BUILD_DIR, path)
    return send_from_directory(BUILD_DIR, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)