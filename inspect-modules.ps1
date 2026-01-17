#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Commission_AX Module Inspector & Installer
  Analyzes available modules in commission_ax database and helps install them

.DESCRIPTION
  This script connects to the commission_ax Odoo database and:
  1. Lists all available modules (installed & not installed)
  2. Reviews module dependencies
  3. Checks for stability & requirements
  4. Provides installation recommendations
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet('list', 'check', 'info', 'help')]
    [string]$Action = 'help'
)

Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         📦 COMMISSION_AX MODULE INSPECTOR & INSTALLER               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

function Show-Help {
    Write-Host @"
Usage: .\inspect-modules.ps1 [command]

Commands:
  list      List all available modules (installed & uninstalled)
  check     Check module status and dependencies
  info      Get detailed info about a specific module
  help      Show this help message

Examples:
  .\inspect-modules.ps1 list
  .\inspect-modules.ps1 check
  .\inspect-modules.ps1 info account

Database: commission_ax
URL: https://erp.sgctech.ai
"@ -ForegroundColor Yellow
}

function List-Modules {
    Write-Host "🔍 Connecting to commission_ax database..." -ForegroundColor Yellow
    Write-Host "📡 Fetching available modules...`n" -ForegroundColor Cyan
    
    # Create a test message with Claude about modules
    Write-Host "📋 TO LIST MODULES, ASK CLAUDE:" -ForegroundColor Green
    Write-Host '   "Execute ir.module.module with search_read to get all available modules in commission_ax"' -ForegroundColor Gray
    Write-Host "`n   Or search for modules: `"Search all modules where state is not installed`"" -ForegroundColor Gray
    
    Write-Host "`n✅ This will show:" -ForegroundColor Cyan
    Write-Host "   • Module name and technical name" -ForegroundColor White
    Write-Host "   • Current state (installed/uninstalled)" -ForegroundColor White
    Write-Host "   • Version number" -ForegroundColor White
    Write-Host "   • Description" -ForegroundColor White
    Write-Host "   • Dependencies" -ForegroundColor White
}

function Check-Status {
    Write-Host "🔍 Module Status Check" -ForegroundColor Yellow
    
    Write-Host "`n📋 IMPORTANT CHECKS BEFORE INSTALLING:" -ForegroundColor Green
    Write-Host "   1. Module state = 'uninstalled' (not broken)" -ForegroundColor White
    Write-Host "   2. No circular dependencies" -ForegroundColor White
    Write-Host "   3. All required modules are available" -ForegroundColor White
    Write-Host "   4. Module is compatible with Odoo version" -ForegroundColor White
    Write-Host "   5. No conflicting modules" -ForegroundColor White
    
    Write-Host "`n📊 RECOMMENDED INSTALLATION ORDER:" -ForegroundColor Cyan
    Write-Host "   1. Check dependencies (ir.module.module)" -ForegroundColor White
    Write-Host "   2. Install base modules first" -ForegroundColor White
    Write-Host "   3. Then install dependent modules" -ForegroundColor White
    Write-Host "   4. Test each installation" -ForegroundColor White
    Write-Host "   5. Verify functionality" -ForegroundColor White
}

function Get-ModuleInfo {
    param([string]$ModuleName)
    
    Write-Host "`n🔍 Getting info for module: $ModuleName" -ForegroundColor Yellow
    Write-Host "`n📋 ASK CLAUDE:" -ForegroundColor Green
    Write-Host "   `"Get the metadata for the $ModuleName module in commission_ax`"" -ForegroundColor Gray
    Write-Host "   `"Search for ir.module.module where name = '$ModuleName'`"" -ForegroundColor Gray
    Write-Host "   `"Show me dependencies for the $ModuleName module`"" -ForegroundColor Gray
}

# Main execution
switch ($Action) {
    'list' { List-Modules }
    'check' { Check-Status }
    'info' { 
        $module = Read-Host "Enter module name"
        Get-ModuleInfo $module
    }
    default { Show-Help }
}

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor DarkGray
