#!/usr/bin/env pwsh
# PowerShell Automated Deployment & Monitoring Script
# Fixed version with proper bash handling

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerHost,
    
    [Parameter(Mandatory=$true)]
    [string]$ServerUser = "root",
    
    [string]$LocalModulePath = "D:\01_WORK_PROJECTS\odoo-mcp-server\deals_management",
    [string]$ZipPath = "D:\deals_management_deploy.zip"
)

$ErrorActionPreference = "Continue"

# Configuration
$ServerAddonsPath = "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
$ServerModulePath = "$ServerAddonsPath/deals_management"
$ServerTempPath = "/tmp/deals_management_deploy.zip"
$DbName = "scholarixv2"

Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         Deals Management - Automated Deployment & Monitoring               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# PHASE 1: CREATE ZIP
# ============================================================================
Write-Host "[PHASE 1/5] Creating deployment ZIP..." -ForegroundColor Yellow
Write-Host "────────────────────────────────────────────────────────────────────────────────"

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
    Write-Host "  Removed old ZIP"
}

try {
    Compress-Archive -Path "$LocalModulePath\*" -DestinationPath $ZipPath -Force
    $ZipSize = (Get-Item $ZipPath).Length / 1KB
    Write-Host "✓ ZIP created: $ZipPath ($([math]::Round($ZipSize, 2)) KB)" -ForegroundColor Green
} catch {
    Write-Host "✗ FAILED to create ZIP: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# ============================================================================
# PHASE 2: UPLOAD TO SERVER
# ============================================================================
Write-Host "[PHASE 2/5] Uploading to server..." -ForegroundColor Yellow
Write-Host "────────────────────────────────────────────────────────────────────────────────"

try {
    Write-Host "  Uploading to ${ServerUser}@${ServerHost}:${ServerTempPath}"
    scp $ZipPath "${ServerUser}@${ServerHost}:${ServerTempPath}" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Upload successful" -ForegroundColor Green
    } else {
        throw "Upload failed"
    }
} catch {
    Write-Host "✗ FAILED to upload: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# ============================================================================
# PHASE 3: DEPLOY ON SERVER
# ============================================================================
Write-Host "[PHASE 3/5] Deploying on server..." -ForegroundColor Yellow
Write-Host "────────────────────────────────────────────────────────────────────────────────"

@"
#!/bin/bash
set -e

ADDONS_PATH="$ServerAddonsPath"
MODULE_PATH="$ServerModulePath"
ZIP_FILE="$ServerTempPath"
DB_NAME="$DbName"

echo "=== STEP 1: Delete old module ==="
if [ -d "`$MODULE_PATH" ]; then
    sudo rm -rf "`$MODULE_PATH"
    echo "✓ Old module deleted"
else
    echo "ℹ Module directory not found (fresh install)"
fi
echo ""

echo "=== STEP 2: Extract ZIP ==="
cd "`$ADDONS_PATH"
sudo unzip -q -o "`$ZIP_FILE" || sudo unzip -o "`$ZIP_FILE"

if [ -d "deals_management" ]; then
    echo "✓ Module directory exists"
else
    echo "✗ ERROR: deals_management directory not created!"
    exit 1
fi

if [ ! -f "deals_management/security/ir.model.access.csv" ]; then
    echo "✗ ERROR: Security file not found!"
    exit 1
else
    echo "✓ Security file present"
fi
echo ""

echo "=== STEP 3: Set permissions ==="
sudo chown -R odoo:odoo "deals_management"
sudo chmod -R 755 "deals_management"
echo "✓ Permissions set"
echo ""

echo "=== STEP 4: Clean database ==="
sudo -u postgres psql "`$DB_NAME" << 'SQL_EOF' 2>&1 | grep -E "(DELETE|UPDATE)" || echo "✓ Cleaned"
DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu');
DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window');
DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view');
DELETE FROM ir_model_data WHERE module = 'deals_management';
UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';
SQL_EOF
echo ""

echo "=== STEP 5: Restart Odoo ==="
sudo systemctl restart odoo
echo "Waiting for Odoo to stabilize..."
sleep 5
sudo systemctl is-active --quiet odoo && echo "✓ Odoo is running" || echo "⚠ Checking Odoo status..."
echo ""
echo "✓ SERVER DEPLOYMENT COMPLETE"
"@ | ssh "${ServerUser}@${ServerHost}" 2>&1 | ForEach-Object {
    Write-Host "  $_"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Deployment failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Server deployment successful" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PHASE 4: MONITOR ODOO LOGS
# ============================================================================
Write-Host "[PHASE 4/5] Monitoring Odoo initialization logs..." -ForegroundColor Yellow
Write-Host "────────────────────────────────────────────────────────────────────────────────"

@"
#!/bin/bash
echo "Waiting 10 seconds for Odoo to fully initialize..."
sleep 10

echo ""
echo "=== Last 50 lines of Odoo log ==="
tail -50 /var/odoo/scholarixv2/var/log/odoo.log

echo ""
echo "=== Checking for critical errors ==="
if grep -i "critical\|error" /var/odoo/scholarixv2/var/log/odoo.log | grep -v "payroll\|commission.cancel" | tail -10; then
    echo "⚠ Found errors in log"
else
    echo "✓ No critical errors detected"
fi
"@ | ssh "${ServerUser}@${ServerHost}" 2>&1 | ForEach-Object {
    Write-Host "  $_"
}

Write-Host "✓ Log monitoring complete" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PHASE 5: VERIFY DEPLOYMENT
# ============================================================================
Write-Host "[PHASE 5/5] Verifying module files..." -ForegroundColor Yellow
Write-Host "────────────────────────────────────────────────────────────────────────────────"

@"
#!/bin/bash
echo "=== Module directory structure ==="
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management/

echo ""
echo "=== Checking critical files ==="
for file in __manifest__.py __init__.py security/ir.model.access.csv models/__init__.py views/deals_views.xml views/commission_views.xml views/deals_menu.xml; do
    if [ -f "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management/\$file" ]; then
        echo "✓ \$file"
    else
        echo "✗ MISSING: \$file"
    fi
done

echo ""
echo "✓ VERIFICATION COMPLETE"
"@ | ssh "${ServerUser}@${ServerHost}" 2>&1 | ForEach-Object {
    Write-Host "  $_"
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ✓ DEPLOYMENT COMPLETE!                                 ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT: Install the module in Odoo UI" -ForegroundColor Yellow
Write-Host "  1. Login to https://erp.sgctech.ai" -ForegroundColor White
Write-Host "  2. Go to Apps" -ForegroundColor White
Write-Host "  3. Update Apps List" -ForegroundColor White
Write-Host "  4. Search 'Deals Management'" -ForegroundColor White
Write-Host "  5. Click Install" -ForegroundColor White
Write-Host ""
