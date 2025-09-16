# Repo Overview

- Name: chatbot SIH
- Root: c:\Users\nrk06\Desktop\Simmy\chatbot SIH

## Layout
- Backend: public-health-chatbot/backend.py (Flask)
- Frontend: public-health-chatbot (React + Tailwind)
- Run script: run-dev.ps1 (spawns backend and frontend terminals)
- Python env: .venv (Windows)
- Env files: .env at repo root and public-health-chatbot/.env

## Backend
- Framework: Flask
- CORS: enabled
- Serves built React from public-health-chatbot/build
- Endpoints:
  - GET /api/health -> { ok: true }
  - POST /api/echo -> echos JSON
  - POST /chat -> calls Gemini (google-generativeai)
- Requires env:
  - GEMINI_API_KEY
  - SECRET_KEY (optional, defaults dev-secret)
  - PORT (optional, defaults 5000)

## Frontend
- React CRA-based app located in public-health-chatbot
- Dev start: npm start within that directory
- Build output used by Flask in build/

## Dev
- Start both: run-dev.ps1
- Python deps: requirements.txt (generated)
- Node deps: package.json in public-health-chatbot

## Notes
- Ensure GEMINI_API_KEY is set in an .env (backend loads via python-dotenv)
- For production, build React then run Flask with gunicorn