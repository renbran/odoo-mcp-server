# ============================================================================
# Odoo Deals Management Module - Automated Deployment Script
# ============================================================================
# This script automates:
# 1. Creating zip of local module
# 2. Uploading to server
# 3. Extracting to correct location
# 4. Cleaning database cache
# 5. Restarting Odoo
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerHost,
    
    [Parameter(Mandatory=$true)]
    [string]$ServerUser,
    
    [string]$ServerPassword = "",
    
    [string]$SshKeyPath = ""
)

$ErrorActionPreference = "Stop"

# Configuration
$LocalModulePath = "D:\01_WORK_PROJECTS\odoo-mcp-server\deals_management"
$ZipPath = "D:\deals_management.zip"
$ServerTempPath = "/tmp/deals_management.zip"
$ServerModulePath = "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management"
$ServerAddonsPath = "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
$DbName = "scholarixv2"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Odoo Deals Management Module - Automated Deployment" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create ZIP file
Write-Host "[1/6] Creating ZIP file..." -ForegroundColor Yellow
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}
Compress-Archive -Path "$LocalModulePath\*" -DestinationPath $ZipPath -Force
Write-Host "✓ ZIP created: $ZipPath" -ForegroundColor Green
Write-Host ""

# Step 2: Upload to server
Write-Host "[2/6] Uploading to server..." -ForegroundColor Yellow

if ($SshKeyPath) {
    # Using SSH key
    scp -i $SshKeyPath $ZipPath "${ServerUser}@${ServerHost}:${ServerTempPath}"
} elseif ($ServerPassword) {
    # Using password (requires plink/pscp from PuTTY)
    echo $ServerPassword | pscp -pw $ServerPassword $ZipPath "${ServerUser}@${ServerHost}:${ServerTempPath}"
} else {
    # Interactive authentication
    scp $ZipPath "${ServerUser}@${ServerHost}:${ServerTempPath}"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Upload successful" -ForegroundColor Green
} else {
    Write-Host "✗ Upload failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3-6: Execute server-side commands
Write-Host "[3/6] Executing server-side deployment..." -ForegroundColor Yellow

$ServerCommands = @"
echo '--- Step 3: Removing old module ---'
sudo rm -rf $ServerModulePath
echo '✓ Old module removed'
echo ''

echo '--- Step 4: Extracting new module ---'
cd $ServerAddonsPath
sudo unzip -o $ServerTempPath -d deals_management
sudo chown -R odoo:odoo deals_management
sudo chmod -R 755 deals_management
echo '✓ Module extracted and permissions set'
echo ''

echo '--- Step 5: Verifying file ---'
LINE_COUNT=\$(wc -l < $ServerModulePath/views/deals_menu.xml)
echo \"File line count: \$LINE_COUNT (expected: 99)\"
BAD_REF=\$(grep -c 'menu_deals_projects\|action_deals_projects' $ServerModulePath/views/deals_menu.xml || true)
if [ \$BAD_REF -eq 0 ]; then
    echo '✓ No bad references found'
else
    echo '✗ WARNING: Bad references still present!'
    exit 1
fi
echo ''

echo '--- Step 6: Cleaning database cache ---'
sudo -u postgres psql $DbName -c "DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu'); DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window'); DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view'); DELETE FROM ir_model_data WHERE module = 'deals_management'; UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';"
echo '✓ Database cache cleaned'
echo ''

echo '--- Step 7: Restarting Odoo ---'
sudo systemctl restart odoo
sleep 5
sudo systemctl status odoo --no-pager | grep 'Active:'
echo '✓ Odoo restarted'
echo ''

echo '--- Cleanup ---'
rm -f $ServerTempPath
echo '✓ Temporary files removed'
echo ''

echo '============================================================================'
echo 'DEPLOYMENT COMPLETE!'
echo '============================================================================'
echo ''
echo 'Next steps:'
echo '1. Login to Odoo at https://erp.sgctech.ai'
echo '2. Go to Apps menu'
echo '3. Remove all filters'
echo '4. Click "Update Apps List"'
echo '5. Search for "Deals Management"'
echo '6. Click Install'
echo ''
"@

if ($SshKeyPath) {
    # Using SSH key
    $ServerCommands | ssh -i $SshKeyPath "${ServerUser}@${ServerHost}" "bash -s"
} elseif ($ServerPassword) {
    # Using password (requires plink from PuTTY)
    $ServerCommands | plink -pw $ServerPassword "${ServerUser}@${ServerHost}"
} else {
    # Interactive authentication
    $ServerCommands | ssh "${ServerUser}@${ServerHost}" "bash -s"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host "✓ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Login to Odoo at https://erp.sgctech.ai" -ForegroundColor White
    Write-Host "2. Go to Apps menu" -ForegroundColor White
    Write-Host "3. Remove all filters" -ForegroundColor White
    Write-Host "4. Click 'Update Apps List'" -ForegroundColor White
    Write-Host "5. Search for 'Deals Management'" -ForegroundColor White
    Write-Host "6. Click Install" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ DEPLOYMENT FAILED!" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Red
    exit 1
}
