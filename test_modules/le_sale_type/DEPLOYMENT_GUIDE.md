# Deployment Guide: Sale Order Type - Invoice Integration v1.1.0

## Overview

This guide provides step-by-step instructions for deploying the Sale Order Type module with Invoice Integration (version 1.1.0) to your Odoo 17 production environment.

## Pre-Deployment Checklist

### 1. Environment Verification

- [ ] Odoo 17 is running (verify version: `odoo --version`)
- [ ] Database backup is created
- [ ] Sufficient disk space available
- [ ] No active users (maintenance window scheduled)
- [ ] Access to Odoo server (SSH/RDP)
- [ ] Access to database (PostgreSQL)

### 2. Module Dependencies

Verify these modules are installed:
- [ ] `sale` - Sales Management
- [ ] `account` - Invoicing/Accounting

```bash
# Check from Odoo shell
psql -U odoo -d your_database -c "SELECT name, state FROM ir_module_module WHERE name IN ('sale', 'account');"
```

### 3. Backup Procedures

```bash
# 1. Backup Database
pg_dump -U odoo -d your_database -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# 2. Backup Odoo Addons (optional but recommended)
tar -czf addons_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/odoo/addons

# 3. Backup Filestore
tar -czf filestore_backup_$(date +%Y%m%d_%H%M%S).tar.gz ~/.local/share/Odoo/filestore/your_database
```

## Deployment Methods

### Method A: Fresh Installation (New Module)

Use this if the module is NOT currently installed.

#### Step 1: Copy Module Files

```bash
# Copy the le_sale_type module to your addons directory
cp -r /source/path/le_sale_type /path/to/odoo/addons/

# Set proper permissions
chown -R odoo:odoo /path/to/odoo/addons/le_sale_type
chmod -R 755 /path/to/odoo/addons/le_sale_type
```

#### Step 2: Restart Odoo

```bash
# For systemd service
sudo systemctl restart odoo17

# For manual startup
# Stop: Ctrl+C
# Start: python odoo-bin -c /etc/odoo.conf
```

#### Step 3: Update Apps List

1. Log in as Administrator
2. Navigate to: **Settings → Apps**
3. Click: **Update Apps List** (three dots menu)
4. Click: **Update**

#### Step 4: Install Module

1. Remove "Apps" filter
2. Search: "Sale Order Type"
3. Click: **Install**
4. Wait for installation to complete

#### Step 5: Verify Installation

```bash
# Check module is installed
psql -U odoo -d your_database -c "SELECT name, state, latest_version FROM ir_module_module WHERE name = 'le_sale_type';"
```

Expected output: `state = installed`, `latest_version = 1.1.0`

---

### Method B: Upgrade from Version 1.0

Use this if version 1.0 is already installed.

#### Step 1: Enable Developer Mode

1. Log in as Administrator
2. Go to: **Settings**
3. Scroll to bottom, click: **Activate the developer mode**

#### Step 2: Backup Current Module State

```bash
# Export current module data (optional)
psql -U odoo -d your_database -c "COPY (SELECT * FROM sale_order_type) TO '/tmp/sale_order_type_backup.csv' CSV HEADER;"
psql -U odoo -d your_database -c "COPY (SELECT id, name, sale_order_type_id FROM sale_order WHERE sale_order_type_id IS NOT NULL) TO '/tmp/sale_orders_with_type.csv' CSV HEADER;"
```

#### Step 3: Replace Module Files

```bash
# Backup old module
mv /path/to/odoo/addons/le_sale_type /path/to/odoo/addons/le_sale_type.old

# Copy new version
cp -r /source/path/le_sale_type /path/to/odoo/addons/

# Set permissions
chown -R odoo:odoo /path/to/odoo/addons/le_sale_type
chmod -R 755 /path/to/odoo/addons/le_sale_type
```

#### Step 4: Restart Odoo

```bash
sudo systemctl restart odoo17
# Wait 10-15 seconds for full startup
```

#### Step 5: Upgrade Module

**Option A: Via UI (Recommended)**

1. Log in as Administrator
2. Go to: **Settings → Apps**
3. Remove "Apps" filter (click X)
4. Search: "Sale Order Type"
5. Click: **Upgrade** button
6. Wait for completion (may take 1-2 minutes)
7. Refresh browser

**Option B: Via Command Line**

```bash
# From Odoo directory
python odoo-bin -c /etc/odoo.conf -d your_database -u le_sale_type --stop-after-init

# Then restart normally
sudo systemctl restart odoo17
```

#### Step 6: Verify Upgrade

