# ===================================
# Initialize PostgreSQL Databases for MedBot Intelligence
# Run this script to create all required databases
# ===================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MedBot Intelligence - Database Initialization" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# PostgreSQL connection parameters
$PGUSER = "docqa_admin"
$PGPASSWORD = "change_this_secure_password"
$PGHOST = "localhost"
$PGPORT = "5432"

# Set environment variable for password
$env:PGPASSWORD = $PGPASSWORD

# List of databases to create
$databases = @(
    "doc_ingestor",
    "deid",
    "indexeur",
    "llm_qa",
    "synthese",
    "audit"
)

Write-Host "Checking PostgreSQL connection..." -ForegroundColor Yellow
try {
    $result = psql -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Cannot connect to PostgreSQL!" -ForegroundColor Red
        Write-Host "Please ensure PostgreSQL is running on localhost:5432" -ForegroundColor Red
        Write-Host "And that user '$PGUSER' exists with password configured" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ PostgreSQL connection successful" -ForegroundColor Green
} catch {
    Write-Host "ERROR: PostgreSQL is not installed or not running!" -ForegroundColor Red
    Write-Host "Please install PostgreSQL first: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Creating databases..." -ForegroundColor Yellow

foreach ($db in $databases) {
    Write-Host "  Creating database: $db..." -NoNewline
    
    # Check if database exists
    $checkDb = psql -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$db'" 2>&1
    
    if ($checkDb -eq "1") {
        Write-Host " [ALREADY EXISTS]" -ForegroundColor Yellow
    } else {
        # Create database
        $createDb = psql -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -c "CREATE DATABASE $db;" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " [CREATED]" -ForegroundColor Green
        } else {
            Write-Host " [FAILED]" -ForegroundColor Red
            Write-Host "Error: $createDb" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database initialization complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created databases:" -ForegroundColor Yellow
foreach ($db in $databases) {
    Write-Host "  - $db" -ForegroundColor White
}
Write-Host ""
Write-Host "You can now start the microservices!" -ForegroundColor Green
