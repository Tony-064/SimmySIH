from flask import Flask, send_from_directory
import os

# Flask app, pointing to React build
app = Flask(__name__, static_folder="static", static_url_path="")

# Serve React index.html at root
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# Serve React Router paths (fallback to index.html)
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

# Optional: health check route (Render pings this)
@app.route("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))