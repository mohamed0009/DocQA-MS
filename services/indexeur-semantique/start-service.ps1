Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\indexeur-semantique'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\indexeur-semantique\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\indexeur-semantique'
Write-Host "Installing dependencies for indexeur-semantique..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Starting indexeur-semantique on port 8003..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
