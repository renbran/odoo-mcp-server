# Brokerage Deal Tracking Enhancement - Installation Checklist

## PRE-INSTALLATION

- [ ] Backup Odoo database
  ```bash
  pg_dump commission_ax > /tmp/commission_ax_backup_$(date +%Y%m%d).sql
  ```

- [ ] Backup commission_ax module
  ```bash
  cp -r /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax \
        /var/odoo/scholarixv2/backups/commission_ax_backup_$(date +%Y%m%d)
  ```

- [ ] Stop Odoo service
  ```bash
  systemctl stop odoo
  ```

- [ ] Verify Odoo stopped
  ```bash
  systemctl status odoo  # Should show inactive
  ```

---

## FILE DEPLOYMENT

- [ ] Deploy Python models:
  - [ ] `sale_order_deal_tracking_ext.py` → models/
  - [ ] `account_move_deal_tracking_ext.py` → models/

- [ ] Deploy XML views:
  - [ ] `sale_order_deal_tracking_views.xml` → views/
  - [ ] `account_move_deal_tracking_views.xml` → views/

- [ ] Verify files exist:
  ```bash
  ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py
  ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/account_move_deal_tracking_ext.py
  ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/sale_order_deal_tracking_views.xml
  ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/views/account_move_deal_tracking_views.xml
  ```

---

## CONFIGURATION UPDATES

- [ ] Update `__manifest__.py`:
  ```python
  'data': [
      'views/sale_order_deal_tracking_views.xml',
      'views/account_move_deal_tracking_views.xml',
      # ... other existing entries
  ]
  ```

- [ ] Update `models/__init__.py`:
  ```python
  from . import sale_order_deal_tracking_ext
  from . import account_move_deal_tracking_ext
  ```

- [ ] Verify file syntax:
  ```bash
  python3 -m py_compile /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/sale_order_deal_tracking_ext.py
  python3 -m py_compile /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/models/account_move_deal_tracking_ext.py
  ```

---

## SERVICE STARTUP

- [ ] Start Odoo service
  ```bash
  systemctl start odoo
  ```

- [ ] Wait 10 seconds for startup
  ```bash
  sleep 10
  ```

- [ ] Verify Odoo is running
  ```bash
  systemctl status odoo  # Should show active (running)
  ```

- [ ] Check Odoo logs for errors
  ```bash
  tail -n 50 /var/log/odoo/odoo-server.log
  ```

  Expected output should include:
  ```
  ... commission_ax ... installed
  ... commission_ax ... load instance ... successfully
  ```

  Should NOT include:
  ```
  ERROR
  CRITICAL
  AttributeError
  ImportError
  ```

---

## MODULE UPGRADE

- [ ] Access Odoo web interface: http://139.84.163.11:8069

- [ ] Login as administrator

- [ ] Go to Apps menu (Settings → Apps)

- [ ] Search for "commission_ax"

- [ ] Click on module

- [ ] If "Upgrade" button shows:
  - [ ] Click "Upgrade"
  - [ ] Confirm upgrade

- [ ] Wait for upgrade to complete (2-5 minutes)

- [ ] Verify no errors in dialog

---

## POST-INSTALLATION VERIFICATION

- [ ] Check database consistency:
  ```bash
  # In Odoo interface:
  # Settings → Technical → Database Structure → Integrity Checks
  ```

- [ ] Verify tables were created:
  ```bash
  # Models with deal fields should have these columns:
  psql commission_ax -c "\d sale_order" | grep -E "buyer_name|project_name|unit_sale|commission"
  psql commission_ax -c "\d account_move" | grep -E "buyer_name|project_name|unit_sale|commission"
  ```

- [ ] Check module manifest is correctly registered:
  ```bash
  grep -A5 "'data':" /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/__manifest__.py
  ```

---

## FIELD VERIFICATION

- [ ] Test sale order deal fields:
  1. Go to Sales → Quotations
  2. Open any existing sale order
  3. Verify you see "BROKERAGE DEAL INFORMATION" section
  4. Verify fields display: buyer_name, project_name, unit_sale_value, primary_commission_percentage
  5. Verify deal_summary_html displays HTML with styling

- [ ] Test invoice deal fields:
  1. Go to Accounting → Invoices
  2. Open any invoice created from a sale order
  3. Verify "Brokerage Deal Information" group displays
  4. Verify all deal fields are populated
  5. Verify deal_information_summary shows HTML

---

## TESTING READINESS

- [ ] All installation steps completed
- [ ] Odoo service running without errors
- [ ] Deal fields visible in forms
- [ ] Deal summary HTML rendering properly
- [ ] Ready to proceed to testing phase

---

## ROLLBACK PROCEDURE (If Needed)

If critical errors occur:

1. Stop Odoo:
   ```bash
   systemctl stop odoo
   ```

2. Restore backup files:
   ```bash
   cp -r /var/odoo/scholarixv2/backups/commission_ax_backup_YYYYMMDD/* \
         /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/
   ```

3. Restore database:
   ```bash
   dropdb commission_ax
   createdb commission_ax
   psql commission_ax < /tmp/commission_ax_backup_YYYYMMDD.sql
   ```

4. Start Odoo:
   ```bash
   systemctl start odoo
   ```

5. Document the issue and logs for debugging

---

## SIGN-OFF

| Step | Completed | Date | Notes |
|------|-----------|------|-------|
| Pre-Installation | [ ] | ____ | |
| File Deployment | [ ] | ____ | |
| Configuration | [ ] | ____ | |
| Service Startup | [ ] | ____ | |
| Module Upgrade | [ ] | ____ | |
| Post-Installation | [ ] | ____ | |
| Field Verification | [ ] | ____ | |
| Testing Ready | [ ] | ____ | |

