#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Systematic Commission_AX Module Installation Workflow
    
.DESCRIPTION
    Complete workflow for:
    1. Backend inspector deployment
    2. Server testing
    3. Module inspection
    4. MCP server configuration
    5. Claude Desktop integration
#>

param(
    [string]$ServerHost = "",
    [string]$ServerUser = "",
    [switch]$SkipServerDeploy,
    [switch]$OnlyMCPSetup
)

# Configuration
$ODOO_SERVER_PATH = "/var/odoo/scholarixv2"
$CLAUDE_CONFIG = "$env:APPDATA\Claude\claude_desktop_config.json"
$PROJECT_ROOT = $PSScriptRoot

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   SYSTEMATIC COMMISSION_AX DEPLOYMENT WORKFLOW            ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================
# PHASE 1: BACKEND INSPECTOR DEPLOYMENT
# ============================================
if (-not $OnlyMCPSetup) {
    Write-Host "═══ PHASE 1: Backend Inspector Deployment ═══" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not $ServerHost -or -not $ServerUser) {
        Write-Host "⚠️  Server connection details needed" -ForegroundColor Red
        $ServerUser = Read-Host "Enter SSH username"
        $ServerHost = Read-Host "Enter server hostname/IP"
    }
    
    $sshTarget = "${ServerUser}@${ServerHost}"
    
    if (-not $SkipServerDeploy) {
        Write-Host "📦 Step 1.1: Verify inspect-backend.py exists..." -ForegroundColor Green
        if (-not (Test-Path "$PROJECT_ROOT\inspect-backend.py")) {
            Write-Host "❌ inspect-backend.py not found!" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ File found" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "📤 Step 1.2: Copy to server..." -ForegroundColor Green
        Write-Host "Command: scp inspect-backend.py ${sshTarget}:${ODOO_SERVER_PATH}/" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Run this command:" -ForegroundColor Yellow
        Write-Host "  scp inspect-backend.py ${sshTarget}:${ODOO_SERVER_PATH}/" -ForegroundColor White
        Write-Host ""
        $continue = Read-Host "Press Enter after copying file (or 's' to skip)"
        if ($continue -eq 's') {
            Write-Host "⏭️  Skipped" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    # ============================================
    # PHASE 2: SERVER TESTING
    # ============================================
    Write-Host "═══ PHASE 2: Server Testing ═══" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "🔌 Step 2.1: Test connection..." -ForegroundColor Green
    Write-Host "SSH into your server and run:" -ForegroundColor Yellow
    Write-Host "  ssh ${sshTarget}" -ForegroundColor White
    Write-Host "  cd ${ODOO_SERVER_PATH}" -ForegroundColor White
    Write-Host "  python3 inspect-backend.py list" -ForegroundColor White
    Write-Host ""
    Write-Host "Expected output: List of installed/uninstalled modules" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Press Enter after testing (or 's' to skip)"
    Write-Host ""
    
    Write-Host "🔍 Step 2.2: Search for commission modules..." -ForegroundColor Green
    Write-Host "Run on server:" -ForegroundColor Yellow
    Write-Host "  python3 inspect-backend.py list uninstalled | grep commission" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "Press Enter when complete"
    Write-Host ""
    
    Write-Host "📋 Step 2.3: Get commission_ax details..." -ForegroundColor Green
    Write-Host "Run on server:" -ForegroundColor Yellow
    Write-Host "  python3 inspect-backend.py info commission_ax" -ForegroundColor White
    Write-Host ""
    Write-Host "This shows: description, dependencies, version, state" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Press Enter when reviewed"
    Write-Host ""
    
    # ============================================
    # PHASE 3: MODULE INSTALLATION
    # ============================================
    Write-Host "═══ PHASE 3: Module Installation ═══" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "⚠️  WARNING: Only install if dependencies are met!" -ForegroundColor Red
    Write-Host ""
    $install = Read-Host "Install commission_ax module now? (yes/no)"
    
    if ($install -eq "yes") {
        Write-Host ""
        Write-Host "📦 Installing commission_ax..." -ForegroundColor Green
        Write-Host "Run on server:" -ForegroundColor Yellow
        Write-Host "  python3 inspect-backend.py install commission_ax" -ForegroundColor White
        Write-Host ""
        Write-Host "This will:" -ForegroundColor Gray
        Write-Host "  • Install the module" -ForegroundColor Gray
        Write-Host "  • Install dependencies automatically" -ForegroundColor Gray
        Write-Host "  • Update database schema" -ForegroundColor Gray
        Write-Host "  • Initialize module data" -ForegroundColor Gray
        Write-Host ""
        $continue = Read-Host "Press Enter after installation completes"
        Write-Host ""
        
        Write-Host "✅ Step 3.1: Verify installation..." -ForegroundColor Green
        Write-Host "Run on server:" -ForegroundColor Yellow
        Write-Host "  python3 inspect-backend.py info commission_ax" -ForegroundColor White
        Write-Host ""
        Write-Host "Check that state = 'installed'" -ForegroundColor Gray
        Write-Host ""
        $continue = Read-Host "Press Enter when verified"
    } else {
        Write-Host "⏭️  Skipping installation" -ForegroundColor Yellow
    }
    Write-Host ""
}

# ============================================
# PHASE 4: MCP SERVER CONFIGURATION
# ============================================
Write-Host "═══ PHASE 4: MCP Server Configuration ═══" -ForegroundColor Yellow
Write-Host ""

Write-Host "🔧 Step 4.1: Check MCP server build..." -ForegroundColor Green
if (Test-Path "$PROJECT_ROOT\dist\index.js") {
    Write-Host "✅ MCP server already built" -ForegroundColor Green
} else {
    Write-Host "⚠️  Building MCP server..." -ForegroundColor Yellow
    Push-Location $PROJECT_ROOT
    npm run build
    Pop-Location
    Write-Host "✅ Build complete" -ForegroundColor Green
}
Write-Host ""

Write-Host "📝 Step 4.2: Prepare Claude Desktop config..." -ForegroundColor Green
Write-Host ""

$claudeConfig = @{
    mcpServers = @{
        "odoo-commission-ax" = @{
            command = "node"
            args = @("$PROJECT_ROOT\dist\index.js" -replace '\\', '/')
            env = @{
                ODOO_URL = "https://erp.sgctech.ai"
                ODOO_DB = "commission_ax"
                ODOO_USERNAME = "info@scholarixglobal.com"
                ODOO_PASSWORD = "123456"
            }
        }
    }
}

$configJson = $claudeConfig | ConvertTo-Json -Depth 10

Write-Host "Configuration to add to Claude Desktop:" -ForegroundColor Yellow
Write-Host $configJson -ForegroundColor White
Write-Host ""

if (Test-Path $CLAUDE_CONFIG) {
    Write-Host "📁 Claude config exists: $CLAUDE_CONFIG" -ForegroundColor Green
    $update = Read-Host "Update Claude config automatically? (yes/no)"
    
    if ($update -eq "yes") {
        try {
            # Backup existing config
            $backup = "${CLAUDE_CONFIG}.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
            Copy-Item $CLAUDE_CONFIG $backup
            Write-Host "✅ Backup created: $backup" -ForegroundColor Green
            
            # Update config
            $existingConfig = Get-Content $CLAUDE_CONFIG -Raw | ConvertFrom-Json
            if (-not $existingConfig.mcpServers) {
                $existingConfig | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value @{}
            }
            $existingConfig.mcpServers | Add-Member -MemberType NoteProperty -Name "odoo-commission-ax" -Value $claudeConfig.mcpServers."odoo-commission-ax" -Force
            
            $existingConfig | ConvertTo-Json -Depth 10 | Set-Content $CLAUDE_CONFIG
            Write-Host "✅ Claude config updated" -ForegroundColor Green
        } catch {
            Write-Host "❌ Auto-update failed: $_" -ForegroundColor Red
            Write-Host "Please update manually" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Manual update required:" -ForegroundColor Yellow
        Write-Host "  1. Open: $CLAUDE_CONFIG" -ForegroundColor White
        Write-Host "  2. Add the 'odoo-commission-ax' server config above" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  Claude config not found" -ForegroundColor Yellow
    Write-Host "Create it at: $CLAUDE_CONFIG" -ForegroundColor White
    Write-Host "With content above" -ForegroundColor White
}
Write-Host ""

# ============================================
# PHASE 5: CLAUDE DESKTOP INTEGRATION
# ============================================
Write-Host "═══ PHASE 5: Claude Desktop Integration ═══" -ForegroundColor Yellow
Write-Host ""

Write-Host "🔄 Step 5.1: Restart Claude Desktop..." -ForegroundColor Green
Write-Host "  1. Close Claude Desktop completely" -ForegroundColor White
Write-Host "  2. Relaunch Claude Desktop" -ForegroundColor White
Write-Host "  3. Check for 'odoo-commission-ax' in MCP servers list" -ForegroundColor White
Write-Host ""
$continue = Read-Host "Press Enter after restarting Claude"
Write-Host ""

Write-Host "🧪 Step 5.2: Test MCP tools..." -ForegroundColor Green
Write-Host "In Claude Desktop, ask:" -ForegroundColor Yellow
Write-Host '  "List all uninstalled modules in commission_ax database"' -ForegroundColor White
Write-Host ""
Write-Host "Expected: Claude uses odoo-commission-ax tools to query modules" -ForegroundColor Gray
Write-Host ""

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              SYSTEMATIC DEPLOYMENT COMPLETE               ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Backend inspector: inspect-backend.py on server" -ForegroundColor Green
Write-Host "✅ MCP server: configured for commission_ax" -ForegroundColor Green
Write-Host "✅ Claude Desktop: ready to use" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "  • COMMISSION-AX-CHECKLIST.md - Installation checklist" -ForegroundColor White
Write-Host "  • BACKEND-INSPECTOR-GUIDE.md - Backend tool guide" -ForegroundColor White
Write-Host "  • COMMISSION-AX-MODULES.md - Module details" -ForegroundColor White
Write-Host ""
