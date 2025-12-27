# ===================================
# Initialize and Run All Services
# Installs dependencies then starts everything
# ===================================

param(
    [switch]$SkipInstall = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MedBot Intelligence - Full Setup & Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ROOT = "C:\Users\HP\Desktop\MedBot-Intelligence"
Set-Location $PROJECT_ROOT

# Services list
$services = @(
    "audit-logger",
    "doc-ingestor",
    "deid",
    "indexeur-semantique",
    "llm-qa-module",
    "synthese-comparative",
    "api-gateway"
)

# Step 1: Create venvs and install dependencies
if (-not $SkipInstall) {
    Write-Host "Step 1: Installing dependencies for all services..." -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($service in $services) {
        $servicePath = Join-Path $PROJECT_ROOT "services\$service"
        $venvPath = Join-Path $servicePath "venv"
        $requirementsPath = Join-Path $servicePath "requirements.txt"
        
        Write-Host "[$service] Installing dependencies..." -ForegroundColor Cyan
        
        # Create venv if it doesn't exist
        if (-not (Test-Path $venvPath)) {
            Write-Host "  Creating virtual environment..." -ForegroundColor Gray
            Set-Location $servicePath
            python -m venv venv
        }
        
        # Install requirements
        if (Test-Path $requirementsPath) {
            Write-Host "  Installing Python packages..." -ForegroundColor Gray
            Set-Location $servicePath
            & "$venvPath\Scripts\python.exe" -m pip install --upgrade pip --quiet 2>&1 | Out-Null
            & "$venvPath\Scripts\pip.exe" install -r requirements.txt --quiet
            Write-Host "  [$service] Dependencies installed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "  [WARNING] No requirements.txt found for $service" -ForegroundColor Yellow
        }
        
        Write-Host ""
    }
    
    Write-Host "All dependencies installed!" -ForegroundColor Green
    Write-Host ""
}
else {
    Write-Host "Skipping dependency installation (--SkipInstall flag set)" -ForegroundColor Yellow
    Write-Host ""
}

# Step 2: Start all services
Write-Host "Step 2: Starting all services..." -ForegroundColor Yellow
Write-Host ""

$serviceConfigs = @(
    @{Name = "audit-logger"; Port = 8006 },
    @{Name = "doc-ingestor"; Port = 8001 },
    @{Name = "deid"; Port = 8002 },
    @{Name = "indexeur-semantique"; Port = 8003 },
    @{Name = "llm-qa-module"; Port = 8004 },
    @{Name = "synthese-comparative"; Port = 8005 },
    @{Name = "api-gateway"; Port = 8000 }
)

foreach ($config in $serviceConfigs) {
    $serviceName = $config.Name
    $servicePort = $config.Port
    $servicePath = Join-Path $PROJECT_ROOT "services\$serviceName"
    $venvPath = Join-Path $servicePath "venv"
    
    Write-Host "[$serviceName] Starting on port $servicePort..." -ForegroundColor Cyan
    
    # Create startup script
    $startupScript = Join-Path $servicePath "start_now.ps1"
    $scriptContent = @"
Set-Location '$servicePath'
& '$venvPath\Scripts\Activate.ps1'
`$env:PYTHONPATH = '$servicePath'
`$env:DATABASE_URL = "sqlite:///./service.db"
`$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:8000,*"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  $serviceName - Port $servicePort" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
uvicorn app.main:app --host 0.0.0.0 --port $servicePort --reload
"@
    Set-Content -Path $startupScript -Value $scriptContent
    
    # Start service in new window
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $startupScript
    
    Write-Host "  Started!" -ForegroundColor Green
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All services are starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Waiting 10 seconds for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Checking service status..." -ForegroundColor Yellow
& "$PROJECT_ROOT\check_all_services_status.ps1"
