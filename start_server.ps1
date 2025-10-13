# RCM_PRICE - Start Server Script
# Automatically stops old instances and starts fresh server

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "    RCM_PRICE - AI Promotion System" -ForegroundColor Green
Write-Host "    Starting API Server..." -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with your configuration" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Required variables:" -ForegroundColor Yellow
    Write-Host "  MONGODB_URL=your_mongodb_url" -ForegroundColor White
    Write-Host "  DATABASE_NAME=your_database_name" -ForegroundColor White
    Write-Host "  GEMINI_API_KEY=your_api_key" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Stop any running Python instances on port 8000
Write-Host "[1/4] Stopping existing server instances..." -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Host "  Stopped $($pythonProcesses.Count) Python process(es)" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "  No existing instances found" -ForegroundColor Green
}

# Test MongoDB connection
Write-Host ""
Write-Host "[2/4] Testing MongoDB connection..." -ForegroundColor Yellow
python test_connection.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: MongoDB connection failed!" -ForegroundColor Red
    Write-Host "Please check your MONGODB_URL in .env file" -ForegroundColor Yellow
    exit 1
}

# Check required packages
Write-Host ""
Write-Host "[3/4] Checking required packages..." -ForegroundColor Yellow
$requiredPackages = @("fastapi", "uvicorn", "pymongo", "pandas", "numpy")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    python -c "import $package" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "  Missing packages: $($missingPackages -join ', ')" -ForegroundColor Red
    Write-Host "  Run: pip install -r requirements-minimal.txt" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "  All required packages installed" -ForegroundColor Green
}

# Start server
Write-Host ""
Write-Host "[4/4] Starting API server..." -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will start at: http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

python app/main.py
