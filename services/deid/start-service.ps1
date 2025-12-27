Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\deid'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\deid\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\deid'
Write-Host "Installing dependencies for deid..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Starting deid on port 8002..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
