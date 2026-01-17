#!/usr/bin/env pwsh
# 🎓 Scholarix v2 - Quick Start with Claude Desktop

Write-Host @"

╔════════════════════════════════════════════════════════════════════════╗
║                    🎓 SCHOLARIX v2 MODULE - LIVE                      ║
║                  Odoo MCP Server Connected to Claude                   ║
╚════════════════════════════════════════════════════════════════════════╝

🚀 YOUR SETUP IS COMPLETE!

📊 Connected Instance:
   • Instance Name: odoo-scholarix
   • URL: https://erp.sgctech.ai
   • Database: scholarixv2
   • User: info@scholarixglobal.com
   • Status: ✅ READY

🤖 Claude Desktop:
   • Status: Should be open now
   • MCP Server: odoo-scholarix (check 🔌 icon)
   • Available Tools: 11 (search, create, update, read, etc.)

════════════════════════════════════════════════════════════════════════

📝 FIRST TESTS TO RUN IN CLAUDE:

1️⃣  Ask Claude about available tools:
    
    "What Odoo tools do you have available?"
    
    Expected: Should list all 11 tools

2️⃣  Explore the database structure:
    
    "Search for all partners in the Scholarix database"
    
    "How many records are in the res.partner model?"

3️⃣  Look for Scholarix-specific models:
    
    "What custom modules are installed in Scholarix?"
    
    "Search for student records in the database"

4️⃣  Get model information:
    
    "Show me all fields available in the res.partner model"
    
    "What fields exist in the student module?"

════════════════════════════════════════════════════════════════════════

🎯 NEXT STEPS:

✓ Claude Desktop is running
✓ MCP server configured with your credentials
✓ 11 Odoo tools available in Claude

Now in Claude:
1. Look for 🔌 icon in the interface
2. Verify "odoo-scholarix" is listed and connected
3. Start asking about your Scholarix data!

════════════════════════════════════════════════════════════════════════

📖 HELPFUL RESOURCES:

• Full Testing Guide: SCHOLARIX-TESTING.md
• Quick Reference: QUICK-REFERENCE.md
• Setup Guide: SETUP-GUIDE.md
• Full Docs: README.md

════════════════════════════════════════════════════════════════════════

💬 EXAMPLE PROMPTS FOR CLAUDE:

Search Data:
  "Get all customer records from Scholarix"
  "Count total students in the database"
  "Find all scholarship applications"

Model Info:
  "List all fields on the sale.order model"
  "Show me the res.partner model structure"
  "What custom fields does the student module have?"

Create Records:
  "Create a new test partner named 'Test Scholar'"
  "Add a new student to the database"

Advanced:
  "Generate a PDF report of all enrollments"
  "Show me students from a specific program"

════════════════════════════════════════════════════════════════════════

🔧 IF CLAUDE DOESN'T SEE THE SERVER:

1. Close Claude completely (right-click taskbar → Quit)
2. Wait 3 seconds
3. Reopen Claude
4. Check for 🔌 icon with "odoo-scholarix"

════════════════════════════════════════════════════════════════════════

🎉 YOU'RE READY TO GO!

Go to Claude Desktop and start exploring your Scholarix database!

Type: What Odoo tools do you have available?

" -ForegroundColor Cyan

Write-Host "`nPress Enter to continue..." -ForegroundColor Yellow
Read-Host
