# ===================================
# Run a Single MedBot Intelligence Service
# Usage: .\run-single-service.ps1 -ServiceName "doc-ingestor"
# ===================================

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("api-gateway", "audit-logger", "deid", "doc-ingestor", "indexeur-semantique", "llm-qa-module", "synthese-comparative")]
    [string]$ServiceName
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting $ServiceName" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
$PROJECT_ROOT = "C:\Users\HP\Desktop\MedBot-Intelligence"
$SERVICE_PATH = Join-Path $PROJECT_ROOT "services\$ServiceName"

# Check if service exists
if (-not (Test-Path $SERVICE_PATH)) {
    Write-Host "ERROR: Service '$ServiceName' not found at $SERVICE_PATH" -ForegroundColor Red
    exit 1
}

# Load environment variables
Write-Host "Loading environment variables..." -ForegroundColor Yellow
if (Test-Path "$PROJECT_ROOT\env.local") {
    Get-Content "$PROJECT_ROOT\env.local" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    Write-Host "✓ Environment variables loaded" -ForegroundColor Green
}
else {
    Write-Host "WARNING: env.local file not found, using system environment" -ForegroundColor Yellow
}

# Determine port based on service
$ports = @{
    "api-gateway"          = 8000
    "doc-ingestor"         = 8001
    "deid"                 = 8002
    "indexeur-semantique"  = 8003
    "llm-qa-module"        = 8004
    "synthese-comparative" = 8005
    "audit-logger"         = 8006
}
$PORT = $ports[$ServiceName]

Write-Host ""
Write-Host "Service: $ServiceName" -ForegroundColor Cyan
Write-Host "Port: $PORT" -ForegroundColor Cyan
Write-Host "Path: $SERVICE_PATH" -ForegroundColor Cyan
Write-Host ""

# Navigate to service directory
Set-Location $SERVICE_PATH

# Check if virtual environment exists
$venvPath = Join-Path $SERVICE_PATH "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Set PYTHONPATH
$env:PYTHONPATH = $SERVICE_PATH

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting $ServiceName on port $PORT..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Documentation: http://localhost:$PORT/docs" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Gray
Write-Host ""

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
