# Manual Installation & Testing Guide
## Step-by-Step for Brokerage Deal Tracking Enhancement

---

## PHASE 1: PREPARE DEPLOYMENT FILES

### Step 1: Get All Source Files

The following files have been created and are ready to deploy:

1. **Python Model Extensions:**
   - `sale_order_deal_tracking_ext.py` - Extends sale.order with deal fields
   - `account_move_deal_tracking_ext.py` - Extends account.move with deal fields

2. **XML Views:**
   - `sale_order_deal_tracking_views.xml` - Forms and tree views for sale orders
   - `account_move_deal_tracking_views.xml` - Forms and views for invoices

3. **Supporting Documentation:**
   - This file (manual guide)
   - `INSTALLATION-CHECKLIST.md` - Verification checklist
   - `TESTING-GUIDE.md` - Comprehensive test cases

---

## PHASE 2: BACKUP BEFORE INSTALLATION

### Step 1: Backup Database

```bash
# SSH to server
ssh root@139.84.163.11

# Create database backup
mkdir -p /var/odoo/scholarixv2/backups
pg_dump commission_ax > /var/odoo/scholarixv2/backups/commission_ax_$(date +%Y%m%d_%H%M%S).sql

# Verify backup created
ls -lh /var/odoo/scholarixv2/backups/commission_ax_*.sql
```

### Step 2: Backup Module

```bash
# Create module backup
BACKUP_NAME="commission_ax_$(date +%Y%m%d_%H%M%S)"
mkdir -p /var/odoo/scholarixv2/backups/$BACKUP_NAME
cp -r /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/* \
      /var/odoo/scholarixv2/backups/$BACKUP_NAME/

# Verify
ls -la /var/odoo/scholarixv2/backups/$BACKUP_NAME/
```

### Step 3: Stop Odoo Service

```bash
# Stop service
systemctl stop odoo

# Verify stopped
systemctl status odoo
# Should show: inactive (dead)

# Wait for full shutdown
sleep 5
```

---

## PHASE 3: DEPLOY PYTHON FILES

### Step 1: Create source files locally

Create these files on your local machine with the content provided:

**File 1: sale_order_deal_tracking_ext.py**
Location: `d:\01_WORK_PROJECTS\odoo-mcp-server\models\sale_order_deal_tracking_ext.py`

**File 2: account_move_deal_tracking_ext.py**
Location: `d:\01_WORK_PROJECTS\odoo-mcp-server\models\account_move_deal_tracking_ext.py`

### Step 2: Transfer files to server

Using SCP or SFTP:

```bash
# From your local machine, upload to server
scp d:\01_WORK_PROJECTS\odoo-mcp-server\models\sale_order_deal_tracking_ext.py \
    root@139.84.163.11:/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/

scp d:\01_WORK_PROJECTS\odoo-mcp-server\models\account_move_deal_tracking_ext.py \
    root@139.84.163.11:/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/
```

### Step 3: Verify Python files

```bash
# SSH to server
ssh root@139.84.163.11

# List files
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/account_move_deal_tracking_ext.py

# Check syntax
python3 -m py_compile /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py
python3 -m py_compile /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/account_move_deal_tracking_ext.py

# Should complete without errors
echo "✓ Python syntax OK"
```

---

## PHASE 4: DEPLOY XML VIEW FILES

### Step 1: Create XML files

**File 1: sale_order_deal_tracking_views.xml**
Location: `d:\01_WORK_PROJECTS\odoo-mcp-server\views\sale_order_deal_tracking_views.xml`

**File 2: account_move_deal_tracking_views.xml**
Location: `d:\01_WORK_PROJECTS\odoo-mcp-server\views\account_move_deal_tracking_views.xml`

### Step 2: Transfer XML files

```bash
# From your local machine
scp d:\01_WORK_PROJECTS\odoo-mcp-server\views\sale_order_deal_tracking_views.xml \
    root@139.84.163.11:/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/

scp d:\01_WORK_PROJECTS\odoo-mcp-server\views\account_move_deal_tracking_views.xml \
    root@139.84.163.11:/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/
```

### Step 3: Verify XML files

```bash
# SSH to server
ssh root@139.84.163.11

# List files
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/sale_order_deal_tracking_views.xml
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/account_move_deal_tracking_views.xml

# Quick XML syntax check (look for well-formed XML)
xmllint /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/sale_order_deal_tracking_views.xml > /dev/null && echo "✓ XML syntax OK"
xmllint /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/account_move_deal_tracking_views.xml > /dev/null && echo "✓ XML syntax OK"
```

---

## PHASE 5: UPDATE MODULE CONFIGURATION

### Step 1: Update __manifest__.py

```bash
# SSH to server
ssh root@139.84.163.11

# Edit manifest
nano /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/__manifest__.py
```

**Find the `'data'` section and add these lines:**

```python
'data': [
    # ... existing entries ...
    'views/sale_order_deal_tracking_views.xml',
    'views/account_move_deal_tracking_views.xml',
    # ... rest of existing entries ...
],
```

