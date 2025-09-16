"""
WSGI entrypoint for Gunicorn.
Safely imports the Flask `app` from the hyphenated directory `public-health-chatbot`.
"""
import os
import sys
import importlib.util

BASE_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.join(BASE_DIR, "public-health-chatbot")
BACKEND_PATH = os.path.join(BACKEND_DIR, "backend.py")

if not os.path.isfile(BACKEND_PATH):
    raise RuntimeError(f"backend.py not found at expected path: {BACKEND_PATH}")

# Load backend.py as a module named 'backend' and expose its `app`
spec = importlib.util.spec_from_file_location("backend", BACKEND_PATH)
backend = importlib.util.module_from_spec(spec)
sys.modules["backend"] = backend
assert spec and spec.loader, "Failed to load spec for backend.py"
spec.loader.exec_module(backend)  # type: ignore

# Gunicorn will look for `app`
app = getattr(backend, "app", None)
if app is None:
    raise RuntimeError("`app` not found in backend module. Ensure backend.py defines `app = Flask(__name__)`.")