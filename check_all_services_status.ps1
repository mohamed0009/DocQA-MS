Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MedBot Intelligence - Services Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check running processes
Write-Host "Python/Uvicorn Processes:" -ForegroundColor Yellow
$pythonProcs = Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn" }
if ($pythonProcs) {
    $pythonProcs | Select-Object ProcessName, Id, @{Name = "CPU(s)"; Expression = { $_.CPU } }, @{Name = "Memory(MB)"; Expression = { [math]::Round($_.WorkingSet64 / 1MB, 2) } } | Format-Table -AutoSize
}
else {
    Write-Host "  No Python/Uvicorn processes running" -ForegroundColor Red
}

Write-Host ""
Write-Host "Port Status:" -ForegroundColor Yellow

$services = @(
    @{Name = "API Gateway"; Port = 8000 },
    @{Name = "Doc Ingestor"; Port = 8001 },
    @{Name = "DeID"; Port = 8002 },
    @{Name = "Indexeur Semantique"; Port = 8003 },
    @{Name = "LLM QA Module"; Port = 8004 },
    @{Name = "Synthese Comparative"; Port = 8005 },
    @{Name = "Audit Logger"; Port = 8006 },
    @{Name = "Frontend (Next.js)"; Port = 3000 }
)

foreach ($service in $services) {
    $port = $service.Port
    $name = $service.Name
    
    $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    
    if ($connection) {
        Write-Host ("  [OK] {0,-25} Port {1} - LISTENING (PID: {2})" -f $name, $port, $connection.OwningProcess) -ForegroundColor Green
    }
    else {
        Write-Host ("  [X]  {0,-25} Port {1} - NOT LISTENING" -f $name, $port) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "PowerShell Windows:" -ForegroundColor Yellow
$psCount = (Get-Process powershell -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "  Total PowerShell processes: $psCount" -ForegroundColor White

Write-Host ""
Write-Host "Testing HTTP Endpoints:" -ForegroundColor Yellow

# Test a few key endpoints
$endpoints = @(
    @{Url = "http://localhost:8000/health"; Name = "API Gateway" },
    @{Url = "http://localhost:8001/health"; Name = "Doc Ingestor" },
    @{Url = "http://localhost:3000"; Name = "Frontend" }
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host ("  [OK] {0,-20} HTTP {1}" -f $endpoint.Name, $response.StatusCode) -ForegroundColor Green
    }
    catch {
        Write-Host ("  [X]  {0,-20} NOT RESPONDING" -f $endpoint.Name) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
