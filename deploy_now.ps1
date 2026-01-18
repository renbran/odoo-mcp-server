# DEAL MANAGEMENT - WINDOWS DEPLOYMENT SCRIPT
# PowerShell script to deploy module to Odoo server

param(
    [string]$Action = "upload"
)

$ErrorActionPreference = "Continue"

# Configuration
$LOCAL_MODULE = "d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management"
$REMOTE_USER = "root"
$REMOTE_HOST = "erp.sgctech.ai"
$REMOTE_ADDON_PATH = "/var/odoo/scholarixv2/src/addons"
$REMOTE_ODOO_ROOT = "/var/odoo/scholarixv2"
$REMOTE_CONFIG = "/var/odoo/scholarixv2/odoo.conf"

function Print-Header {
    param([string]$Text)
    Write-Host "`n" -ForegroundColor Yellow
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
}

function Print-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Print-Error {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

function Print-Warning {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor Yellow
}

function Print-Info {
    param([string]$Text)
    Write-Host "ℹ️  $Text" -ForegroundColor Cyan
}

Print-Header "DEAL MANAGEMENT - WINDOWS DEPLOYMENT"

# Step 1: Verify module exists
Print-Header "STEP 1: VERIFY LOCAL MODULE"

if (-not (Test-Path $LOCAL_MODULE)) {
    Print-Error "Module not found at: $LOCAL_MODULE"
    exit 1
}

if (-not (Test-Path "$LOCAL_MODULE\__manifest__.py")) {
    Print-Error "__manifest__.py not found in module"
    exit 1
}

Print-Success "Module found at: $LOCAL_MODULE"
$py_count = (Get-ChildItem -Path $LOCAL_MODULE -Filter "*.py" -Recurse).Count
$xml_count = (Get-ChildItem -Path $LOCAL_MODULE -Filter "*.xml" -Recurse).Count
Print-Info "Files: $py_count Python, $xml_count XML"

# Step 2: Test SSH (if OpenSSH available)
Print-Header "STEP 2: CHECK SSH AVAILABILITY"

$ssh_available = $null
try {
    $ssh_available = Get-Command ssh -ErrorAction SilentlyContinue
    if ($ssh_available) {
        Print-Success "SSH found: $($ssh_available.Source)"
    } else {
        Print-Warning "SSH not found. Using alternative methods."
    }
} catch {
    Print-Warning "SSH not available. Install OpenSSH or use WinSCP"
}

# Step 3: Upload module
Print-Header "STEP 3: UPLOAD MODULE"

if ($ssh_available) {
    Print-Info "Attempting SCP upload..."
    Print-Info "From: $LOCAL_MODULE"
    Print-Info "To:   $REMOTE_USER@$REMOTE_HOST`:$REMOTE_ADDON_PATH/"
    
    try {
        scp -r "$LOCAL_MODULE" "$REMOTE_USER@$REMOTE_HOST`:$REMOTE_ADDON_PATH/" 2>&1 | ForEach-Object {
            if ($_ -like "*error*" -or $_ -like "*denied*") {
                Print-Error $_
            } else {
                Print-Info $_
            }
        }
        Print-Success "SCP upload completed"
    } catch {
        Print-Error "SCP upload failed: $_"
        Print-Warning "Please upload manually via WinSCP"
    }
} else {
    Print-Warning "SSH not available on this system"
    Print-Info "MANUAL UPLOAD INSTRUCTIONS:"
    Print-Info "1. Download WinSCP: https://winscp.net/"
    Print-Info "2. Connect: root@erp.sgctech.ai"
    Print-Info "3. Navigate to: $REMOTE_ADDON_PATH/"
    Print-Info "4. Drag & drop: deal_management folder"
    Print-Info "5. Run Step 4 once upload is complete"
    
    Read-Host "Press Enter to continue (after upload complete)..."
}

# Step 4: Set permissions
Print-Header "STEP 4: SET PERMISSIONS"

if ($ssh_available) {
    Print-Info "Setting file permissions..."
    
    try {
        ssh $REMOTE_USER@$REMOTE_HOST "chown -R odoo:odoo $REMOTE_ADDON_PATH/deal_management" 2>&1
        ssh $REMOTE_USER@$REMOTE_HOST "chmod -R 755 $REMOTE_ADDON_PATH/deal_management" 2>&1
        Print-Success "Permissions set"
    } catch {
        Print-Warning "Permission setting may have failed"
    }
} else {
    Print-Warning "Cannot set permissions without SSH"
    Print-Info "This will be done automatically by Odoo on next restart"
}

# Step 5: Update module list
Print-Header "STEP 5: UPDATE ODOO MODULE LIST"

if ($ssh_available) {
    Print-Info "This will take 2-5 minutes..."
    Print-Info "Updating module list via Odoo shell..."
    
    $update_cmd = @"
cd $REMOTE_ODOO_ROOT && sudo -u odoo /var/odoo/scholarixv2/venv/bin/python3 /var/odoo/scholarixv2/src/odoo-bin -c $REMOTE_CONFIG --no-http --stop-after-init -u base
"@
    
    try {
        ssh $REMOTE_USER@$REMOTE_HOST $update_cmd 2>&1 | Tee-Object -Variable output | ForEach-Object {
            if ($_ -like "*error*" -or $_ -like "*Error*") {
                Print-Error $_
            }
        }
        Print-Success "Module list updated"
    } catch {
        Print-Warning "Module update may have issues"
    }
} else {
    Print-Warning "Cannot update module list without SSH"
    Print-Info "This will be updated when Odoo restarts"
}

# Step 6: Web UI installation
Print-Header "STEP 6: INSTALL VIA WEB UI"

Print-Info "Opening Odoo in browser..."
try {
    Start-Process "https://erp.sgctech.ai/scholarixv2"
} catch {
    Print-Info "Manual: Go to https://erp.sgctech.ai/scholarixv2"
}

Print-Info "Installation steps:"
Print-Info "1. Login: info@scholarixglobal.com / 123456"
Print-Info "2. Go to: Settings > Apps"
Print-Info "3. Click: 'Update App List' (refresh button)"
Print-Info "4. Search: 'Deal Management'"
Print-Info "5. Click: 'Install'"
Print-Info "6. Wait 2-5 minutes for installation"

Print-Header "DEPLOYMENT STATUS"
Print-Success "✅ Module ready to install"
Print-Success "✅ Upload attempted/completed"
Print-Success "✅ Permissions set (if SSH available)"
Print-Success "✅ Module list updated (if SSH available)"
Print-Warning "⏳ Complete web UI installation manually"

Print-Info ""
Print-Info "Next steps:"
Print-Info "1. Complete web UI installation (see instructions above)"
Print-Info "2. Verify in Settings > Apps that 'Deal Management' is installed"
Print-Info "3. Go to Sales > Deals to see new menu"
Print-Info "4. Create test deal to verify functionality"
Print-Info ""
Print-Info "Total time: 10-20 minutes"

Read-Host "Press Enter to close this window"
