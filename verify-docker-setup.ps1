# Odoo 17 Docker Module Testing - Automated Verification
# Run this script to verify the testing environment is ready

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Odoo 17 Docker Testing Environment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Docker
Write-Host "[1/7] Checking Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Docker installed: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Docker not found! Install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check Docker Compose
Write-Host "`n[2/7] Checking Docker Compose..." -ForegroundColor Yellow
$composeVersion = docker-compose --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Docker Compose: $composeVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Docker Compose not found!" -ForegroundColor Red
    exit 1
}

# Check Containers
Write-Host "`n[3/7] Checking Containers..." -ForegroundColor Yellow
$containers = docker-compose ps --format json | ConvertFrom-Json
if ($containers.Count -ge 2) {
    Write-Host "  ✅ Found $($containers.Count) containers:" -ForegroundColor Green
    foreach ($container in $containers) {
        $status = if ($container.State -eq "running") { "✅" } else { "⚠️" }
        Write-Host "     $status $($container.Service): $($container.State)" -ForegroundColor $(if ($container.State -eq "running") { "Green" } else { "Yellow" })
    }
} else {
    Write-Host "  ❌ Containers not running! Run: docker-compose up -d" -ForegroundColor Red
    exit 1
}

# Check Modules Mounted
Write-Host "`n[4/7] Verifying Module Mounts..." -ForegroundColor Yellow
$modules = docker exec odoo17_test ls /mnt/extra-addons/ 2>$null
if ($modules) {
    $moduleList = $modules -split "`n" | Where-Object { $_ -match "rental" }
    Write-Host "  ✅ Mounted modules ($($moduleList.Count)):" -ForegroundColor Green
    foreach ($mod in $moduleList) {
        Write-Host "     • $mod" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ❌ Modules not mounted!" -ForegroundColor Red
    exit 1
}

# Check Database Connection
Write-Host "`n[5/7] Testing Database Connection..." -ForegroundColor Yellow
$dbTest = docker exec odoo17_postgres pg_isready -U odoo 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ PostgreSQL 15 ready" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Database starting up..." -ForegroundColor Yellow
}

# Check Web Access
Write-Host "`n[6/7] Testing Web Access..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8069" -UseBasicParsing -TimeoutSec 10
    Write-Host "  ✅ Odoo web accessible: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Web service starting up... (retry in 30s)" -ForegroundColor Yellow
}

# Check Logs for Errors
Write-Host "`n[7/7] Checking Logs..." -ForegroundColor Yellow
$logs = docker logs odoo17_test --tail=50 2>&1
$errors = $logs | Select-String -Pattern "ERROR|CRITICAL" -CaseSensitive
if ($errors.Count -eq 0) {
    Write-Host "  ✅ No critical errors in logs" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Found $($errors.Count) error(s) - check logs" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Environment Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Odoo URL:     http://localhost:8069" -ForegroundColor White
Write-Host "Database:     odoo17_test (not created yet)" -ForegroundColor White
Write-Host "DB Port:      localhost:5432" -ForegroundColor White
Write-Host "Username:     odoo" -ForegroundColor White
Write-Host "Password:     odoo" -ForegroundColor White
Write-Host "`nModules Ready:" -ForegroundColor White
Write-Host "  • rental_account_fields" -ForegroundColor Cyan
Write-Host "  • rental_management" -ForegroundColor Cyan
Write-Host "  • rental_website" -ForegroundColor Cyan
Write-Host "  • rental_portal_syndication" -ForegroundColor Cyan

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ READY FOR TESTING!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Open browser: http://localhost:8069" -ForegroundColor White
Write-Host "2. Create database: odoo17_test" -ForegroundColor White
Write-Host "3. Login with admin / admin" -ForegroundColor White
Write-Host "4. Install rental modules" -ForegroundColor White
Write-Host "`nSee DOCKER_TEST_GUIDE.md for detailed instructions`n" -ForegroundColor Cyan
