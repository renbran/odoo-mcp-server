# Deploy Deal Management Module

# Configuration
$ServerIP = "erp.sgctech.ai"
$OdooAddonsPath = "/var/lib/odoo/addons"
$ModuleName = "deal_management"
$ModulePath = ".\$ModuleName"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Deal Management Module Deployment" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Verify module exists
if (-not (Test-Path $ModulePath)) {
    Write-Host "❌ Error: $ModuleName directory not found" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Module found: $ModuleName" -ForegroundColor Cyan
Write-Host "📍 Source: $(Get-Item $ModulePath | Select-Object -ExpandProperty FullName)" -ForegroundColor Cyan
Write-Host "🎯 Target: $ServerIP" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload module
Write-Host "📤 Uploading module to server..." -ForegroundColor Yellow

# Create tar file
Write-Host "   Creating archive..." -ForegroundColor Gray
tar -czf "$ModuleName.tar.gz" $ModuleName

# Upload via SCP
Write-Host "   Transferring via SCP..." -ForegroundColor Gray
scp -r $ModulePath root@${ServerIP}:${OdooAddonsPath}/

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Upload failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Module uploaded" -ForegroundColor Green
Write-Host ""

# Step 2: Fix permissions
Write-Host "🔐 Fixing permissions..." -ForegroundColor Yellow
ssh root@${ServerIP} "chown -R odoo:odoo $OdooAddonsPath/$ModuleName"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Permission fix failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Permissions fixed" -ForegroundColor Green
Write-Host ""

# Step 3: Restart Odoo
Write-Host "🔄 Restarting Odoo..." -ForegroundColor Yellow
ssh root@${ServerIP} "systemctl restart odoo"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Restart failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Odoo restarted" -ForegroundColor Green
Write-Host ""

# Step 4: Summary
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Open: https://$ServerIP/scholarixv2" -ForegroundColor Gray
Write-Host "2. Go to: Settings > Apps > Update App List" -ForegroundColor Gray
Write-Host "3. Search: 'Deal Management'" -ForegroundColor Gray
Write-Host "4. Click: Install" -ForegroundColor Gray
Write-Host ""
Write-Host "THEN TEST:" -ForegroundColor Yellow
Write-Host "1. Go to: Sales > Deals" -ForegroundColor Gray
Write-Host "2. Create a test deal" -ForegroundColor Gray
Write-Host "3. Test workflow buttons" -ForegroundColor Gray
Write-Host ""

# Cleanup
Remove-Item "$ModuleName.tar.gz" -ErrorAction SilentlyContinue