**Example of completed section:**
```python
'data': [
    'security/ir.model.access.csv',
    'views/commission_ax_views.xml',
    'views/commission_ax_templates.xml',
    'views/commission_ax_menus.xml',
    'views/sale_order_deal_tracking_views.xml',      # ADD THIS
    'views/account_move_deal_tracking_views.xml',   # ADD THIS
    'data/commission_ax_demo.xml',
],
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano)

### Step 2: Update models/__init__.py

```bash
# Edit models init
nano /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/__init__.py
```

**Add these lines after other imports:**

```python
from . import sale_order_deal_tracking_ext
from . import account_move_deal_tracking_ext
```

**Example of completed file:**
```python
# -*- coding: utf-8 -*-

from . import commission_ax
from . import commission_po
# ... other existing imports ...
from . import sale_order_deal_tracking_ext      # ADD THIS
from . import account_move_deal_tracking_ext    # ADD THIS
```

**Save and exit**

### Step 3: Verify configuration files

```bash
# Check manifest syntax
python3 -c "import ast; ast.parse(open('/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/__manifest__.py').read())" && echo "✓ Manifest syntax OK"

# Check init syntax
python3 -c "import ast; ast.parse(open('/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/__init__.py').read())" && echo "✓ Init syntax OK"

# Verify entries in manifest
grep -n "sale_order_deal_tracking_views.xml" /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/__manifest__.py && echo "✓ Manifest entry found"

# Verify imports in init
grep -n "sale_order_deal_tracking_ext" /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/__init__.py && echo "✓ Import found"
```

---

## PHASE 6: START ODOO SERVICE

### Step 1: Start the service

```bash
# SSH to server if not already connected
ssh root@139.84.163.11

# Start Odoo
systemctl start odoo

# Wait for startup
sleep 10

# Check status
systemctl status odoo
```

**Expected output:**
```
● odoo.service - Odoo Server
   Loaded: loaded (/etc/systemd/system/odoo.service; enabled; vendor preset: enabled)
   Active: active (running) since ...
```

### Step 2: Monitor startup logs

```bash
# Watch logs during startup (press Ctrl+C to exit)
tail -f /var/log/odoo/odoo-server.log

# Should see messages like:
# [timestamp] commission_ax loaded
# [timestamp] commission_ax installed/updated
# [timestamp] Listening on 0.0.0.0:8069
```

### Step 3: Check for errors

```bash
# Look for error lines
tail -n 100 /var/log/odoo/odoo-server.log | grep -i "error\|critical\|traceback"

# Should find: NOTHING (or only warning-level messages)
```

---

## PHASE 7: UPGRADE MODULE IN ODOO UI

### Step 1: Access Odoo web interface

1. Open browser: **http://139.84.163.11:8069**
2. Login with administrator credentials

### Step 2: Upgrade commission_ax module

**Method A: Using Apps Menu (Recommended)**

1. Click **Settings** (gear icon, top-right)
2. Click **Apps**
3. Search for: `commission_ax`
4. Click on the **commission_ax** module
5. If you see an **"Upgrade"** button:
   - Click it
   - Confirm the upgrade
   - Wait 2-5 minutes for completion
6. If no "Upgrade" button appears:
   - Module is already in sync
   - Close this dialog

**Method B: Using --upgrade Flag (Requires CLI)**

```bash
# SSH to server
ssh root@139.84.163.11

# Stop Odoo
systemctl stop odoo

# Upgrade specific module
cd /var/odoo/scholarixv2
python3 -m odoo -c ./odoo.conf -d commission_ax -u commission_ax --stop-after-init

