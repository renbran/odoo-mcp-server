# 📦 Commission_AX - Module Installation Guide

## 🎯 Objective
Review, analyze, and safely install available modules in the **commission_ax** database with full stability verification.

---

## 🔍 Step 1: Discover Available Modules

### Commands to Use in Claude:

```
1. "Get all ir.module.module records where state != 'installed' from commission_ax"

2. "Search for modules in commission_ax database that are available but not installed"

3. "List all module names, versions, and states in commission_ax"

4. "Show me modules with dependencies in the commission_ax database"
```

### What to Look For:
- ✅ **Module State**: Should be `"uninstalled"` (not "broken")
- ✅ **Dependencies**: Clear list of required modules
- ✅ **Version**: Compatible with current Odoo version
- ✅ **Category**: Type of module (accounting, sales, etc.)
- ✅ **Stability**: Check if mature/stable

---

## 🛠️ Step 2: Analyze Module Details

Once you identify a module you want to install, ask Claude:

```
"Get detailed information about the [MODULE_NAME] module:
- Description
- Dependencies
- Current version
- Last update
- Install state"
```

### Critical Module Attributes:
```python
{
    "name": "Technical name (e.g., account_accountant)",
    "module_type": "Type (application/library)",
    "version": "Version number",
    "description": "What it does",
    "depends": ["List of required modules"],
    "external_dependencies": {"python": [], "bin": []},
    "installed_version": "Current version if installed",
    "state": "installed/uninstalled/broken",
    "latest_version": "Available version",
    "url": "Module author URL",
    "auto_install": True/False
}
```

---

## 📋 Step 3: Dependency Validation

Before installing, check ALL dependencies:

```
"For the [MODULE_NAME] module in commission_ax:
1. List all direct dependencies
2. Check if each dependency is installed
3. Find any missing or broken dependencies
4. Detect circular dependencies"
```

### Dependency Resolution Chart:
```
module_name
├── depends: [dep1, dep2, dep3]
│   ├── dep1
│   │   └── depends: [sub_dep1]
│   ├── dep2
│   │   └── depends: []
│   └── dep3
│       └── depends: [sub_dep1, sub_dep2]
└── Status: ✅ All deps available
```

---

## 🔒 Step 4: Safety Checks (BEFORE INSTALLATION)

### Create a Pre-Installation Checklist:

```
Ask Claude:
"Verify these safety checks for installing [MODULE]:

1. STATE CHECK: state = 'uninstalled' ✓
2. DEPENDENCY CHECK: All depends are installed ✓
3. CONFLICT CHECK: No conflicting modules ✓
4. STABILITY CHECK: Not marked as 'broken' ✓
5. VERSION CHECK: Compatible with current Odoo ✓
6. EXTERNAL DEPS: Python packages available ✓
7. DATABASE BACKUP: Created before install ✓"
```

---

## ✅ Step 5: Installation Process

### Safe Installation Steps:

**5.1 Prepare for Installation**
```
Ask Claude:
"Show me the ir.module.module record for [MODULE_NAME] 
and verify button_install is available"
```

**5.2 Execute Installation**
```
Ask Claude:
"Install the [MODULE_NAME] module in commission_ax by:
1. Reading the ir.module.module record
2. Calling the button_install action
3. Wait for installation to complete
4. Verify state changed to 'installed'"
```

**5.3 Verify Installation**
```
Ask Claude:
"After installing [MODULE_NAME]:
1. Confirm state = 'installed'
2. Check installed_version matches latest_version
3. Verify all menus appeared if it's an app
4. Test key functionality"
```

---

## 🧪 Step 6: Functionality Testing

### Test Matrix:

| Test | Command | Expected |
|------|---------|----------|
| **Menu Visibility** | "Show menus for [MODULE]" | New menus appear |
| **Model Creation** | "Can you access [MODULE] models?" | Models accessible |
| **Default Records** | "Get default data for [MODULE]" | Data exists |
| **Permissions** | "Check access rights for [MODULE]" | Proper access |
| **Links/Buttons** | "Test [MODULE] action buttons" | Works without errors |

---

## 🚀 Recommended Modules for Commission_AX

### Common Modules to Check:

**Core Financial:**
- `account` - Accounting
- `account_accountant` - Advanced Accounting
- `sale` - Sales Management
- `purchase` - Purchase Management
- `stock` - Inventory
- `mrp` - Manufacturing