```bash
# Check version
psql -U odoo -d your_database -c "SELECT latest_version FROM ir_module_module WHERE name = 'le_sale_type';"
# Should show: 1.1.0

# Check new field exists
psql -U odoo -d your_database -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'account_move' AND column_name = 'sale_order_type_id';"
# Should return: sale_order_type_id

# Check index was created
psql -U odoo -d your_database -c "SELECT indexname FROM pg_indexes WHERE tablename = 'account_move' AND indexname LIKE '%sale_order_type%';"
```

---

## Post-Deployment Tasks

### 1. Verify Core Functionality

**Quick Smoke Test:**

1. Open: **Sales → Configuration → Sale Order Types**
2. Verify existing types are still there
3. Create test sale order with type
4. Create invoice from sale order
5. Verify Sale Type auto-filled on invoice

### 2. Check for Errors

```bash
# Check Odoo logs for errors
tail -f /var/log/odoo/odoo-server.log | grep -i error

# Or check systemd logs
journalctl -u odoo17 -f --since "5 minutes ago"
```

### 3. Test All Views

Navigate to: **Invoicing → Customers → Invoices**

Verify:
- [ ] List view shows Sale Type column
- [ ] Form view shows Sale Type field
- [ ] Search by Sale Type works
- [ ] Group By Sale Type works
- [ ] Pivot view includes Sale Type
- [ ] Graph view includes Sale Type

### 4. Validate Existing Data

```sql
-- Check how many existing invoices could have sale type
SELECT
    COUNT(*) as total_invoices,
    COUNT(ail.sale_line_ids) as invoices_from_sales,
    COUNT(am.sale_order_type_id) as invoices_with_type
FROM account_move am
LEFT JOIN account_move_line aml ON am.id = aml.move_id
LEFT JOIN sale_order_line_account_move_line_rel ail ON aml.id = ail.account_move_line_id
WHERE am.move_type = 'out_invoice';
```

### 5. Run Full Test Suite

Execute the comprehensive tests from `TESTING_GUIDE.md`:

```bash
# Minimum critical tests (15-20 minutes):
# - Test 3: Auto-fetch from sale order
# - Test 4: Search by sale type
# - Test 5: Group by sale type
# - Test 6: Credit note propagation
# - Test 11: Supplier bills (negative test)
```

---

## Database Migration (Optional)

If you want to populate sale_order_type_id for existing invoices:

### Automatic Migration Script

```python
#!/usr/bin/env python3
"""
Migrate existing invoices to populate sale_order_type_id
Run via Odoo shell: odoo-bin shell -c /etc/odoo.conf -d your_database < migrate_invoice_types.py
"""

import logging
_logger = logging.getLogger(__name__)

# Get environment
env = self.env

# Find all customer invoices without sale type
invoices = env['account.move'].search([
    ('move_type', 'in', ['out_invoice', 'out_refund']),
    ('sale_order_type_id', '=', False),
])

_logger.info(f"Found {len(invoices)} invoices to process")

updated_count = 0
skipped_count = 0

for invoice in invoices:
    try:
        # Use existing compute method
        invoice._compute_sale_order_type_from_lines()

        if invoice.sale_order_type_id:
            updated_count += 1
            _logger.info(f"Updated invoice {invoice.name} with type {invoice.sale_order_type_id.name}")
        else:
            skipped_count += 1

        # Commit every 100 records
        if (updated_count + skipped_count) % 100 == 0:
            env.cr.commit()
            _logger.info(f"Progress: {updated_count} updated, {skipped_count} skipped")

    except Exception as e:
        _logger.error(f"Error processing invoice {invoice.name}: {str(e)}")
        continue

# Final commit
env.cr.commit()

_logger.info(f"Migration complete: {updated_count} invoices updated, {skipped_count} skipped")
```

Save as `migrate_invoice_types.py` and run:

```bash
odoo-bin shell -c /etc/odoo.conf -d your_database < migrate_invoice_types.py
```

---

## Troubleshooting

### Issue: Module Won't Upgrade

**Symptoms:**
- Upgrade button is greyed out
- Error: "Module not found"

**Solution:**
```bash
# Update apps list first
# Then check module status
psql -U odoo -d your_database -c "SELECT name, state FROM ir_module_module WHERE name = 'le_sale_type';"

# If state is 'to upgrade', force completion
psql -U odoo -d your_database -c "UPDATE ir_module_module SET state='installed' WHERE name='le_sale_type';"

# Then try upgrade again
```

---

### Issue: Field Not Appearing on Invoices

**Symptoms:**
- Sale Type field not visible on invoice form

