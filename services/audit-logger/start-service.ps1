Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\audit-logger'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\audit-logger\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\audit-logger'
Write-Host "Installing dependencies for audit-logger..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Starting audit-logger on port 8006..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload
