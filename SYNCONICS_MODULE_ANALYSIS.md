# Synconics BI Dashboard - Module Analysis & Testing Report

## Module Information
- **Name:** Synconics BI Dashboard
- **Version:** 1.0 (Claims v18.0 compatibility)
- **Author:** Synconics Technologies Pvt. Ltd.
- **Category:** Web
- **License:** OPL-1 (Odoo Proprietary License)

## Critical Compatibility Issues Identified

### 1. **Asset Bundle Conflicts**
**Problem:** Module loads excessive external JavaScript libraries directly into `web.assets_backend`:
- `html2canvas.js` (~150KB)
- `jspdf.js` (~300KB)
- `amcharts/` suite (multiple files, ~500KB+)
- `gridstack/` library (entire directory)

**Impact:** When minified by Odoo's asset bundler, these cause:
```
TypeError: Cannot read properties of undefined
at web.assets_web_dark.min.js:17507
```

**Why it fails:**
1. Third-party libraries aren't designed for Odoo's asset bundling
2. Global scope conflicts (multiple library instances)
3. Missing dependencies in manifest
4. No lazy-loading implementation

### 2. **Odoo 17 Compatibility**
**Version Mismatch:**
- Module claims "BI Dashboard v18.0"
- Dependencies only declare: `["web", "mail"]`
- No explicit `"version": "17.0"` matching Odoo 17

**Required for Odoo 17:**
```python
"version": "17.0.1.0.0"  # Not "1.0"
```

### 3. **External Dependencies**
**Python:** Requires `imgkit==1.2.3`
- Related to image rendering (HTML to image)
- May need system dependencies: `wkhtmltopdf` or `chromium`

## File Structure Analysis

```
synconics_bi_dashboard/
├── __manifest__.py          # Module definition (ISSUE: version mismatch)
├── __init__.py              # Empty or minimal
├── models/                  # ORM models
├── views/                   # XML view definitions
├── security/                # Access control rules
├── data/                    # Initial data
├── wizard/                  # Wizard forms
├── static/
│   └── src/
│       ├── lib/             # PROBLEM: 500+ MB of external libraries
│       │   ├── html2canvas.js
│       │   ├── jspdf.js
│       │   ├── amcharts/    # Multiple chart libraries
│       │   ├── gridstack/   # Dashboard grid system
│       │   └── themes/      # Theme files
│       ├── js/              # Custom JavaScript (poorly integrated)
│       ├── components/      # Vue/Owl components
│       └── scss/            # Stylesheets
└── requirements.txt         # imgkit==1.2.3
```

## Root Cause Analysis

### Why Asset Bundling Fails:
1. **No Module Exports:** Libraries loaded without proper ES6 module syntax
2. **Global Pollution:** Each library extends global scope
3. **Cyclic Dependencies:** amcharts subfolder dependencies
4. **Minification Errors:** Complex regex patterns break under aggressive minification
5. **Missing Polyfills:** No compatibility layer for Odoo's OWL framework

### Why Browser Shows "You are offline":
- Asset bundle load fails
- JavaScript initialization fails
- Session/communication broken
- Browser can't establish Odoo connection

## Testing Strategy for Docker

### Step 1: Prepare Docker Module
```bash
# Copy to Docker addons
cp -r test_modules/synconics_bi_dashboard /mnt/extra-addons/

# Verify in Docker container
docker exec odoo17_test ls -la /mnt/extra-addons/synconics_bi_dashboard
```

### Step 2: Install with Monitoring
```bash
# Watch logs in real-time
docker logs -f odoo17_test

# Install via Odoo CLI (in separate terminal)
docker exec odoo17_test odoo-bin -c /etc/odoo/odoo.conf -d test_db \
  -i synconics_bi_dashboard --stop-after-init
```

### Step 3: Test Asset Generation
```bash
# Check if assets compile without errors
docker exec odoo17_test curl http://localhost:8069/web

# Inspect browser console for JavaScript errors
# Expected errors: TypeError in asset bundle
```

### Step 4: Verify Database State
```bash
# Check module installation status
docker exec odoo17_postgres psql -U odoo -d test_db -c \
  "SELECT name, state FROM ir_module_module WHERE name='synconics_bi_dashboard';"
```

## Recommended Fixes (by Priority)

### CRITICAL:  Fix Asset Loading
```python
# Option 1: Remove external libraries from asset bundling
"assets": {
    "web.assets_backend": [
        # Only custom OWL components
        "synconics_bi_dashboard/static/src/components/**/*",
    ],
    # Load libraries lazily
    "web.assets_frontend": [
        "synconics_bi_dashboard/static/src/lib/html2canvas.js",
    ]
}

# Option 2: Lazy-load all third-party libraries
# Use dynamic imports in JavaScript:
import('synconics_bi_dashboard/static/src/lib/html2canvas.js')
  .then(module => { /* use module */ })
```

### HIGH: Fix Version Declaration
```python
# Current (WRONG):
"version": "1.0",

# Correct:
"version": "17.0.1.0.0",
```

### MEDIUM: Add System Dependencies
```
requirements.txt should include:
imgkit==1.2.3
wkhtmltopdf  # or install separately

# Docker should have:
apt-get install -y wkhtmltopdf chromium
```

### LOW: Fix JavaScript Integration
- Convert to proper ES6 modules
- Remove global scope pollution
- Add Odoo OWL framework compatibility
- Implement proper error handling

## Testing Results Expected

### ❌ Current Behavior (Will Fail):
1. Module installs but asset bundle fails
2. Browser console: "TypeError: Cannot read properties"
3. User sees "You are offline" message
4. WebSocket connection fails
5. Dashboard pages don't load

### ✅ After Fixes:
1. Module installs cleanly
2. Asset bundles compile without errors
3. Dashboard pages load
4. Charts render properly
5. No JavaScript errors in console

## Docker Testing Checklist

- [ ] Module copied to `/mnt/extra-addons/`
- [ ] Docker container sees module in `ls -la /mnt/extra-addons/`
- [ ] Odoo log shows "Loading module synconics_bi_dashboard"
- [ ] Database shows module state (installed/uninstalled)
- [ ] Asset bundle generation attempted (check logs)
- [ ] Browser console checked for JavaScript errors
- [ ] Login page loads without errors
- [ ] Module menu appears in Odoo (if installation succeeds)

## Conclusion

The **synconics_bi_dashboard module is NOT compatible with Odoo 17** in its current form.

Primary issues:
1. Asset bundling incompatibility (blocker)
2. Version declaration mismatch
3. Missing system dependencies
4. Poor JavaScript integration

**Recommendation:** 
- Contact Synconics for an Odoo 17-compatible version
- OR hire developers to refactor the module
- OR use Odoo's built-in reporting/dashboards instead

---

**Test Date:** 2026-01-22
**Odoo Version:** 17.0
**Docker Container:** odoo17_test
