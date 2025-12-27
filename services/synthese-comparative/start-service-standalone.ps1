Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\synthese-comparative'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\synthese-comparative\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\synthese-comparative'
$env:DATABASE_URL = "sqlite:///./service.db"
$env:LLM_PROVIDER = "mock"
$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:8000,*"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service: synthese-comparative" -ForegroundColor Cyan
Write-Host "Port: 8005" -ForegroundColor Cyan
Write-Host "Mode: STANDALONE (No RabbitMQ/Ollama)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting synthese-comparative on port 8005..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
