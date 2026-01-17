# Quick Start - Odoo 17 Docker Test Environment
Write-Host "Starting Odoo 17 Test Environment..." -ForegroundColor Cyan
Write-Host ""

$dockerPath = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"

if (-not (Test-Path $dockerPath)) {
    Write-Host "Docker not found!" -ForegroundColor Red
    exit 1
}

try {
    & $dockerPath info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running! Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "Starting services..." -ForegroundColor Cyan
& $dockerPath compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access Odoo at: http://localhost:8069" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "1. Open http://localhost:8069" -ForegroundColor Gray
    Write-Host "2. Create database: odoo17_test" -ForegroundColor Gray
    Write-Host "3. Install 'Deal Report & Commissions'" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "Failed to start services" -ForegroundColor Red
    exit 1
}
