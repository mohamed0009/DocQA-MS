Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\llm-qa-module'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\llm-qa-module\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\llm-qa-module'
$env:DATABASE_URL = "sqlite:///./service.db"
$env:LLM_PROVIDER = "mock"
$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:8000,*"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service: llm-qa-module" -ForegroundColor Cyan
Write-Host "Port: 8004" -ForegroundColor Cyan
Write-Host "Mode: STANDALONE (No RabbitMQ/Ollama)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting llm-qa-module on port 8004..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
