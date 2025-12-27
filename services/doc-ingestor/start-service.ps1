Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\doc-ingestor'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\doc-ingestor\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\doc-ingestor'
Write-Host "Installing dependencies for doc-ingestor..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Starting doc-ingestor on port 8001..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
