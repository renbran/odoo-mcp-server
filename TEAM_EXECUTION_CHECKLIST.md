# Odoo 17 Sales Dashboard Fix - Team Execution Checklist
**Completed: Jan 19, 2026**  
**Server**: 139.84.163.11 | **Database**: osusproperties | **Module**: osus_sales_invoicing_dashboard

---

## Problem Summary
Dashboard field error: `sales_order_type_id field is undefined` prevented the dashboard from loading.

**Root Cause**: Model had duplicate contradictory field definitions:
- `sales_order_type_id` (many2one) - **SHOULD NOT EXIST**
- `sales_order_type_ids` (many2many) - **CORRECT**

View XML referenced only the plural form, but database had both, causing QWeb template to crash.

---

## Solution Overview
**4-Step Fix**:
1. Remove singular field definition from Python source code
2. Delete stale field from database
3. Force module reload to rebuild fields
4. Restore complete dashboard view architecture

---

## Step-by-Step Execution Guide

### PHASE 1: Code Cleanup (5 minutes)

#### Step 1.1: Verify Code State
```bash
# SSH to server
ssh -i ~/.ssh/id_ed25519_139.84.163.11 root@139.84.163.11

# Check for singular field definition (should return 0 matches)
grep -n 'sales_order_type_id[^s]' \
  /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard/models/sales_invoicing_dashboard.py

# Expected: (no output = success)
```

#### Step 1.2: Edit Model File (if not done)
If grep found matches, edit the model file:
```bash
nano /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard/models/sales_invoicing_dashboard.py
```

Remove this block (if present):
```python
sales_order_type_id = fields.Many2one(
    'sale.order.type',
    string='Sales Order Type (Single)',
    help='DO NOT USE - Use sales_order_type_ids instead'
)
```

Keep this (correct definition):
```python
sales_order_type_ids = fields.Many2many(
    'sale.order.type',
    string='Sales Order Types',
    help='Filter dashboard by selected order types'
)
```

---

### PHASE 2: Database Cleanup (3 minutes)

#### Step 2.1: Delete Stale Field from Database
```bash
# Connect to PostgreSQL
psql -U odoo -d osusproperties

# Execute in psql:
DELETE FROM ir_model_fields 
WHERE model_id=(SELECT id FROM ir_model WHERE model='osus.sales.invoicing.dashboard') 
  AND name='sales_order_type_id';

# Verify deletion
SELECT name, ttype FROM ir_model_fields 
WHERE model_id=(SELECT id FROM ir_model WHERE model='osus.sales.invoicing.dashboard') 
  AND name LIKE 'sales_order%'
ORDER BY name;

# Expected output:
#          name         |   ttype   
# ----------------------+-----------
#  sales_order_type_ids | many2many
# (1 row)
```

---

### PHASE 3: Module Reload (8 minutes)

#### Step 3.1: Mark Module for Upgrade
```bash
# In psql:
UPDATE ir_module_module 
SET state='to upgrade' 
WHERE name='osus_sales_invoicing_dashboard';
```

#### Step 3.2: Restart Service
```bash
# Exit psql
\q

# Restart the service
systemctl restart odoo-osusproperties

# Wait 12 seconds for startup
sleep 12

# Verify service is running
systemctl status odoo-osusproperties | grep -E '(Active|Main PID)'

# Expected: Active: active (running)
```

#### Step 3.3: Verify Module State
```bash
# In psql:
psql -U odoo -d osusproperties

SELECT name, state FROM ir_module_module 
WHERE name='osus_sales_invoicing_dashboard';

# Expected: state = 'installed' (not 'to upgrade')

# Verify field count decreased
SELECT COUNT(*) as total_fields FROM ir_model_fields 
WHERE model_id=(SELECT id FROM ir_model WHERE model='osus.sales.invoicing.dashboard');

# Expected: 40 (was 41 before fix)
```

---

### PHASE 4: View Restoration (5 minutes)

#### Step 4.1: Update View with Complete Dashboard Arch
```bash
# Create Python script to extract and update arch
python3 << 'PYTHON_SCRIPT'
import json
import psycopg2

# Read the form arch from source file
with open('/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard/views/dashboard_views.xml', 'r') as f:
    content = f.read()

# Extract the arch section (between <field name="arch" type="xml"> and </field>)
start = content.find('<field name="arch" type="xml">') + len('<field name="arch" type="xml">')
end = content.find('</field>', start)
arch_content = content[start:end].strip()

# Format as JSON for database
db_format = json.dumps({'en_US': arch_content})

# Connect and update database
conn = psycopg2.connect("dbname=osusproperties user=odoo")
cur = conn.cursor()

# Update view 6962 (the dashboard form view)
cur.execute(
    "UPDATE ir_ui_view SET arch_db = %s WHERE id = 6962",
    (db_format,)
)

affected = cur.rowcount
conn.commit()
cur.close()
conn.close()

print(f'✓ Updated {affected} view record(s) with {len(arch_content)} bytes of dashboard XML')
PYTHON_SCRIPT
```

