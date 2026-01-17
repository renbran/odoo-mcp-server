#!/usr/bin/env pwsh
# Quick Start Script for Odoo MCP Server
# This script helps you quickly test and configure your Odoo MCP server

param(
  [Parameter(Position = 0)]
  [ValidateSet('test', 'config', 'claude', 'help')]
  [string]$Action = 'help'
)

$ProjectRoot = $PSScriptRoot
$EnvFile = Join-Path $ProjectRoot ".env"
$DistPath = Join-Path $ProjectRoot "dist\index.js"

function Show-Help {
  Write-Host @"
🚀 Odoo MCP Server - Quick Start Helper
======================================

Usage: .\start.ps1 [command]

Commands:
  test      Test connection to your Odoo instance
  config    Open .env file to configure Odoo credentials
  claude    Show Claude Desktop configuration instructions
  help      Show this help message

Examples:
  .\start.ps1 test          # Test if Odoo connection works
  .\start.ps1 config        # Edit Odoo credentials
  .\start.ps1 claude        # Get Claude Desktop setup info

"@ -ForegroundColor Cyan
}

function Test-Connection {
  Write-Host "`n🔍 Testing Odoo MCP Server Connection..." -ForegroundColor Yellow
    
  if (-not (Test-Path $EnvFile)) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Run: .\start.ps1 config" -ForegroundColor Yellow
    return
  }

  Write-Host "✓ .env file found" -ForegroundColor Green
  Write-Host "✓ Built files exist" -ForegroundColor Green
  Write-Host "`nStarting test connection (press Ctrl+C to stop)...`n" -ForegroundColor Cyan
    
  npm run dev
}

function Edit-Config {
  Write-Host "`n📝 Opening Odoo configuration..." -ForegroundColor Yellow
    
  if (-not (Test-Path $EnvFile)) {
    Copy-Item "$EnvFile.example" $EnvFile
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
  }
    
  Write-Host "`nEdit these values with your Odoo details:" -ForegroundColor Cyan
  Write-Host "  ODOO_URL      = Your Odoo server URL" -ForegroundColor White
  Write-Host "  ODOO_DB       = Your database name" -ForegroundColor White
  Write-Host "  ODOO_USERNAME = Your username" -ForegroundColor White
  Write-Host "  ODOO_PASSWORD = Your password`n" -ForegroundColor White
    
  # Open in default editor
  Start-Process $EnvFile
    
  Write-Host "After editing, run: .\start.ps1 test" -ForegroundColor Yellow
}

function Show-ClaudeConfig {
  Write-Host "`n🤖 Claude Desktop Configuration" -ForegroundColor Yellow
  Write-Host "================================`n" -ForegroundColor Yellow
    
  $configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
    
  Write-Host "1. Open this file:" -ForegroundColor Cyan
  Write-Host "   $configPath`n" -ForegroundColor White
    
  Write-Host "2. Add this configuration:" -ForegroundColor Cyan
    
  $config = @"
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["$($DistPath -replace '\\', '\\')"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "your_database",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin"
      }
    }
  }
}
"@
    
  Write-Host $config -ForegroundColor Gray
    
  Write-Host "`n3. Update the env values with your Odoo credentials" -ForegroundColor Cyan
  Write-Host "4. Restart Claude Desktop completely" -ForegroundColor Cyan
  Write-Host "5. Look for 🔌 icon showing 'odoo' server connected`n" -ForegroundColor Cyan
    
  Write-Host "📁 Opening Claude config folder..." -ForegroundColor Yellow
  Start-Process (Split-Path $configPath)
    
  # Copy config to clipboard
  $config | Set-Clipboard
  Write-Host "✓ Configuration copied to clipboard!" -ForegroundColor Green
}

# Main execution
switch ($Action) {
  'test' { Test-Connection }
  'config' { Edit-Config }
  'claude' { Show-ClaudeConfig }
  default { Show-Help }
}
