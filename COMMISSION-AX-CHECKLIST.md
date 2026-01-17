# 📦 COMMISSION_AX - MODULE INSTALLATION CHECKLIST

## Current Status ✅

Your Odoo MCP Server is now **fully configured** for the commission_ax database:

```
✅ Environment Setup
   • Database: commission_ax
   • URL: https://erp.sgctech.ai
   • User: info@scholarixglobal.com
   • MCP Instance: odoo-commission-ax
   
✅ MCP Server
   • Built and running
   • 11 tools available
   • Configuration ready
   
✅ Documentation
   • Installation guides created
   • Safety procedures documented
   • Troubleshooting guide included
```

---

## What to Do Now

### 1️⃣ Update Claude Desktop Configuration

Your `claude_desktop_config.json` needs to point to `odoo-commission-ax`:

```json
{
  "mcpServers": {
    "odoo-commission-ax": {
      "command": "node",
      "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
      "env": {
        "ODOO_URL": "https://erp.sgctech.ai",
        "ODOO_DB": "commission_ax",
        "ODOO_USERNAME": "info@scholarixglobal.com",
        "ODOO_PASSWORD": "123456"
      }
    }
  }
}
```

**Or use the pre-made config:**
- Location: `d:\01_WORK_PROJECTS\odoo-mcp-server\claude-config-YOUR-SETUP.json`
- Copy this to: `%APPDATA%\Claude\claude_desktop_config.json`

### 2️⃣ Restart Claude Desktop

1. Completely close Claude Desktop
2. Wait 3 seconds
3. Reopen Claude Desktop
4. Check for 🔌 icon showing `odoo-commission-ax` connected

### 3️⃣ Start Module Discovery in Claude

Ask Claude:

```
"In the commission_ax database, what modules are available 
that haven't been installed yet? For each module show:
- Name
- Version
- Description
- Required dependencies"
```

---

## The 5-Step Installation Process

Once you identify a module to install:

### STEP 1: Deep Analysis
```
"Analyze the [MODULE_NAME] module in detail:
- What is its purpose and key features?
- What modules does it depend on?
- Are all dependencies currently installed?
- Is it marked as stable/production-ready?
- Any known issues or limitations?"
```

### STEP 2: Safety Verification
```
"Before installing [MODULE_NAME], verify:
✓ Current state is 'uninstalled' (not 'broken')
✓ All dependencies are installed
✓ No circular dependency chains
✓ Module is compatible with current Odoo version
✓ No conflicting modules already exist
✓ External dependencies (Python packages) available"
```

### STEP 3: Dependency Resolution
```
"If any dependencies are missing:
1. Install each required dependency first
2. Work bottom-up (dependencies before dependents)
3. Test each installation before moving to next
4. Verify all dependencies are in 'installed' state"
```

### STEP 4: Execute Installation
```
"Install [MODULE_NAME] in commission_ax:
1. Locate the ir.module.module record
2. Call button_install action
3. Wait for installation to complete
4. Verify state changed to 'installed'
5. Confirm installed_version is current"
```

### STEP 5: Functionality Testing
```
"Test [MODULE_NAME] to ensure it's working:
1. Are new menu items visible in the Odoo UI?
2. Can you access the module's main models/views?
3. Do default records exist (if applicable)?
4. Test core functionality of the module
5. Check for any console/server errors"
```

---

## Module Categories to Explore

### Core Accounting & Finance
- `account` - General Accounting
- `account_accountant` - Advanced Accounting Features
- `payment` - Payment Processing
- `tax` - Tax Management

### Sales & CRM
- `sale` - Sales Orders
- `sale_commission` - Commission Tracking
- `crm` - CRM/Leads Management
- `partner_commission` - Partner Commissions

### Inventory & Supply Chain
- `stock` - Inventory Management
- `purchase` - Purchase Orders
- `mrp` - Manufacturing

