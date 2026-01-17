# 🔧 COMMISSION_AX BACKEND - MODULE INSPECTION & INSTALLATION GUIDE

## ✅ MCP Server is Running!

**Server Status:** ACTIVE  
**Database:** commission_ax  
**URL:** https://erp.sgctech.ai  
**Instance:** odoo-commission-ax  
**Available Tools:** 11

---

## 🔍 PHASE 1: INSPECT AVAILABLE MODULES

### Command 1: Get ALL Uninstalled Modules

Use Claude to execute this:

```
Execute this in commission_ax:
Search ir.module.module where state != 'installed'
Return fields: name, technical_name, version, description, state
Order by: category, name

Show me all available modules with their versions and descriptions.
```

**What this shows:**
- Module name and technical identifier
- Version number
- Current state (uninstalled, installed, broken)
- Module description
- Category

---

### Command 2: List Modules by Category

```
In commission_ax, show me:
- All modules grouped by category
- For each category, count how many are installed vs uninstalled
- Highlight commission-related modules

Format: Category | Module Name | Version | State
```

**What this shows:**
- Module organization
- Installation coverage by category
- Which modules exist for commissions

---

### Command 3: Get Detailed Module Dependencies

```
In commission_ax, for each uninstalled module:
1. Get the 'depends' field (list of required modules)
2. Check if those dependencies are installed
3. Identify any modules with ALL deps already installed (can install immediately)

Show format:
Module: [name]
  Version: [version]
  Dependencies: [list]
  Status: Ready to Install / Waiting for: [missing]
```

---

## 📊 PHASE 2: ANALYZE COMMISSION MODULES

### Command 4: Find Commission-Related Modules

```
Search for all modules in commission_ax with 'commission' in the name
Show:
- Full module name
- Version
- Description
- All dependencies
- Current state

Priority: Which commission modules are NOT installed?
```

---

### Command 5: Check Module Metadata

For each module you want to install, ask:

```
In commission_ax, get the ir.module.module record for [MODULE_NAME]:
{
  "name": full name,
  "module_type": type (application/library),
  "version": current version,
  "description": what it does,
  "depends": required modules,
  "external_dependencies": {python, system},
  "state": current state,
  "installed_version": currently installed version,
  "latest_version": newest version available,
  "sequence": menu order,
  "author": creator
}
```

---

### Command 6: Check for Conflicts

```
Before installing [MODULE]:
1. Get the ir.module.module record
2. Check if any INSTALLED modules have [MODULE] in their conflicts
3. Verify [MODULE] doesn't conflict with anything installed
4. List any modules that depend on [MODULE]

Status: Safe to Install / Conflicts Found
```

---

## ✅ PHASE 3: VERIFY DEPENDENCIES (CRITICAL!)

### Command 7: Dependency Tree Analysis

```
For [MODULE_NAME], analyze the full dependency tree:

1. List direct dependencies (level 1)
2. For each, show THEIR dependencies (level 2)
3. Continue until you reach modules with no deps (level 0)
4. Check each module's installation status
5. Identify installation order (must install bottom-up)

Format:
[MODULE] (uninstalled)
├── dep1 (installed) ✓
├── dep2 (uninstalled) ⚠️
│   ├── sub_dep1 (installed) ✓
│   └── sub_dep2 (installed) ✓
└── dep3 (installed) ✓
```

---

### Command 8: Check for Circular Dependencies

```
In commission_ax database:
Search for any circular dependency patterns:
- Module A requires B
- Module B requires A

Check the top 20 uninstalled modules for this pattern.
Result: Safe / Circular Dependencies Found
```

---

## 🛠️ PHASE 4: SAFETY VERIFICATION (BEFORE INSTALL!)

### Command 9: Pre-Installation Checklist

```
For [MODULE_NAME], verify these ALL are TRUE:

✓ CHECK 1: Module Record Found
  Search ir.module.module where name = '[MODULE_NAME]'
  Result: Record exists

✓ CHECK 2: State is Uninstalled
  Get state field: Should be 'uninstalled' (not 'broken')
  Result: [state]

✓ CHECK 3: Dependencies Installed
  Get depends field: [list]
  For each, verify state = 'installed'
  Result: All Ready / Missing: [list]

✓ CHECK 4: No Conflicts
  Verify no installed modules conflict with this
  Result: Clear

✓ CHECK 5: External Dependencies
  Check external_dependencies field (Python, system libs)
  Result: Available / Missing: [list]

✓ CHECK 6: Version Compatible
  Check if version matches current Odoo version
  Result: Compatible / Incompatible

✓ CHECK 7: Button Available
  Verify button_install action is available
  Result: Can execute
```

---

## 🚀 PHASE 5: INSTALLATION EXECUTION

### Command 10: Execute Installation

```
Install [MODULE_NAME] in commission_ax:

STEP 1: Locate Module
  Search ir.module.module where name = '[MODULE_NAME]'
  Get the ID

STEP 2: Call Install
  Execute button_install action on the module

STEP 3: Monitor
  Wait for installation to complete

STEP 4: Verify State
  Check state field - should now be 'installed'
  Check installed_version - should equal latest

STEP 5: Confirm Success
  Installation complete: [yes/no]
```

---

### Command 11: Post-Installation Verification

