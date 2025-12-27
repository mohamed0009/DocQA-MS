# Eureka Integration - Quick Setup Script (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📋 Eureka Service Discovery Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "🔍 Checking Docker..." -ForegroundColor Yellow
try {
    docker info > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Build Eureka Server
Write-Host "🏗️  Building Eureka Server..." -ForegroundColor Yellow
docker-compose build eureka-server
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Eureka Server" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Eureka Server built successfully" -ForegroundColor Green
Write-Host ""

# Start Eureka Server
Write-Host "🚀 Starting Eureka Server..." -ForegroundColor Yellow
docker-compose up -d eureka-server
Write-Host "⏳ Waiting 40 seconds for Eureka to fully start..." -ForegroundColor Yellow
Start-Sleep -Seconds 40

# Check Eureka health
Write-Host "🏥 Checking Eureka health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8761/actuator/health" -Method Get -TimeoutSec 5
    if ($response.status -eq "UP") {
        Write-Host "✅ Eureka Server is UP and healthy" -ForegroundColor Green
    } else {
        throw "Eureka not healthy"
    }
} catch {
    Write-Host "❌ Eureka Server is not healthy" -ForegroundColor Red
    Write-Host "Check logs: docker-compose logs eureka-server" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Start services with Eureka
Write-Host "🚀 Starting services with Eureka integration..." -ForegroundColor Yellow
docker-compose up -d api-gateway indexeur-semantique

Write-Host "⏳ Waiting 30 seconds for services to register..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Open Eureka Dashboard: http://localhost:8761" -ForegroundColor White
Write-Host "   2. Run tests: python test_eureka_integration.py" -ForegroundColor White
Write-Host "   3. Check API Gateway: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Verify Services:" -ForegroundColor Yellow
Write-Host "   curl http://localhost:8761/eureka/apps" -ForegroundColor White
Write-Host ""
