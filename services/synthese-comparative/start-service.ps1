Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\synthese-comparative'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\synthese-comparative\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\synthese-comparative'
Write-Host "Installing dependencies for synthese-comparative..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Starting synthese-comparative on port 8005..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