### Commission-Specific (Likely Candidates)
- `sale_commission` - Sales commission engine
- `commission_rules` - Rule-based commissions
- `partner_commission` - Partner/vendor commissions
- Any custom commission modules

### Reporting & Analytics
- `report` - Report Engine
- `web_analytics` - Analytics Dashboard
- `dashboard` - Custom Dashboards

---

## Key Models for Module Management

When exploring modules, you'll interact with these Odoo models:

```
ir.module.module      - Module definitions & status
ir.model              - Data models in modules
ir.model.fields       - Field definitions
ir.ui.menu            - Menu items
ir.ui.view            - Views (forms, lists, kanban)
ir.actions.act_window - Menu actions
ir.module.category    - Module categories
```

---

## Critical Safety Rules ⚠️

**BEFORE INSTALLING ANY MODULE:**

1. ✅ Check module state is "uninstalled" (not "broken")
2. ✅ Verify all dependencies exist and are installable
3. ✅ Check for circular dependencies
4. ✅ Ensure compatibility with Odoo version
5. ✅ Test one module at a time
6. ✅ Document what you install and why

**DURING INSTALLATION:**

1. ✅ Monitor for errors
2. ✅ Don't interrupt the process
3. ✅ Let it complete fully before testing

**AFTER INSTALLATION:**

1. ✅ Verify state is "installed"
2. ✅ Test basic functionality
3. ✅ Check for console/database errors
4. ✅ Document the installation in a log

---

## Troubleshooting Guide

### "Module state is broken"
```
Ask Claude:
"The [MODULE] has state='broken'. 
What's causing this and how do we fix it?
Can we install missing dependencies first?"
```

### "Installation failed"
```
Ask Claude:
"Installation of [MODULE] failed. 
Show the exact error message and 
suggest solutions."
```

### "New menus don't appear"
```
Ask Claude:
"After installing [MODULE], new menus aren't showing.
1. Check if ir.ui.menu records exist for this module
2. Verify menu access permissions
3. Check if module is really installed
4. Look for menu visibility settings"
```

### "Dependency not found"
```
Ask Claude:
"[MODULE] requires [DEPENDENCY] but it's not installed.
Can we:
1. Install [DEPENDENCY] first?
2. Check if it's available in this Odoo version?
3. Find an alternative module?"
```

---

## Recommended Reading

- **Full Guide:** `COMMISSION-AX-MODULES.md`
- **Quick Steps:** `COMMISSION-AX-INSTALL-STEPS.txt`
- **General Reference:** `QUICK-REFERENCE.md`
- **Full Documentation:** `README.md`

---

## Quick Command Reference

In Claude, these commands will help:

```
# List available modules
"Search ir.module.module records with state != 'installed'"

# Get module details
"Get fields for ir.module.module: [list specific fields]"

# Check dependencies
"Show dependencies field for [MODULE_NAME]"

# Install a module
"Call button_install on ir.module.module record for [MODULE]"

# Test functionality
"Execute search_read on [MODEL_NAME] from installed module"

# Generate reports
"Generate report for [REPORT_NAME]"
```

---

## Success Criteria ✅

An installation is **successful** when:

1. ✅ Module state = "installed"
2. ✅ Installed version = latest available
3. ✅ New menus/features visible in UI
4. ✅ Core functionality tested and working
5. ✅ No console/database errors
6. ✅ All dependent modules still work

---

## Your Next Move 🚀

1. **Close this file**
2. **Update Claude config** to use `odoo-commission-ax`
3. **Restart Claude Desktop**
4. **Ask Claude:** "What modules are available in commission_ax?"
5. **Pick a module** to install
6. **Follow the 5-step process** above
7. **Report back** when module is installed!

---

**Status: READY FOR MODULE DISCOVERY & INSTALLATION** ✅

Last Updated: January 16, 2026
Database: commission_ax
Instance: odoo-commission-ax
Tools: 11 Available
