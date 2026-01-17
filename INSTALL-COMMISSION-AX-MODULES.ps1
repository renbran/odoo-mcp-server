#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Commission_AX - Smart Module Installer
  Safely discovers, analyzes, and installs Odoo modules
#>

Write-Host @"
╔══════════════════════════════════════════════════════════════════════════╗
║                 📦 COMMISSION_AX MODULE INSTALLER                        ║
║              Safe Module Discovery & Installation Toolkit                 ║
╚══════════════════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

Write-Host "`n🎯 MISSION: Find & Install Available Modules with Full Stability`n" -ForegroundColor Yellow

Write-Host "┌─────────────────────────────────────────────────────────────────────┐" -ForegroundColor Magenta
Write-Host "│ 📋 STEP 1: LIST AVAILABLE MODULES                                   │" -ForegroundColor Magenta
Write-Host "└─────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor Magenta

Write-Host "In Claude Desktop, ask:" -ForegroundColor Green
Write-Host '   "Execute this Odoo search in commission_ax database:' -ForegroundColor Cyan
Write-Host '   Search ir.module.module where state != "installed"' -ForegroundColor Cyan
Write-Host '   Show: name, description, version, state, depends"' -ForegroundColor Cyan

Write-Host "`n   This will show you ALL modules that CAN be installed but aren't yet.`n" -ForegroundColor White

Write-Host "┌─────────────────────────────────────────────────────────────────────┐" -ForegroundColor Magenta
Write-Host "│ 🔍 STEP 2: ANALYZE MODULE DETAILS                                   │" -ForegroundColor Magenta
Write-Host "└─────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor Magenta

Write-Host "Once you identify a module you want, ask Claude:" -ForegroundColor Green
Write-Host '   "Analyze the [MODULE_NAME] module in commission_ax:' -ForegroundColor Cyan
Write-Host '   1. What is its purpose?' -ForegroundColor Cyan
Write-Host '   2. What modules does it depend on?' -ForegroundColor Cyan
Write-Host '   3. Are all dependencies installed?' -ForegroundColor Cyan
Write-Host '   4. Is it marked as stable?' -ForegroundColor Cyan
Write-Host '   5. What version is available?"' -ForegroundColor Cyan

Write-Host "`n   This checks stability and compatibility BEFORE installation.`n" -ForegroundColor White

Write-Host "┌─────────────────────────────────────────────────────────────────────┐" -ForegroundColor Magenta
Write-Host "│ ✅ STEP 3: PRE-INSTALLATION VERIFICATION                            │" -ForegroundColor Magenta
Write-Host "└─────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor Magenta

Write-Host "Before installing, ask Claude to verify:" -ForegroundColor Green
Write-Host '   "Verify installation safety for [MODULE]:' -ForegroundColor Cyan
Write-Host '   ✓ State is "uninstalled" (not broken)' -ForegroundColor Cyan
Write-Host '   ✓ All dependencies are installed' -ForegroundColor Cyan
Write-Host '   ✓ No circular dependencies' -ForegroundColor Cyan
Write-Host '   ✓ Module is compatible with current Odoo version' -ForegroundColor Cyan
Write-Host '   ✓ No conflicting modules installed"' -ForegroundColor Cyan

Write-Host "`n   Gets all safety checks done at once.`n" -ForegroundColor White

Write-Host "┌─────────────────────────────────────────────────────────────────────┐" -ForegroundColor Magenta
Write-Host "│ 🚀 STEP 4: INSTALL MODULE                                           │" -ForegroundColor Magenta
Write-Host "└─────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor Magenta

Write-Host "When everything checks out, ask Claude:" -ForegroundColor Green
Write-Host '   "Install [MODULE_NAME] in commission_ax by:' -ForegroundColor Cyan
Write-Host '   1. Call button_install on the module record' -ForegroundColor Cyan
Write-Host '   2. Wait for installation to complete' -ForegroundColor Cyan
Write-Host '   3. Verify state changed to "installed"' -ForegroundColor Cyan
Write-Host '   4. Confirm installed_version is current"' -ForegroundColor Cyan

Write-Host "`n   This executes the installation safely.`n" -ForegroundColor White

Write-Host "┌─────────────────────────────────────────────────────────────────────┐" -ForegroundColor Magenta
Write-Host "│ 🧪 STEP 5: POST-INSTALLATION TESTING                               │" -ForegroundColor Magenta
Write-Host "└─────────────────────────────────────────────────────────────────────┘`n" -ForegroundColor Magenta

Write-Host "After installation, ask Claude to test:" -ForegroundColor Green
Write-Host '   "Test [MODULE] installation:' -ForegroundColor Cyan
Write-Host '   1. Are new menu items visible in the UI?' -ForegroundColor Cyan
Write-Host '   2. Can you access the module models?' -ForegroundColor Cyan
Write-Host '   3. Are there any default records created?' -ForegroundColor Cyan
Write-Host '   4. Test the main functionality' -ForegroundColor Cyan
Write-Host '   5. Check for any console/server errors"' -ForegroundColor Cyan

Write-Host "`n   Comprehensive testing ensures stability.`n" -ForegroundColor White

Write-Host "═════════════════════════════════════════════════════════════════════════`n" -ForegroundColor DarkGray

Write-Host "📊 DATABASE INFO:" -ForegroundColor Yellow
Write-Host "  Instance: commission_ax" -ForegroundColor White
Write-Host "  URL: https://erp.sgctech.ai" -ForegroundColor White
Write-Host "  MCP Server: odoo-commission-ax" -ForegroundColor White
Write-Host "  Available Tools: 11" -ForegroundColor White

Write-Host "`n🤖 CLAUDE SETUP:" -ForegroundColor Yellow
Write-Host "  Make sure your Claude Desktop config uses:" -ForegroundColor White
Write-Host '  "odoo-commission-ax" instance' -ForegroundColor Cyan

Write-Host "`n📚 REFERENCE DOCS:" -ForegroundColor Yellow
Write-Host "  Full Guide: COMMISSION-AX-MODULES.md" -ForegroundColor White
Write-Host "  Quick Ref: QUICK-REFERENCE.md" -ForegroundColor White

Write-Host "`n════════════════════════════════════════════════════════════════════════`n" -ForegroundColor DarkGray

Write-Host "🎯 READY TO START?" -ForegroundColor Green
Write-Host "`nIn Claude, ask:" -ForegroundColor Cyan
Write-Host '   "What modules are available in commission_ax that aren''t installed?"' -ForegroundColor Gray

Write-Host "`nThen follow the 5 steps above for safe installation! 🚀`n" -ForegroundColor Yellow
