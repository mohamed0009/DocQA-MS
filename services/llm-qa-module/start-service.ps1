Set-Location 'C:\Users\HP\Desktop\MedBot-Intelligence\services\llm-qa-module'
& 'C:\Users\HP\Desktop\MedBot-Intelligence\services\llm-qa-module\venv\Scripts\Activate.ps1'
$env:PYTHONPATH = 'C:\Users\HP\Desktop\MedBot-Intelligence\services\llm-qa-module'
Write-Host "Installing dependencies for llm-qa-module..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Starting llm-qa-module on port 8004..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
