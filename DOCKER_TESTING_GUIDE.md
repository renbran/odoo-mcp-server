# Synconics BI Dashboard - Docker Testing Guide

## Current Status

✅ **Module Copied to Docker:** `/mnt/extra-addons/synconics_bi_dashboard`  
✅ **Module Size:** 38.8 MB  
✅ **Container:** odoo17_test  
✅ **Odoo Version:** 17.0  
✅ **Database:** test_db  

---

## How to Test Manually

### Step 1: Access Odoo UI
Open browser and navigate to:
```
http://localhost:8069
```

### Step 2: Install Module via UI
1. Click **"Apps"** (top right)
2. Click **"Manage Modules"** or toggle **"Developer Mode"**
3. Search for **"synconics"**
4. Click module name
5. Click **"Install"** button

### Step 3: Monitor Docker Logs
In a separate terminal, watch the logs:
```bash
docker logs -f odoo17_test
```

### Step 4: Test Asset Compilation
After clicking Install:
1. Docker will attempt to compile assets
2. Watch for lines like:
   ```
   Loading module synconics_bi_dashboard
   Compiling asset bundle...
   ERROR: TypeError in asset compilation
   ```

### Step 5: Check Browser Console
1. Open **Developer Tools** (`F12`)
2. Go to **Console** tab
3. Look for error:
   ```
   Uncaught TypeError: Cannot read properties of undefined
   at web.assets_web_dark.min.js:17507
   ```

---

## Expected Behavior

### ❌ **What Will Happen (Module Incompatibility):**

1. **Installation Appears to Start:**
   - Module shows "Installing..." status
   - Loading spinner appears

2. **Asset Bundle Fails:**
   - Docker logs show compilation errors
   - JavaScript minification fails
   - Error messages about undefined properties

3. **Browser Shows Error:**
   - Page becomes unresponsive
   - Console shows JavaScript TypeError
   - User sees "You are offline" message
   - Module menu may not appear

4. **System State:**
   - Module remains in "to install" state
   - Corrupted asset bundle in database
   - Odoo service may restart

### ✅ **What Should Happen (If Compatible):**

1. Installation completes cleanly
2. Module shows "Installed" status
3. New menu items appear
4. No JavaScript errors in console
5. Dashboard pages load without errors

---

## Docker Testing Commands

### Check Module Directory:
```bash
docker exec odoo17_test bash -c "find /mnt/extra-addons/synconics_bi_dashboard -name '__manifest__' -o -name '*.js' | head -20"
```

### View Module Manifest:
```bash
docker exec odoo17_test bash -c "cat /mnt/extra-addons/synconics_bi_dashboard/__manifest__.py | head -100"
```

### Count JavaScript Files:
```bash
docker exec odoo17_test bash -c "find /mnt/extra-addons/synconics_bi_dashboard -name '*.js' | wc -l"
```

### Check File Sizes:
```bash
docker exec odoo17_test bash -c "du -sh /mnt/extra-addons/synconics_bi_dashboard/static/src/lib/*"
```

### Get Recent Logs:
```bash
docker logs odoo17_test --tail 100 | grep -E "(synconics|error|ERROR|Exception)"
```

---

## How to Fix (If You Want to Continue)

### Option 1: Fix in Docker First
1. Modify `/mnt/extra-addons/synconics_bi_dashboard/__manifest__.py`
2. Change version to `"17.0.1.0.0"`
3. Remove large libraries from `assets` list
4. Reload Odoo

### Option 2: Remove & Use Alternatives
```bash
# Uninstall from Docker
docker exec odoo17_test psql -U odoo -d test_db -c "
  DELETE FROM ir_module_module WHERE name='synconics_bi_dashboard';
"

# Or use Odoo's built-in reporting instead
```

### Option 3: Use Alternative Modules
- **Pivot Tables** - native Odoo feature
- **Reporting** - built-in reporting engine
- **Custom OWL Components** - modern web framework
- **Dashboard Views** - lightweight dashboard system

---

## File Locations Helpful for Debugging

**In Docker Container:**
- Module: `/mnt/extra-addons/synconics_bi_dashboard/`
- Odoo Bin: `/opt/odoo/odoo-bin`
- Config: `/etc/odoo/odoo.conf`
- Database: `test_db` in `odoo17_postgres`

**On Your Machine:**
- Module Copy: `D:/01_WORK_PROJECTS/odoo-mcp-server/test_modules/synconics_bi_dashboard/`
- Analysis Doc: `D:/01_WORK_PROJECTS/odoo-mcp-server/SYNCONICS_MODULE_ANALYSIS.md`
- Test Results: `D:/01_WORK_PROJECTS/odoo-mcp-server/docker_test_install.log`

---

## Summary

The **synconics_bi_dashboard module is incompatible with Odoo 17** due to:

1. **Asset Bundle Issues** - Heavy JavaScript libraries cause compilation errors
2. **Version Mismatch** - Declared as v1.0 instead of v17.0
3. **Missing Dependencies** - No proper imgkit/system dependency setup
4. **Poor Integration** - Libraries not designed for Odoo's bundler

**You can test this in Docker to confirm the error, but the module needs vendor fixes before it will work on production.**

---

**Test Date:** 2026-01-22  
**Docker Container:** odoo17_test  
**Odoo Version:** 17.0  
**Status:** INCOMPATIBLE - Recommended for Rejection
