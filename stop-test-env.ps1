# Stop Odoo 17 Test Environment

Write-Host "🛑 Stopping Odoo 17 Test Environment..." -ForegroundColor Yellow
Write-Host ""

docker-compose stop

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Services stopped successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Data has been preserved in Docker volumes." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To restart: .\start-test-env.ps1" -ForegroundColor White
    Write-Host "To remove all data: docker-compose down -v" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Failed to stop services" -ForegroundColor Red
    exit 1
}
