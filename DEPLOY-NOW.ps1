# ============================================
# ODOO DEPLOYMENT SCRIPT - INTERACTIVE
# ============================================
# This script automates the deployment of deal tracking
# to your Odoo server via SSH

param(
    [Parameter(Mandatory=$false)]
    [string]$ServerIP = "139.84.163.11",
    [Parameter(Mandatory=$false)]
    [string]$Username = "root",
    [Parameter(Mandatory=$false)]
    [string]$Password = $null
)

# ============================================
# SETUP & COLORS
# ============================================
$ErrorActionPreference = "Continue"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommandPath

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    $colors = @{
        "OK"    = "Green"
        "ERROR" = "Red"
        "WARN"  = "Yellow"
        "INFO"  = "Cyan"
        "STEP"  = "Blue"
    }
    $color = $colors[$Status] ?? "White"
    Write-Host "[$Status] $Message" -ForegroundColor $color
}

function Check-ScriptExists {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        Write-Status "Found: $FilePath" "OK"
        return $true
    } else {
        Write-Status "Missing: $FilePath" "ERROR"
        return $false
    }
}

# ============================================
# STEP 1: VERIFY LOCAL FILES
# ============================================
Write-Host "`n" + ("="*60) "DEPLOYMENT INITIALIZATION" ("="*60) -ForegroundColor Blue
Write-Status "Checking local deployment files..." "STEP"

$requiredFiles = @(
    "deploy-interactive.sh",
    "monitor-deployment.sh",
    "sale_order_deal_tracking_ext.py",
    "account_move_deal_tracking_ext.py",
    "sale_order_deal_tracking_views.xml",
    "account_move_deal_tracking_views.xml"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $scriptPath $file
    if (Check-ScriptExists $filePath) {
        # OK
    } else {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Status "Missing files: $($missingFiles -join ', ')" "ERROR"
    exit 1
}

Write-Status "All deployment files verified ✓" "OK"

# ============================================
# STEP 2: GATHER DEPLOYMENT PARAMETERS
# ============================================
Write-Host "`n" + ("="*60) "DEPLOYMENT PARAMETERS" ("="*60) -ForegroundColor Blue
Write-Status "Server IP: $ServerIP" "INFO"
Write-Status "Username: $Username" "INFO"

if (-not $Password) {
    Write-Host "`nEnter the SSH password for $Username@$ServerIP:"
    $secPassword = Read-Host -AsSecureString
    $Password = [System.Net.NetworkCredential]::new("", $secPassword).Password
}

# ============================================
# STEP 3: TEST SSH CONNECTION
# ============================================
Write-Host "`n" + ("="*60) "TESTING SSH CONNECTION" ("="*60) -ForegroundColor Blue
Write-Status "Testing connection to $ServerIP..." "STEP"

$testCmd = @"
sshpass -p '$Password' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $Username@$ServerIP "echo 'SSH Connection OK'; pwd; systemctl is-active odoo"
"@

try {
    # First check if sshpass exists
    $sshpassTest = (Get-Command sshpass -ErrorAction SilentlyContinue)
    if (-not $sshpassTest) {
        Write-Status "sshpass not found. Installing via choco..." "WARN"
        choco install sshpass -y | Out-Null
    }
    
    $connectionTest = & cmd /c $testCmd 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Status "SSH connection successful ✓" "OK"
        Write-Host "Output: $connectionTest" -ForegroundColor DarkGray
    } else {
        Write-Status "SSH connection failed" "ERROR"
        Write-Host "Error: $connectionTest" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Status "Failed to test connection: $_" "ERROR"
    exit 1
}

# ============================================
# STEP 4: COPY DEPLOYMENT SCRIPTS
# ============================================
Write-Host "`n" + ("="*60) "COPYING DEPLOYMENT FILES" ("="*60) -ForegroundColor Blue
Write-Status "Copying scripts to /tmp on server..." "STEP"

try {
    $deployScript = Join-Path $scriptPath "deploy-interactive.sh"
    $monitorScript = Join-Path $scriptPath "monitor-deployment.sh"
    
    # Using sshpass with scp
    $scpCmd = @"
sshpass -p '$Password' scp -o StrictHostKeyChecking=no "$deployScript" "$Username@$ServerIP`:/tmp/"
"@
    
    & cmd /c $scpCmd 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Scripts copied successfully ✓" "OK"
    } else {
        Write-Status "Failed to copy scripts" "ERROR"
        exit 1
    }
} catch {
    Write-Status "Copy failed: $_" "ERROR"
    exit 1
}

# ============================================
# STEP 5: EXECUTE INSTALLATION
# ============================================
Write-Host "`n" + ("="*60) "STARTING INSTALLATION" ("="*60) -ForegroundColor Blue
Write-Status "Beginning automated deployment..." "STEP"
Write-Host "This will take 10-15 minutes. Monitoring output below...`n" -ForegroundColor DarkGray

$installCmd = @"
sshpass -p '$Password' ssh -o StrictHostKeyChecking=no $Username@$ServerIP "cd /var/odoo/scholarixv2 && bash /tmp/deploy-interactive.sh"
"@

# Run installation and capture output
$output = & cmd /c $installCmd 2>&1
Write-Host $output

if ($LASTEXITCODE -eq 0) {
    Write-Status "Installation completed successfully ✓" "OK"
} else {
    Write-Status "Installation may have encountered issues. Check output above." "WARN"
}

# ============================================
# STEP 6: POST-DEPLOYMENT VERIFICATION
# ============================================
Write-Host "`n" + ("="*60) "POST-DEPLOYMENT VERIFICATION" ("="*60) -ForegroundColor Blue
Write-Status "Checking deployment status..." "STEP"

$verifyCmd = @"
sshpass -p '$Password' ssh -o StrictHostKeyChecking=no $Username@$ServerIP "systemctl status odoo | head -5; echo '---'; ls -lh /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py"
"@

try {
    $verifyOutput = & cmd /c $verifyCmd 2>&1
    Write-Host $verifyOutput -ForegroundColor DarkGray
} catch {
    Write-Status "Verification check failed: $_" "WARN"
}

# ============================================
# STEP 7: NEXT STEPS
# ============================================
Write-Host "`n" + ("="*60) "NEXT STEPS" ("="*60) -ForegroundColor Blue
Write-Host @"
1. ✓ Deployment Scripts Uploaded
2. ✓ Installation Executed
3. PENDING: Module Upgrade in Odoo UI

To complete setup:

A) Open Odoo Web Interface:
   → http://139.84.163.11:8069

B) Log in with admin credentials

C) Go to Settings → Apps

D) Search for: commission_ax

E) Click on module → Upgrade

F) Wait 2-5 minutes for upgrade

G) Verify new fields appear in:
   → Sales → Quotations (open a sale order)
   → Look for "BROKERAGE DEAL INFORMATION" section

Running Tests:
→ Follow instructions in TESTING-GUIDE.md

Monitoring Logs (in separate SSH session):
→ ssh root@139.84.163.11
→ tail -f /var/log/odoo/odoo-server.log
"@ -ForegroundColor Green

Write-Host "`nDeployment Package Ready!" -ForegroundColor Green
Write-Host "Check: http://139.84.163.11:8069`n" -ForegroundColor Cyan
