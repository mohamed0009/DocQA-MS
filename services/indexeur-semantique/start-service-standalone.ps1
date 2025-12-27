Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\indexeur-semantique'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\indexeur-semantique\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\indexeur-semantique'
$env:DATABASE_URL = "sqlite:///./service.db"
$env:LLM_PROVIDER = "mock"
$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:8000,*"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service: indexeur-semantique" -ForegroundColor Cyan
Write-Host "Port: 8003" -ForegroundColor Cyan
Write-Host "Mode: STANDALONE (No RabbitMQ/Ollama)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting indexeur-semantique on port 8003..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