**Commission-Specific (likely):**
- `sale_commission` - Commission calculations
- `commission_rules` - Commission rules engine
- `partner_commission` - Commission tracking
- Custom commission modules

**Integrations:**
- `payment` - Payment processing
- `api` - REST API
- `web_services` - Web service integration

**Reporting:**
- `report` - Report engine
- `web_analytics` - Analytics
- `dashboard` - Dashboards

---

## 📊 Installation Checklist Template

```
MODULE: _______________
DATE: _______________
INSTALLER: _______________

PRE-INSTALLATION:
□ Module state verified: uninstalled
□ All dependencies identified
□ All dependencies installed
□ No conflicting modules
□ No circular dependencies
□ External dependencies available
□ Database backup created

INSTALLATION:
□ button_install executed
□ No errors during installation
□ State changed to installed
□ Installed version correct

POST-INSTALLATION:
□ New menus visible in UI
□ Models accessible
□ Default records created
□ Permissions correct
□ Key functionality tested
□ No console errors

STATUS: ✅ STABLE / ⚠️ ISSUES / ❌ FAILED

NOTES:
_________________________________
_________________________________
_________________________________
```

---

## 🔧 Troubleshooting

### If Installation Fails:

```
Ask Claude:
"The [MODULE_NAME] installation failed. 
Show me:
1. The error message in technical details
2. Which dependency is missing
3. Is the module state marked as 'broken'?
4. Can we fix dependencies and retry?"
```

### If Module Appears Broken:

```
"The [MODULE] state is 'broken'. 
Can you:
1. Identify what caused the broken state
2. Check for missing dependencies
3. Try to uninstall and reinstall
4. Review system logs for errors?"
```

### If No Menu Items Appear:

```
"After installing [MODULE], no menus appeared.
Check:
1. Does ir.ui.menu exist for this module?
2. Are menus marked as active?
3. Are there permission issues?
4. Check module manifest for menu definitions"
```

---

## 📚 Key Odoo Models for Module Management

| Model | Use Case |
|-------|----------|
| `ir.module.module` | List/manage all modules |
| `ir.model` | See all models in a module |
| `ir.model.fields` | See all fields |
| `ir.ui.menu` | Module menus |
| `ir.ui.view` | Module views |
| `ir.actions.act_window` | Module actions |

---

## 🎯 Quick Start

**In Claude Desktop, run this sequence:**

### Phase 1: Discovery (5 min)
```
1. "Get all uninstalled modules in commission_ax"
2. "For each module, show name, version, and dependencies"
3. "Which modules are most important?"
```

### Phase 2: Analysis (10 min)
```
1. "Analyze the [SELECTED_MODULE] dependencies"
2. "Verify all deps are installed or available"
3. "Check for any stability issues"
```

### Phase 3: Installation (5 min)
```
1. "Install [MODULE_NAME] and monitor progress"
2. "Verify state changed to installed"
3. "Test that menus/features appeared"
```

### Phase 4: Validation (5 min)
```
1. "Verify [MODULE] functionality"
2. "Test key features"
3. "Check for any errors"
```

---

## 💡 Pro Tips

1. **Always check dependencies first** - Cascading failures hurt
2. **Install in dependency order** - Bottom-up installation
3. **Test after each installation** - Catch issues early
4. **Use Claude to automate checks** - Speed up analysis
5. **Document everything** - Track what was installed and why
6. **Keep backups** - Always have recovery options

---

## 🎓 Example: Full Installation Walkthrough

Let's say you want to install `sale_commission`:

```
STEP 1: Discover
Claude: "Get all modules matching 'commission' in commission_ax"
Result: Lists available commission modules

STEP 2: Analyze
Claude: "Get detailed info about sale_commission:
- Current state
- Dependencies  
- Version
- Description"
Result: Shows it needs [sale, account, base]

STEP 3: Check Deps
Claude: "Verify these modules are installed:
- sale ✓ installed
- account ✓ installed  
- base ✓ installed
All dependencies met!"

STEP 4: Install
Claude: "Install sale_commission module"
Result: Installation completes, state = 'installed'

STEP 5: Test
Claude: "Test sale_commission:
- Show commission models
- Test commission calculations
- Verify commission menus"
Result: ✅ All working perfectly!
```

---

**Ready to discover and install modules? Start with:**

```
"Get all uninstalled modules in commission_ax database with their names, 
versions, and dependencies. Order by importance."
```
