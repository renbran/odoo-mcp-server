#!/usr/bin/env pwsh

param(
    [string]$ServerHost = "erp.sgctech.ai",
    [string]$ServerUser = "root"
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Deals Management - Automated Deployment & Log Monitoring" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Phase 1: Create ZIP
Write-Host "[PHASE 1/3] Creating deployment ZIP..." -ForegroundColor Yellow
$ZipPath = "D:\deals_management_deploy.zip"
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
Compress-Archive -Path "D:\01_WORK_PROJECTS\odoo-mcp-server\deals_management\*" -DestinationPath $ZipPath -Force
$ZipSize = [math]::Round((Get-Item $ZipPath).Length / 1KB, 2)
Write-Host "OK: ZIP created ($ZipSize KB)" -ForegroundColor Green
Write-Host ""

# Phase 2: Upload
Write-Host "[PHASE 2/3] Uploading to server..." -ForegroundColor Yellow
scp $ZipPath "${ServerUser}@${ServerHost}:/tmp/deals_management_deploy.zip" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Upload successful" -ForegroundColor Green
} else {
    Write-Host "FAIL: Upload failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Phase 3: Deploy and Monitor
Write-Host "[PHASE 3/3] Deploying and monitoring logs..." -ForegroundColor Yellow
Write-Host "======================================================================"
Write-Host ""

scp "D:\01_WORK_PROJECTS\odoo-mcp-server\deploy.sh" "${ServerUser}@${ServerHost}:/tmp/" 2>$null
ssh "${ServerUser}@${ServerHost}" "bash /tmp/deploy.sh" 2>&1 | ForEach-Object {
    if ($_ -match "^OK:" -or $_ -match "^===") {
        Write-Host $_ -ForegroundColor Green
    } elseif ($_ -match "FAIL|ERROR|error") {
        Write-Host $_ -ForegroundColor Red
    } elseif ($_ -match "^\[") {
        Write-Host $_ -ForegroundColor Yellow
    } else {
        Write-Host $_
    }
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT: Install module in Odoo UI" -ForegroundColor Yellow
Write-Host "  1. Login to https://erp.sgctech.ai" -ForegroundColor White
Write-Host "  2. Go to Apps menu" -ForegroundColor White
Write-Host "  3. Click Update Apps List" -ForegroundColor White
Write-Host "  4. Search for Deals Management" -ForegroundColor White
Write-Host "  5. Click Install" -ForegroundColor White
Write-Host ""
