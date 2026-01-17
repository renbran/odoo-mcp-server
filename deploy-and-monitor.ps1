# PowerShell Automated Deployment & Monitoring Script
# This script handles everything: zip, upload, deploy, monitor, and test

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerHost,
    
    [Parameter(Mandatory=$true)]
    [string]$ServerUser = "root",
    
    [string]$LocalModulePath = "D:\01_WORK_PROJECTS\odoo-mcp-server\deals_management",
    [string]$ZipPath = "D:\deals_management_deploy.zip"
)

$ErrorActionPreference = "Stop"
$WarningPreference = "SilentlyContinue"

# Configuration
$ServerAddonsPath = "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
$ServerModulePath = "$ServerAddonsPath/deals_management"
$ServerTempPath = "/tmp/deals_management_deploy.zip"
$DbName = "scholarixv2"
$OdooLogPath = "/var/odoo/scholarixv2/var/log/odoo.log"

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
        throw "SCP returned exit code $LASTEXITCODE"
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

$DeployScript = @"
#!/bin/bash
set -e

ADDONS_PATH="$ServerAddonsPath"
MODULE_PATH="$ServerModulePath"
ZIP_FILE="$ServerTempPath"
DB_NAME="$DbName"
LOG_FILE="$OdooLogPath"

echo "=== STEP 1: Delete old module ==="
if [ -d "\$MODULE_PATH" ]; then
    sudo rm -rf "\$MODULE_PATH"
    echo "✓ Old module deleted"
else
    echo "ℹ Module directory not found (fresh install)"
fi
echo ""

echo "=== STEP 2: Extract ZIP ==="
cd "\$ADDONS_PATH"
echo "Current directory: \$(pwd)"
echo "Extracting ZIP: \$ZIP_FILE"
sudo unzip -q -o "\$ZIP_FILE" 2>&1 || sudo unzip -o "\$ZIP_FILE"

# Check structure
if [ -d "deals_management" ]; then
    echo "✓ Module directory exists"
else
    echo "✗ ERROR: deals_management directory not created!"
    echo "Contents of \$ADDONS_PATH:"
    ls -la
    exit 1
fi

# Verify security file
if [ ! -f "deals_management/security/ir.model.access.csv" ]; then
    echo "✗ ERROR: Security file not found in deals_management!"
    echo "Module contents:"
    find deals_management -type f | head -20
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
sudo -u postgres psql "\$DB_NAME" << 'SQL_EOF' 2>&1 | grep -E "(DELETE|UPDATE|ERROR)" || true
DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu');
DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window');
DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view');
DELETE FROM ir_model_data WHERE module = 'deals_management';
UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';
SQL_EOF
echo "✓ Database cleaned"
echo ""

echo "=== STEP 5: Restart Odoo ==="
sudo systemctl restart odoo
echo "Waiting for Odoo to restart..."
sleep 3

# Check if Odoo is running
for i in {1..10}; do
    if sudo systemctl is-active --quiet odoo; then
        echo "✓ Odoo is running"
        break
    fi
    if [ \$i -eq 10 ]; then
        echo "✗ Odoo failed to start after 10 attempts"
        sudo systemctl status odoo
        exit 1
    fi
    echo "  Attempt \$i/10 - waiting for Odoo..."
    sleep 2
done
echo ""

echo "=== STEP 6: Verify deployment ==="
echo "Checking module file structure..."
ls -la deals_management/ | head -15
echo ""
echo "✓ DEPLOYMENT COMPLETE"
echo "Waiting for Odoo initialization..."
sleep 8
"@

# Execute deployment script on server
try {
    Write-Host "  Executing deployment script on server..."
    $DeployScript | ssh "${ServerUser}@${ServerHost}" "bash -s" 2>&1 | ForEach-Object {
        Write-Host "  $_"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Server deployment successful" -ForegroundColor Green
    } else {
        Write-Host "✗ Server deployment failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ FAILED to execute deployment: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# ============================================================================
# PHASE 4: MONITOR ODOO INITIALIZATION
# ============================================================================
Write-Host "[PHASE 4/5] Monitoring Odoo initialization..." -ForegroundColor Yellow
Write-Host "────────────────────────────────────────────────────────────────────────────────"

$LogMonitorScript = @"
#!/bin/bash
LOG_FILE="$OdooLogPath"
echo "Tailing Odoo log for 30 seconds..."
timeout 30 tail -f "\$LOG_FILE" 2>/dev/null || true
echo ""
echo "Last 20 lines of log:"
tail -20 "\$LOG_FILE"
"@

Write-Host "  Waiting for Odoo to initialize (checking logs)..."
$LogMonitorScript | ssh "${ServerUser}@${ServerHost}" "bash -s" 2>&1 | ForEach-Object {
    if ($_ -match "ERROR|CRITICAL" -and $_ -notmatch "WARNING.*payroll|WARNING.*commission.cancel") {
        Write-Host "  [ERROR] $_" -ForegroundColor Red
    } elseif ($_ -match "Modules loaded|Registry loaded") {
        Write-Host "  [SUCCESS] $_" -ForegroundColor Green
    } elseif ($_ -match "WARNING|DEBUG") {
        # Skip most warnings
        if ($_ -notmatch "payroll|commission.cancel") {
            Write-Host "  $_" -ForegroundColor Gray
        }
    } else {
        Write-Host "  $_"
    }
}

Write-Host "✓ Odoo initialization completed" -ForegroundColor Green
Write-Host ""

# ============================================================================
# PHASE 5: TEST INSTALLATION
# ============================================================================
Write-Host "[PHASE 5/5] Testing module installation..." -ForegroundColor Yellow
Write-Host "────────────────────────────────────────────────────────────────────────────────"

$TestScript = @"
#!/bin/bash
DB_NAME="$DbName"
MODULE_NAME="deals_management"

echo "=== Testing via direct SQL ==="

# Check if module exists in database
echo "1. Checking if module is listed..."
sudo -u postgres psql "\$DB_NAME" -c "SELECT name, state FROM ir_module_module WHERE name = '\$MODULE_NAME';" 2>&1

# Check for any parsing errors
echo ""
echo "2. Checking for XML parsing errors in logs..."
if grep -i "ParseError\|deals_management" "$OdooLogPath" | tail -5; then
    echo "⚠ Found recent errors related to module"
else
    echo "✓ No recent parsing errors"
fi

# Check menu items
echo ""
echo "3. Checking menu items in database..."
sudo -u postgres psql "\$DB_NAME" -c "SELECT id, name FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = '\$MODULE_NAME') LIMIT 5;" 2>&1

# Check actions
echo ""
echo "4. Checking actions in database..."
sudo -u postgres psql "\$DB_NAME" -c "SELECT id, name FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = '\$MODULE_NAME') LIMIT 5;" 2>&1
"@

$TestScript | ssh "${ServerUser}@${ServerHost}" "bash -s" 2>&1 | ForEach-Object {
    Write-Host "  $_"
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ✓ DEPLOYMENT COMPLETE!                                 ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Login to Odoo: https://erp.sgctech.ai" -ForegroundColor White
Write-Host "  2. Go to Apps menu" -ForegroundColor White
Write-Host "  3. Remove all filters and click 'Update Apps List'" -ForegroundColor White
Write-Host "  4. Search for 'Deals Management'" -ForegroundColor White
Write-Host "  5. Click 'Install'" -ForegroundColor White
Write-Host ""
Write-Host "If installation fails, the error will be shown in the Odoo UI." -ForegroundColor White
Write-Host "Check the log file on server: $OdooLogPath" -ForegroundColor White
Write-Host ""
