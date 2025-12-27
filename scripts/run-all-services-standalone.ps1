# ===================================
# Run All MedBot Intelligence Services Locally
# STANDALONE MODE (No RabbitMQ, No Ollama required)
# ===================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MedBot Intelligence - Start All Services" -ForegroundColor Cyan
Write-Host "(Standalone Mode - No RabbitMQ/Ollama)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
$PROJECT_ROOT = "C:\Users\HP\Desktop\MedBot-Intelligence"
Set-Location $PROJECT_ROOT

# Set environment variables for standalone mode
$env:DATABASE_URL = "sqlite:///./service.db"
$env:RABBITMQ_HOST = "localhost"
$env:RABBITMQ_PORT = "5672"
$env:LLM_PROVIDER = "mock"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:ENABLE_RABBIT_MQ = "false"
$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:8000,*"

Write-Host "Environment configured for standalone mode" -ForegroundColor Green
Write-Host ""

# Create necessary directories
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
Write-Host ""

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
        Write-Host "  Virtual environment not found, skipping dependencies install..." -ForegroundColor Yellow
        Write-Host "  (Dependencies should already be installed)" -ForegroundColor Gray
    }
    
    # Start the service in a new PowerShell window
    Write-Host "  Starting service..." -ForegroundColor Yellow
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    # Create a startup script for this service
    $startupScript = Join-Path $servicePath "start-service-standalone.ps1"
    $scriptContent = @"
Set-Location '$servicePath'
& '$activateScript'
`$env:PYTHONPATH = '$servicePath'
`$env:DATABASE_URL = "sqlite:///./service.db"
`$env:LLM_PROVIDER = "mock"
`$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:8000,*"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service: $serviceName" -ForegroundColor Cyan
Write-Host "Port: $servicePort" -ForegroundColor Cyan
Write-Host "Mode: STANDALONE (No RabbitMQ/Ollama)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting $serviceName on port $servicePort..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port $servicePort --reload
"@
    Set-Content -Path $startupScript -Value $scriptContent
    
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $startupScript
    
    Write-Host "  $serviceName started on port $servicePort" -ForegroundColor Green
    Write-Host ""
    
    # Wait a bit before starting next service
    Start-Sleep -Seconds 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All services started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Yellow
Write-Host "  API Gateway:           http://localhost:8000" -ForegroundColor White
Write-Host "  API Gateway Docs:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Doc Ingestor:          http://localhost:8001" -ForegroundColor White
Write-Host "  DeID:                  http://localhost:8002" -ForegroundColor White
Write-Host "  Indexeur Semantique:   http://localhost:8003" -ForegroundColor White
Write-Host "  LLM QA Module:         http://localhost:8004" -ForegroundColor White
Write-Host "  Synthese Comparative:  http://localhost:8005" -ForegroundColor White
Write-Host "  Audit Logger:          http://localhost:8006" -ForegroundColor White
Write-Host ""
Write-Host "Frontend: Start separately with 'npm run dev' in interface-clinique folder" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each service window to stop" -ForegroundColor Gray
