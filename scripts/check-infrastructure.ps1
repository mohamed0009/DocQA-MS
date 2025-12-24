# ===================================
# Check Infrastructure Services Status
# ===================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Infrastructure Services Health Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allHealthy = $true

# Check PostgreSQL
Write-Host "[PostgreSQL]" -ForegroundColor Cyan
Write-Host "  Port: 5432" -ForegroundColor Gray
Write-Host "  Status: " -NoNewline
try {
    $pgTest = Test-NetConnection -ComputerName localhost -Port 5432 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($pgTest.TcpTestSucceeded) {
        Write-Host "RUNNING" -ForegroundColor Green
    }
    else {
        Write-Host "NOT RUNNING" -ForegroundColor Red
        Write-Host "  Action: Start PostgreSQL service" -ForegroundColor Yellow
        $allHealthy = $false
    }
}
catch {
    Write-Host "NOT INSTALLED" -ForegroundColor Red
    Write-Host "  Action: Install PostgreSQL from https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    $allHealthy = $false
}
Write-Host ""

# Check RabbitMQ
Write-Host "[RabbitMQ]" -ForegroundColor Cyan
Write-Host "  Port: 5672 (AMQP)" -ForegroundColor Gray
Write-Host "  Status: " -NoNewline
try {
    $rabbitTest = Test-NetConnection -ComputerName localhost -Port 5672 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($rabbitTest.TcpTestSucceeded) {
        Write-Host "RUNNING" -ForegroundColor Green
        Write-Host "  Management UI: http://localhost:15672" -ForegroundColor Gray
    }
    else {
        Write-Host "NOT RUNNING" -ForegroundColor Red
        Write-Host "  Action: Start RabbitMQ service" -ForegroundColor Yellow
        $allHealthy = $false
    }
}
catch {
    Write-Host "NOT INSTALLED" -ForegroundColor Red
    Write-Host "  Action: Install RabbitMQ from https://www.rabbitmq.com/download.html" -ForegroundColor Yellow
    $allHealthy = $false
}
Write-Host ""

# Check Redis
Write-Host "[Redis]" -ForegroundColor Cyan
Write-Host "  Port: 6379" -ForegroundColor Gray
Write-Host "  Status: " -NoNewline
try {
    $redisTest = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($redisTest.TcpTestSucceeded) {
        Write-Host "RUNNING" -ForegroundColor Green
    }
    else {
        Write-Host "NOT RUNNING" -ForegroundColor Red
        Write-Host "  Action: Start Redis service" -ForegroundColor Yellow
        $allHealthy = $false
    }
}
catch {
    Write-Host "NOT INSTALLED" -ForegroundColor Red
    Write-Host "  Action: Install Redis from https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    $allHealthy = $false
}
Write-Host ""

# Check Ollama
Write-Host "[Ollama]" -ForegroundColor Cyan
Write-Host "  Port: 11434" -ForegroundColor Gray
Write-Host "  Status: " -NoNewline
try {
    $ollamaTest = Test-NetConnection -ComputerName localhost -Port 11434 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($ollamaTest.TcpTestSucceeded) {
        Write-Host "RUNNING" -ForegroundColor Green
    }
    else {
        Write-Host "NOT RUNNING" -ForegroundColor Red
        Write-Host "  Action: Start Ollama service (run 'ollama serve' in a terminal)" -ForegroundColor Yellow
        $allHealthy = $false
    }
}
catch {
    Write-Host "NOT INSTALLED" -ForegroundColor Red
    Write-Host "  Action: Install Ollama from https://ollama.ai/download" -ForegroundColor Yellow
    $allHealthy = $false
}
Write-Host ""

# Check Python
Write-Host "[Python]" -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Version: $pythonVersion" -ForegroundColor Gray
    Write-Host "  Status: INSTALLED" -ForegroundColor Green
}
catch {
    Write-Host "  Status: NOT INSTALLED" -ForegroundColor Red
    Write-Host "  Action: Install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    $allHealthy = $false
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
if ($allHealthy) {
    Write-Host "All infrastructure services are healthy!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the services:" -ForegroundColor Yellow
    Write-Host "  .\scripts\run-all-services.ps1" -ForegroundColor White
}
else {
    Write-Host "Some services are not ready!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install/start the missing services above" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
