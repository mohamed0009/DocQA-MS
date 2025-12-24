# MedBot Intelligence - Run All Services Locally
# This script starts all microservices without Docker

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  MedBot Intelligence - Local Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Service configuration
$services = @(
    @{Name = "doc-ingestor"; Port = 8001; Path = "services\doc-ingestor" }
    @{Name = "deid"; Port = 8002; Path = "services\deid" }
    @{Name = "indexeur-semantique"; Port = 8003; Path = "services\indexeur-semantique" }
    @{Name = "llm-qa-module"; Port = 8004; Path = "services\llm-qa-module" }
    @{Name = "synthese-comparative"; Port = 8005; Path = "services\synthese-comparative" }
    @{Name = "audit-logger"; Port = 8006; Path = "services\audit-logger" }
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Starting All Services" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Start all services
foreach ($service in $services) {
    $serviceName = $service.Name
    $servicePath = $service.Path
    $port = $service.Port
    
    Write-Host "Starting $serviceName on port $port..." -ForegroundColor Yellow
    
    $appPath = Join-Path $servicePath "app"
    if (Test-Path $appPath) {
        # Start the service in a new PowerShell window
        $title = "MedBot - $serviceName"
        $command = "cd '$servicePath'; uvicorn app.main:app --host 0.0.0.0 --port $port --reload"
        
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '$title' -ForegroundColor Cyan; $command" -WindowStyle Normal
        
        Write-Host "  Started on http://localhost:$port" -ForegroundColor Green
        Start-Sleep -Milliseconds 500
    }
    else {
        Write-Host "  App directory not found!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  All Services Started!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services running on:" -ForegroundColor Cyan
foreach ($service in $services) {
    $name = $service.Name.PadRight(25)
    $url = "http://localhost:$($service.Port)"
    Write-Host "  $name $url" -ForegroundColor White
}
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in each service window to stop" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