**Solution:**
```bash
# Check if view was created
psql -U odoo -d your_database -c "SELECT name FROM ir_ui_view WHERE name LIKE '%sale.type%' AND model = 'account.move';"

# If missing, update view list
# In Odoo: Settings → Technical → Views → Refresh
# Or upgrade module with -u flag
```

---

### Issue: Database Error on Invoice Creation

**Symptoms:**
- Error: "column account_move.sale_order_type_id does not exist"

**Solution:**
```bash
# Manually create column (emergency only)
psql -U odoo -d your_database -c "ALTER TABLE account_move ADD COLUMN sale_order_type_id INTEGER REFERENCES sale_order_type(id);"

# Create index
psql -U odoo -d your_database -c "CREATE INDEX idx_account_move_sale_type ON account_move(sale_order_type_id);"

# Then upgrade module
```

---

### Issue: Performance Degradation

**Symptoms:**
- Invoice list loads slowly after upgrade

**Solution:**
```sql
-- Verify index exists
SELECT indexname FROM pg_indexes WHERE tablename = 'account_move' AND indexname LIKE '%sale_order_type%';

-- If missing, create it
CREATE INDEX idx_account_move_sale_type ON account_move(sale_order_type_id);

-- Analyze table
ANALYZE account_move;

-- Update statistics
VACUUM ANALYZE account_move;
```

---

## Rollback Procedures

### Quick Rollback (Keep Module, Remove Views)

If only views are problematic:

```python
# Via Odoo shell
psql -U odoo -d your_database

-- Delete view records
DELETE FROM ir_ui_view WHERE name LIKE '%inherit.sale.type%' AND model = 'account.move';

-- Restart Odoo
\q
sudo systemctl restart odoo17
```

### Full Rollback (Complete Removal)

```bash
# 1. Restore database backup
pg_restore -U odoo -d your_database -c backup_YYYYMMDD_HHMMSS.dump

# 2. Restore old module files
rm -rf /path/to/odoo/addons/le_sale_type
mv /path/to/odoo/addons/le_sale_type.old /path/to/odoo/addons/le_sale_type

# 3. Restart Odoo
sudo systemctl restart odoo17
```

---

## Production Deployment Checklist

### Pre-Deployment (1-2 days before)

- [ ] Staging environment tested successfully
- [ ] All tests passed (see TESTING_GUIDE.md)
- [ ] User training completed
- [ ] Documentation updated
- [ ] Backups verified and tested
- [ ] Maintenance window scheduled
- [ ] Stakeholders notified

### During Deployment

- [ ] Set Odoo to maintenance mode (if available)
- [ ] Create fresh backups
- [ ] Execute deployment steps
- [ ] Run smoke tests
- [ ] Verify critical workflows
- [ ] Check error logs

### Post-Deployment (same day)

- [ ] Remove maintenance mode
- [ ] Notify users of new feature
- [ ] Monitor system for 2-4 hours
- [ ] Run extended test suite
- [ ] Document any issues
- [ ] Update runbook with learnings

### Follow-up (next day)

- [ ] Review overnight logs
- [ ] Check performance metrics
- [ ] Gather user feedback
- [ ] Address any issues
- [ ] Schedule follow-up review

---

## Contact & Support

**Technical Issues:**
- Check logs: `/var/log/odoo/odoo-server.log`
- Odoo documentation: https://www.odoo.com/documentation/17.0/
- Module author: support@lunerpsolution.com

**Emergency Rollback:**
If critical issues arise, execute rollback procedure immediately and document the issue for later resolution.

---

## Deployment Log Template

```
=== DEPLOYMENT LOG ===
Date: _______________
Deployed By: _______________
Environment: Production / Staging
Database: _______________
Odoo Version: _______________

Pre-Deployment:
- Backup Created: [Time] _______________
- Dependencies Verified: ⬜ Yes ⬜ No
- Maintenance Mode: ⬜ Yes ⬜ No

Deployment:
- Start Time: _______________
- Method Used: ⬜ Fresh Install ⬜ Upgrade
- Completion Time: _______________
- Duration: _______________

Post-Deployment:
- Smoke Tests: ⬜ Pass ⬜ Fail
- Error Logs: ⬜ Clean ⬜ Errors Found
- User Testing: ⬜ Pass ⬜ Fail

Issues Encountered:
_______________________________________________
_______________________________________________

Resolution:
_______________________________________________
_______________________________________________

Sign-off:
Deployed By: _______________  Date: ___________
Verified By: _______________  Date: ___________
```

---

**Note:** This deployment has been designed following Odoo best practices and enterprise deployment standards. Always test in a staging environment before production deployment.
