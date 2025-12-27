Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\api-gateway'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\api-gateway\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\api-gateway'
Write-Host "Installing dependencies for api-gateway..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Starting api-gateway on port 8000..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