---

### PHASE 5: Cache Clear & Final Restart (5 minutes)

#### Step 5.1: Clear Caches
```bash
# Clear asset files
rm -rf /var/odoo/osusproperties/.local/share/Odoo/filestore/osusproperties/assets/*

# Clear Python cache
rm -rf /var/odoo/osusproperties/.cache/Odoo/*

echo "Cache cleared"
```

#### Step 5.2: Final Service Restart
```bash
systemctl restart odoo-osusproperties

# Wait for stabilization
sleep 12

# Verify
systemctl status odoo-osusproperties | grep Active

# Expected: Active: active (running)
```

---

### PHASE 6: Verification (3 minutes)

#### Step 6.1: Test Basic Connectivity
```bash
# Test via curl
curl -s -H 'Host: erposus.com' http://localhost:8070/web | head -5

# Expected: HTML response with no "field undefined" errors
```

#### Step 6.2: Test Dashboard in Browser
1. Navigate to: **http://erposus.com/web**
2. Login if needed
3. Click on **Sales Dashboard** or navigate to:
   - Menu: Sales → Dashboards → Sales & Invoicing Dashboard
   - Or direct URL: `http://erposus.com/web#action=osus_sales_invoicing_dashboard.action_elite_dashboard`

#### Step 6.3: Verify Dashboard Loads
- ✓ Dashboard loads without JavaScript errors
- ✓ All KPI cards visible (Total Booked Sales, Total Invoiced, Outstanding, Collected)
- ✓ Filters work (Booking Date, Order Types, Salesperson, Customer)
- ✓ Charts render correctly
- ✓ Analysis tables display
- ✓ Export buttons visible

---

## Validation SQL Queries

Run these to confirm fix is complete:

```sql
-- Check: Only plural field exists
SELECT name, ttype FROM ir_model_fields 
WHERE model_id=(SELECT id FROM ir_model WHERE model='osus.sales.invoicing.dashboard') 
AND name LIKE 'sales_order%';
-- EXPECTED: 1 row | sales_order_type_ids | many2many

-- Check: Module is installed
SELECT name, state FROM ir_module_module 
WHERE name='osus_sales_invoicing_dashboard';
-- EXPECTED: installed

-- Check: View has full arch
SELECT id, name, LENGTH(arch_db) as arch_size FROM ir_ui_view 
WHERE id=6962;
-- EXPECTED: id=6962 | arch_size > 10000 (should be ~19KB)

-- Check: Dashboard record exists
SELECT id, name FROM osus_sales_invoicing_dashboard;
-- EXPECTED: 1 row (singleton record)
```

---

## Rollback Plan (if issues occur)

### Quick Rollback to Previous State
If you need to revert, use the backup:
```bash
# Restore from backup
cp /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard/backups/20260107_202256/dashboard_views.xml \
   /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard/views/dashboard_views.xml

# Restart module
systemctl restart odoo-osusproperties
```

---

## Timeline
- **Phase 1 (Code Cleanup)**: 5 min
- **Phase 2 (Database Cleanup)**: 3 min
- **Phase 3 (Module Reload)**: 8 min
- **Phase 4 (View Restoration)**: 5 min
- **Phase 5 (Cache & Restart)**: 5 min
- **Phase 6 (Verification)**: 3 min
- **Total**: ~30 minutes (mostly waiting for service restarts)

---

## Key Files Modified
- `/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard/models/sales_invoicing_dashboard.py` (singular field removed)
- `ir_model_fields` table (1 row deleted)
- `ir_ui_view` table id=6962 (arch_db restored)
- `ir_module_module` table (module upgraded)

---

## Success Criteria
- [x] Dashboard loads at erposus.com/web
- [x] No "field undefined" errors in console
- [x] All dashboard elements render correctly
- [x] Filters functional
- [x] No 502 Bad Gateway errors

---

## Support
If issues persist:
1. Check `/var/log/odoo-osusproperties.log` for errors
2. Run `psql` queries above to verify database state
3. Ensure Python field definition is completely clean (no singular form references)
4. Contact: DevOps team with logs

