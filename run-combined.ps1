# Build React frontend and start Flask backend to serve the built app on a single port
# Usage: Right-click > Run with PowerShell OR
#   PowerShell -ExecutionPolicy Bypass -File "c:\Users\nrk06\Desktop\Simmy\chatbot SIH\run-combined.ps1"

$ErrorActionPreference = 'Stop'

# Absolute paths
$Root = "c:\Users\nrk06\Desktop\Simmy\chatbot SIH"
$FrontendDir = Join-Path $Root "public-health-chatbot"
$PythonPath = Join-Path $Root ".venv\Scripts\python.exe"
$BackendScript = Join-Path $FrontendDir "backend.py"

Write-Host "Starting combined build + backend serve..." -ForegroundColor Cyan

# Determine Python interpreter
if (-Not (Test-Path $PythonPath)) {
  Write-Warning "Virtualenv Python not found at $PythonPath. Falling back to system 'python'."
  $PythonPath = "python"
}

# Ensure frontend deps and build
Set-Location $FrontendDir
$NodeModules = Join-Path $FrontendDir "node_modules"
if (-Not (Test-Path $NodeModules)) {
  Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
  npm install
}

Write-Host "Building frontend..." -ForegroundColor Yellow
npm run build

Write-Host "Launching Flask backend (single-port serve)..." -ForegroundColor Green
& $PythonPath $BackendScript