```
After installing [MODULE_NAME]:

CHECK 1: State Verification
  ir.module.module - state should be 'installed'
  Result: [state]

CHECK 2: Models Created
  Search ir.model where module = '[MODULE_NAME]'
  How many models were created?
  List them

CHECK 3: Views Created
  Search ir.ui.view where module = '[MODULE_NAME]'
  How many views exist?
  List main ones

CHECK 4: Menus Created
  Search ir.ui.menu where module = '[MODULE_NAME]'
  How many menu items?
  List them

CHECK 5: Actions Created
  Search ir.actions.act_window where module = '[MODULE_NAME]'
  How many actions exist?

CHECK 6: Data Records
  Search any default data created
  Show sample records

CHECK 7: No Errors
  Check system logs/debug for [MODULE_NAME] errors
  Result: No errors / Errors found: [list]
```

---

## 📋 RECOMMENDED MODULES TO INSPECT FIRST

### High Priority (Core)
1. **account** - Accounting (if not installed)
2. **sale** - Sales (likely already installed)
3. **purchase** - Purchasing
4. **stock** - Inventory

### Commission-Specific (Main Target!)
1. **sale_commission** - Commission engine
2. **commission_rules** - Rule configuration
3. **partner_commission** - Partner commissions
4. Custom commission modules

### Utility
1. **web_analytics** - Dashboard analytics
2. **report** - Report generator
3. **api** - REST API

---

## 🎯 QUICK START SEQUENCE

### Step 1: List Everything
```
"Get all uninstalled modules in commission_ax with versions and deps"
```

### Step 2: Find Commission Modules
```
"Which modules have 'commission' in their name or description?"
```

### Step 3: Pick One to Install
```
"What are the dependencies for [SELECTED_MODULE]? Are they all installed?"
```

### Step 4: Verify Safety
```
"Run the 9-point pre-installation checklist for [MODULE]"
```

### Step 5: Install
```
"Install [MODULE] in commission_ax and monitor the process"
```

### Step 6: Test
```
"After installation, verify [MODULE] is working by checking:
- Models exist
- Menus appear  
- No errors in logs
- Core functionality works"
```

---

## 🔧 ADVANCED COMMANDS

### Get Exact Module Definition
```
Search ir.module.module where id = [MODULE_ID]
Read all fields and show complete definition
```

### Check Module Size
```
Search ir.model where module = '[MODULE]'
Count total models: [count]
Search ir.ui.view where module = '[MODULE]'
Count total views: [count]
Search ir.ui.menu where module = '[MODULE]'
Count total menus: [count]
```

### Test Module Action
```
Search ir.actions.act_window where res_model = '[MODULE_MODEL]'
Get the action details
Show what happens when action is called
```

---

## ⚠️ CRITICAL RULES

1. **ALWAYS check dependencies first** - Never install without verifying deps
2. **State MUST be uninstalled** - Broken modules will fail
3. **Install bottom-up** - Dependencies BEFORE dependents
4. **One at a time** - Install one module, test, then move to next
5. **Document everything** - Keep track of what you install

---

## 📊 INSTALLATION LOG TEMPLATE

```
MODULE: _______________________
DATE: _______________________
INSTALLER: _______________________

PRE-INSTALLATION:
□ Module found: ID=_______
□ State confirmed: uninstalled
□ Dependencies: ________________
  - All installed? YES/NO
□ Conflicts: None found
□ External deps: Available
□ Version: Compatible
□ Button: Available

INSTALLATION:
□ button_install executed
□ No errors during install
□ Time taken: _______ seconds
□ State now: installed
□ Version: _______

POST-INSTALLATION:
□ Models created: _______ count
□ Views created: _______ count
□ Menus created: _______ count
□ Actions: _______ available
□ Default data: Created/None
□ Errors: None/List: _______
□ Functionality: WORKS/ISSUES

STATUS: ✅ SUCCESS / ⚠️ ISSUES / ❌ FAILED
NOTES:
_________________________________
_________________________________
```

---

## 🎓 EXAMPLE: FULL INSTALLATION WALKTHROUGH

**Goal: Install sale_commission module**

```
STEP 1: DISCOVER
Claude: "Get all uninstalled modules with 'commission' in name"
Result: sale_commission, commission_rules, partner_commission

STEP 2: ANALYZE
Claude: "Show details for sale_commission:
- Version
- Description
- Dependencies
- State"
Result: Version 17.0, state=uninstalled, depends=[sale, account, base]

STEP 3: VERIFY DEPS
Claude: "Check if these are installed in commission_ax: sale, account, base"
Result: All installed ✓

STEP 4: SAFETY CHECK
Claude: "Run pre-install checklist for sale_commission"
Result: All 7 checks passed ✓

STEP 5: INSTALL
Claude: "Execute button_install for sale_commission"
Result: Installation complete, state=installed ✓

STEP 6: TEST
Claude: "Verify sale_commission:
- Models exist (count them)
- New menus visible
- No errors
- Can create a commission record"
Result: ✅ All working perfectly!
```

---

## 🚀 YOU'RE READY!

Your MCP server is connected to commission_ax and ready to inspect and install modules.

**Start with:**

```
"Show me all uninstalled modules in commission_ax. 
For each, display: name, version, description, and dependencies."
```

Then follow the steps above to safely inspect and install!

---

**Backend Connection Status: ✅ ACTIVE**  
**Database: commission_ax**  
**Ready to Inspect & Install: YES**
