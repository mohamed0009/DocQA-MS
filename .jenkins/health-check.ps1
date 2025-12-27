# ===========================================
# Jenkins Pipeline Health Check Script (PowerShell)
# ===========================================
# This script validates that the Jenkins pipeline
# can successfully build and test the project locally

Write-Host "🔍 Jenkins Pipeline Health Check" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

$PASSED = 0
$FAILED = 0

function Check-Command {
    param([string]$CommandName)
    
    if (Get-Command $CommandName -ErrorAction SilentlyContinue) {
        Write-Host "✅ $CommandName is installed" -ForegroundColor Green
        $script:PASSED++
        return $true
    }
    else {
        Write-Host "❌ $CommandName is not installed" -ForegroundColor Red
        $script:FAILED++
        return $false
    }
}

# 1. Check Prerequisites
Write-Host "1️⃣  Checking Prerequisites..." -ForegroundColor Yellow
Write-Host "----------------------------"
Check-Command "docker"
Check-Command "docker-compose"
Check-Command "python"
Check-Command "pip"
Check-Command "node"
Check-Command "npm"
Check-Command "git"
Write-Host ""

# 2. Check Docker Access
Write-Host "2️⃣  Checking Docker Access..." -ForegroundColor Yellow
Write-Host "----------------------------"
try {
    docker ps | Out-Null
    Write-Host "✅ Docker daemon is running" -ForegroundColor Green
    $PASSED++
}
catch {
    Write-Host "❌ Cannot access Docker daemon" -ForegroundColor Red
    Write-Host "   Make sure Docker is running and you have permissions" -ForegroundColor Yellow
    $FAILED++
}
Write-Host ""

# 3. Validate Jenkinsfile
Write-Host "3️⃣  Validating Jenkinsfile..." -ForegroundColor Yellow
Write-Host "----------------------------"
if (Test-Path "Jenkinsfile") {
    Write-Host "✅ Jenkinsfile exists" -ForegroundColor Green
    $PASSED++
    
    $content = Get-Content "Jenkinsfile" -Raw
    if ($content -match "pipeline" -and $content -match "stages" -and $content -match "post") {
        Write-Host "✅ Jenkinsfile has valid structure" -ForegroundColor Green
        $PASSED++
    }
    else {
        Write-Host "❌ Jenkinsfile structure seems invalid" -ForegroundColor Red
        $FAILED++
    }
}
else {
    Write-Host "❌ Jenkinsfile not found" -ForegroundColor Red
    $FAILED++
}
Write-Host ""

# 4. Check Service Dependencies
Write-Host "4️⃣  Checking Service Dependencies..." -ForegroundColor Yellow
Write-Host "------------------------------------"

$services = @("api-gateway", "doc-ingestor", "deid", "indexeur-semantique", 
    "llm-qa-module", "synthese-comparative", "audit-logger", "ml-predictor")

foreach ($service in $services) {
    if (Test-Path "services\$service\requirements.txt") {
        Write-Host "✅ services\$service\requirements.txt" -ForegroundColor Green
        $PASSED++
    }
    else {
        Write-Host "❌ services\$service\requirements.txt missing" -ForegroundColor Red
        $FAILED++
    }
}
Write-Host ""

# 5. Check Frontend Dependencies
Write-Host "5️⃣  Checking Frontend Dependencies..." -ForegroundColor Yellow
Write-Host "-------------------------------------"
if (Test-Path "interface-clinique\package.json") {
    Write-Host "✅ interface-clinique\package.json exists" -ForegroundColor Green
    $PASSED++
}
else {
    Write-Host "❌ interface-clinique\package.json missing" -ForegroundColor Red
    $FAILED++
}
Write-Host ""

# 6. Verify Docker Compose Configuration
Write-Host "6️⃣  Verifying Docker Compose..." -ForegroundColor Yellow
Write-Host "-------------------------------"
try {
    docker-compose config | Out-Null
    Write-Host "✅ docker-compose.yml is valid" -ForegroundColor Green
    $PASSED++
}
catch {
    Write-Host "❌ docker-compose.yml has errors" -ForegroundColor Red
    $FAILED++
}
Write-Host ""

# 7. Check Test Files
Write-Host "7️⃣  Checking Test Files..." -ForegroundColor Yellow
Write-Host "-------------------------"
if (Test-Path "services\ml-predictor\tests") {
    Write-Host "✅ ml-predictor tests exist" -ForegroundColor Green
    $PASSED++
}
else {
    Write-Host "⚠️  ml-predictor tests not found" -ForegroundColor Yellow
}

if (Test-Path "services\indexeur-semantique\tests") {
    Write-Host "✅ indexeur-semantique tests exist" -ForegroundColor Green
    $PASSED++
}
else {
    Write-Host "⚠️  indexeur-semantique tests not found" -ForegroundColor Yellow
}
Write-Host ""

# 8. Check Jenkins Helper Files
Write-Host "8️⃣  Checking Jenkins Configuration..." -ForegroundColor Yellow
Write-Host "--------------------------------------"
if (Test-Path ".jenkins\helpers.groovy") {
    Write-Host "✅ Jenkins helpers library exists" -ForegroundColor Green
    $PASSED++
}
else {
    Write-Host "❌ .jenkins\helpers.groovy missing" -ForegroundColor Red
    $FAILED++
}

if (Test-Path ".jenkins\ENV_CONFIG.md") {
    Write-Host "✅ Environment config documentation exists" -ForegroundColor Green
    $PASSED++
}
else {
    Write-Host "⚠️  .jenkins\ENV_CONFIG.md missing" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "📊 Health Check Summary" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Passed: $PASSED" -ForegroundColor Green
Write-Host "Failed: $FAILED" -ForegroundColor Red
Write-Host ""

if ($FAILED -eq 0) {
    Write-Host "✅ All checks passed! Jenkins pipeline should work correctly." -ForegroundColor Green
    exit 0
}
else {
    Write-Host "❌ Some checks failed. Please fix the issues above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  - Install missing tools (Docker, Python, Node.js, etc.)"
    Write-Host "  - Ensure Docker Desktop is running"
    Write-Host "  - Check file paths are correct"
    Write-Host "  - Review docker-compose.yml syntax"
    exit 1
}