# Start again
systemctl start odoo
```

### Step 3: Verify upgrade success

1. After upgrade, check the log for errors:
   ```bash
   tail -n 50 /var/log/odoo/odoo-server.log | grep -i "commission_ax"
   ```

2. Expected output:
   ```
   commission_ax ... loaded successfully
   commission_ax ... installed/upgraded
   ```

3. Check for error messages:
   ```bash
   tail -n 100 /var/log/odoo/odoo-server.log | grep -i "error\|traceback"
   ```

   Expected result: No error-level messages

---

## PHASE 8: VERIFY FIELD DEPLOYMENT

### Step 1: Access sale order form

1. In Odoo web interface, go to:
   **Sales → Quotations** (or Sales → Orders)
2. Click any existing sale order (or create test one)
3. Look for section: **"BROKERAGE DEAL INFORMATION"**

**Verify it shows:**
- [ ] Buyer Name (readonly, shows customer name)
- [ ] Project Name (readonly, shows project)
- [ ] Unit Sale Value (readonly, shows price)
- [ ] Primary Commission % (readonly, shows highest rate)
- [ ] Deal Summary HTML (colored box with formatted info)

### Step 2: Verify tree view columns

1. Go to **Sales → Quotations** (list view, not form)
2. Check column headers for:
   - [ ] "Buyer" column
   - [ ] "Project" column
   - [ ] "Unit Price" column
   - [ ] "Commission %" column

### Step 3: Access invoice form

1. Go to **Accounting → Invoices**
2. Open any invoice (especially one created from a sale order)
3. Look for: **"Brokerage Deal Information"** group

**Verify it shows:**
- [ ] Buyer Name field
- [ ] Project Name field
- [ ] Unit Sale Value field
- [ ] Commission % field
- [ ] Deal Information Summary HTML

### Step 4: Verify invoice tree view

1. Stay on **Accounting → Invoices** (list view)
2. Check for new columns showing deal information

---

## PHASE 9: CREATE TEST DATA

### Test 1: Basic Sale Order

**Steps:**
1. Go to **Sales → Quotations → Create**
2. Fill in:
   - **Customer:** Any customer (or create "Test Buyer")
   - **Project:** Any project (or leave blank)
   - **Order Line:**
     - Product: Any product
     - Quantity: 1
     - Price Unit: 100,000
3. Set commission rates:
   - **Manager Rate:** 5%
   - **Agent 1:** 3%
   - **Broker:** 2%
4. Click **Save**

**Verify:**
- [ ] `buyer_name` shows customer name
- [ ] `project_name` shows project name (or empty)
- [ ] `unit_sale_value` shows 100,000
- [ ] `primary_commission_percentage` shows 5
- [ ] `deal_summary_html` displays formatted box
- [ ] HTML has burgundy styling

**Test Result:** ✓ PASS / ✗ FAIL

---

### Test 2: Create Invoice from Sale Order

**Steps:**
1. Open the sale order from Test 1
2. Click **Create Invoice** button
3. In dialog, select "Posted" option (or leave as default)
4. Click **Create Invoice**
5. Open the created invoice

**Verify:**
- [ ] Invoice created successfully
- [ ] "Brokerage Deal Information" group visible
- [ ] All deal fields populated from SO:
  - buyer_name = SO buyer_name
  - project_name = SO project_name
  - unit_sale_value = SO unit_sale_value
  - commission_percentage = SO primary_commission_percentage
- [ ] deal_information_summary displays HTML

**Test Result:** ✓ PASS / ✗ FAIL

---

### Test 3: Test HTML Rendering

**Steps:**
1. Open sale order from Test 1 in Chrome browser
2. Inspect the deal_summary_html section
3. Right-click → Inspect → Check HTML styling
4. Verify colors and layout

**Verify:**
- [ ] Background color: Light gray (#f8f9fa)
- [ ] Border: Left border in burgundy (#8b1538)
- [ ] Text colors: Headers in burgundy, data in dark
- [ ] Table layout: 2x2 grid or similar
- [ ] No overlapping elements
- [ ] Responsive on different screen sizes

**Test Result:** ✓ PASS / ✗ FAIL

---

## PHASE 10: TROUBLESHOOTING

### Issue: Fields not showing in form

**Diagnosis:**
```bash
# Check if XML views were loaded
grep -r "buyer_name" /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/
```

**Solution:**
1. Verify XML files are in `views/` directory
2. Verify manifest lists XML files
3. Restart Odoo: `systemctl restart odoo`
4. Clear browser cache (Ctrl+F5)
5. Try upgrade again: Settings → Apps → commission_ax → Upgrade

### Issue: Odoo won't start

**Diagnosis:**
```bash
# Check logs
tail -n 200 /var/log/odoo/odoo-server.log | grep -i "error\|traceback"

# Check syntax of new files
python3 -m py_compile /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py
```

**Solution:**
1. Restore from backup:
   ```bash
   systemctl stop odoo
   cp -r /var/odoo/scholarixv2/backups/commission_ax_YYYYMMDD_HHMMSS/* \
         /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/
   systemctl start odoo
   ```
2. Check Python syntax for errors
3. Check XML syntax with xmllint

### Issue: Fields compute empty values

**Diagnosis:**
Check compute methods are working:
```bash
# In Odoo UI: Debug → Python Expression
# Try: self.partner_id.name
# Should return customer name
```

**Solution:**
1. Verify @api.depends() decorators match field names
2. Create new sale order (don't use old ones)
3. Check field values in database:
   ```bash
   psql commission_ax -c "SELECT id, buyer_name, project_name FROM sale_order LIMIT 5;"
   ```

### Issue: Invoice doesn't get deal info

**Diagnosis:**
```bash
# Check invoice creation log
tail -n 100 /var/log/odoo/odoo-server.log | grep -i "move\|invoice"
```

**Solution:**
1. Verify SO has all deal fields populated
2. Check _prepare_invoice() method is correct
3. Create new invoice, not converting old invoices
4. Check if sale_order_id is populated on invoice

---

## PHASE 11: SIGN-OFF

**Installation Completed:**
- [x] Files deployed
- [x] Configuration updated
- [x] Service restarted
- [x] Module upgraded
- [x] Fields visible in forms
- [x] Test data created
- [x] Tests passing

**Date Completed:** _________________

**Completed By:** _________________

**Issues Encountered:** 
_________________________________________________________________

**Readiness for Production:**
- [ ] All tests passing
- [ ] No errors in logs
- [ ] Data transferring correctly
- [ ] Team trained
- [ ] Ready to deploy

