# ===================================
# Run All MedBot Intelligence Services Locally
# WITHOUT Docker
# ===================================

param(
    [switch]$SkipInfraCheck = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MedBot Intelligence - Start All Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
$PROJECT_ROOT = "C:\Users\HP\Desktop\MedBot-Intelligence"
Set-Location $PROJECT_ROOT

# Load environment variables from env.local
Write-Host "Loading environment variables..." -ForegroundColor Yellow
if (Test-Path "$PROJECT_ROOT\env.local") {
    Get-Content "$PROJECT_ROOT\env.local" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    Write-Host "Environment variables loaded" -ForegroundColor Green
}
else {
    Write-Host "ERROR: env.local file not found!" -ForegroundColor Red
    Write-Host "Please create env.local file first" -ForegroundColor Yellow
    exit 1
}

# Create necessary directories
Write-Host ""
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
$directories = @(
    "$PROJECT_ROOT\data\documents",
    "$PROJECT_ROOT\data\faiss_indices",
    "$PROJECT_ROOT\backups"
)
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    }
}
Write-Host "Directories ready" -ForegroundColor Green

# Services to start (in order)
$services = @(
    @{Name = "audit-logger"; Port = 8006; Path = "services\audit-logger" },
    @{Name = "doc-ingestor"; Port = 8001; Path = "services\doc-ingestor" },
    @{Name = "deid"; Port = 8002; Path = "services\deid" },
    @{Name = "indexeur-semantique"; Port = 8003; Path = "services\indexeur-semantique" },
    @{Name = "llm-qa-module"; Port = 8004; Path = "services\llm-qa-module" },
    @{Name = "synthese-comparative"; Port = 8005; Path = "services\synthese-comparative" },
    @{Name = "api-gateway"; Port = 8000; Path = "services\api-gateway" }
)

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host ""

foreach ($service in $services) {
    $serviceName = $service.Name
    $servicePort = $service.Port
    $servicePath = Join-Path $PROJECT_ROOT $service.Path
    
    Write-Host "[$serviceName] Starting on port $servicePort..." -ForegroundColor Cyan
    
    # Check if virtual environment exists
    $venvPath = Join-Path $servicePath "venv"
    if (-not (Test-Path $venvPath)) {
        Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
        Set-Location $servicePath
        python -m venv venv
        Write-Host "  Virtual environment created" -ForegroundColor Green
    }
    
    # Start the service in a new PowerShell window
    Write-Host "  Starting service..." -ForegroundColor Yellow
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    # Create a startup script for this service
    $startupScript = Join-Path $servicePath "start-service.ps1"
    $scriptContent = @"
Set-Location '$servicePath'
& '$activateScript'
`$env:PYTHONPATH = '$servicePath'
Write-Host "Installing dependencies for $serviceName..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Starting $serviceName on port $servicePort..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port $servicePort --reload
"@
    Set-Content -Path $startupScript -Value $scriptContent
    
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $startupScript
    
    Write-Host "  $serviceName started on port $servicePort" -ForegroundColor Green
    Write-Host ""
    
    # Wait a bit before starting next service
    Start-Sleep -Seconds 2
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All services started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Yellow
Write-Host "  API Gateway:           http://localhost:8000" -ForegroundColor White
Write-Host "  API Gateway Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "  DocIngestor:           http://localhost:8001" -ForegroundColor White
Write-Host "  DeID:                  http://localhost:8002" -ForegroundColor White
Write-Host "  Indexeur Semantique:   http://localhost:8003" -ForegroundColor White
Write-Host "  LLM QA Module:         http://localhost:8004" -ForegroundColor White
Write-Host "  Synthese Comparative:  http://localhost:8005" -ForegroundColor White
Write-Host "  Audit Logger:          http://localhost:8006" -ForegroundColor White
Write-Host ""
Write-Host "Infrastructure URLs:" -ForegroundColor Yellow
Write-Host "  RabbitMQ Management:   http://localhost:15672" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each service window to stop" -ForegroundColor Gray
