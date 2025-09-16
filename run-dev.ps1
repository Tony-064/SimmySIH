# Runs Flask backend and React frontend in separate PowerShell windows

# Absolute paths
$Root = "c:\Users\nrk06\Desktop\Simmy\chatbot SIH"
$FrontendDir = Join-Path $Root "public-health-chatbot"
$PythonPath = Join-Path $Root ".venv\Scripts\python.exe"
$BackendScript = Join-Path $FrontendDir "backend.py"

Write-Host "Starting development environment..." -ForegroundColor Cyan

# Determine Python interpreter
if (-Not (Test-Path $PythonPath)) {
  Write-Warning "Virtualenv Python not found at $PythonPath. Falling back to system 'python'."
  $PythonPath = "python"
}

# Start Backend (Flask) in a new terminal
Write-Host "Launching backend (Flask)..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "Set-Location '$FrontendDir'; & '$PythonPath' '$BackendScript'"
)

# Start Frontend (React) in a new terminal
Write-Host "Launching frontend (React)..." -ForegroundColor Green
$NodeModules = Join-Path $FrontendDir "node_modules"
if (-Not (Test-Path $NodeModules)) {
  # If dependencies are missing, install then start
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$FrontendDir'; npm install; npm start"
  )
} else {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$FrontendDir'; npm start"
  )
}

Write-Host "Both processes starting in separate terminals." -ForegroundColor Cyan