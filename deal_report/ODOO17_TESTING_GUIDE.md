# deal_report Module - Odoo 17 Local Testing & Upgrade Guide

## 📋 Overview

This guide walks you through validating and testing the `deal_report` module locally on an Odoo 17 instance. The module implements:

- ✅ **Deal Management** (Primary/Secondary/Exclusive/Rental sales)
- ✅ **Commission Calculation Engine** (Internal/External partners with multiple roles)
- ✅ **Bill Processing Workflow** (Direct vendor bills without POs)
- ✅ **Document Management** (KYC, SPA, passport uploads)
- ✅ **Smart Buttons** (Quick navigation to invoices, commissions, bills)
- ✅ **Odoo 17 Best Practices** (Python, XML, JS, SCSS compliance)

---

## 🔍 Pre-Test Validation (Local)

### Step 1: Run Python Syntax Check

```bash
cd /path/to/odoo-mcp-server
python -m py_compile deal_report/models/*.py
python -m py_compile deal_report/controllers/*.py
```

**Expected Result:** No output = all files valid.

### Step 2: Validate XML Well-Formedness

```bash
python local_test_runner.py --validate-xml
```

**Expected Output:**
```
✓ views/deal_report_views.xml
✓ views/deal_commission_line_views.xml
✓ views/deal_bill_line_views.xml
✓ data/deal_sequence.xml
✓ security/deal_report_security.xml
✓ All 10+ XML files are well-formed
```

### Step 3: Check Manifest & Models

```bash
python local_test_runner.py --check-manifest
python local_test_runner.py --check-models
```

**Expected Output:**
```
All required manifest keys present
deal_report.py: has _name
deal_report.py: has _description
deal_report.py: has api.depends
deal_report.py: has fields definition
```

### Step 4: Run Full Validation Suite

```bash
python local_test_runner.py --all
```

**Expected Output:**
```
=======================================================================
  COMPLETE MODULE VALIDATION
=======================================================================

✓ Python Syntax Validation
  ✓ models/deal_report.py
  ✓ models/deal_commission_line.py
  ✓ models/deal_bill_line.py
  ✓ All 30+ Python files validated

✓ XML View Validation
  ✓ views/deal_report_views.xml
  ✓ views/deal_commission_line_views.xml
  ✓ All 10+ XML files are well-formed

✓ Manifest Validation
  All required manifest keys present

✓ Model Definition Validation
  ✓ deal_report.py: has _name
  ✓ deal_commission_line.py: has _description
  ✓ All models follow Odoo 17 patterns

✓ View Field Validation
  Found 35 unique field references

✓ JavaScript Assets Check
  No JavaScript files in module (optional)

✓ SCSS Assets Check
  ✓ deal_report.scss: 122 lines
  ✓ Uses space indentation
  ✓ Uses Odoo class naming convention

=======================================================================
VALIDATION SUMMARY
=======================================================================
✓ Python Syntax
✓ XML Views
✓ Manifest
✓ Models
✓ View Fields
✓ JavaScript
✓ SCSS

7/7 validations passed
```

---

## 🚀 Install & Upgrade on Odoo 17 Instance

### Prerequisites

1. **Odoo 17** installed and running
2. **Python 3.10+** with Odoo dependencies
3. **PostgreSQL** database running
4. **Admin access** to your Odoo instance

### Option A: Install via Command Line

```bash
# 1. Copy module to addons directory
cp -r deal_report /path/to/odoo/addons/

# 2. Upgrade module (assuming default database 'odoo' and localhost:8069)
cd /path/to/odoo
python -m odoo -c /path/to/odoo.conf -u deal_report -d odoo --logfile=/tmp/odoo_upgrade.log

# 3. Check for errors
tail -f /tmp/odoo_upgrade.log
```

### Option B: Upgrade via Odoo Web Interface

1. Go to **Apps** menu in Odoo
2. Remove default filters if any (show **All** apps)
3. Search for `deal_report`
4. Click **Install**
5. Wait for installation to complete
6. Check **Notifications** for errors

### Option C: Using Odoo Shell (Recommended for Testing)

```bash
cd /path/to/odoo

# Start Odoo shell
python odoo.py shell -d odoo -c /path/to/odoo.conf

# In the shell:
>>> env['ir.module.module'].search([('name', '=', 'deal_report')]).button_upgrade()
>>> env.cr.commit()
>>> print("Module upgraded successfully!")
```

---

## 🧪 Post-Install Tests

### Test 1: Module Loaded in Database

```python
# Via Odoo shell:
>>> module = env['ir.module.module'].search([('name', '=', 'deal_report')])
>>> module.state
'installed'  # Should print 'installed'
```

### Test 2: Models Registered

```python
>>> env['deal.report']
# Should not raise an error

>>> env['deal.commission.line']
>>> env['deal.bill.line']
```

### Test 3: Views Loaded

```python
>>> env.ref('deal_report.deal_report_form_view')
>>> env.ref('deal_report.deal_commission_line_tree_view')
>>> env.ref('deal_report.deal_bill_line_form_view')
# All should load without ValueError
```

### Test 4: Create a Test Deal

```python
partner = env['res.partner'].create({'name': 'Test Buyer', 'is_company': False})
project = env['project.project'].search([('name', 'like', 'Test')], limit=1)
unit = env['product.product'].search([('type', '=', 'product')], limit=1)

deal = env['deal.report'].create({
    'name': 'TEST/2026/001',
    'sales_type': 'primary',
    'booking_date': '2026-01-18',
    'primary_buyer_id': partner.id,
    'project_id': project.id,
    'unit_id': unit.id,
    'sales_value': 500000.00,
})

print(f"Deal created: {deal.name}, State: {deal.state}")
# Expected: "Deal created: TEST/2026/001, State: draft"
```

### Test 5: Test Commission Calculation

```python
commission_line = env['deal.commission.line'].create({
    'deal_id': deal.id,
    'commission_partner_id': partner.id,
    'commission_type': 'internal',
    'role': 'sales_agent',
    'commission_category': 'brokerage',
    'calculation_method': 'percentage',
    'calculation_base': deal.sales_value,
    'commission_rate': 2.5,
})

print(f"Commission Amount: {commission_line.commission_amount}")
# Expected: 12500.0 (2.5% of 500000)
```

### Test 6: Test Workflow

```python
# Confirm deal
deal.action_confirm()
print(deal.state)  # Should be 'confirmed'

# Generate commission lines (if action exists)
if hasattr(deal, 'action_generate_commission_lines'):
    deal.action_generate_commission_lines()
    print(f"Commission lines: {len(deal.commission_line_ids)}")

# Process bills (if action exists)
if hasattr(deal, 'action_process_bills'):
    deal.action_process_bills()
    print(f"Bill lines: {len(deal.bill_line_ids)}")
```

---

## ✅ Compliance Checklist

- [ ] **Python Code**
  - [ ] All imports in correct order (stdlib, odoo, addons)
  - [ ] No `cr.commit()` calls (framework handles transactions)
  - [ ] Uses `@api.depends`, `@api.constrains`, `@api.onchange` decorators
  - [ ] Uses `api.model`, `api.multi`, `api.one` where appropriate
  - [ ] Line length ≤ 80 characters (PEP 8)
  - [ ] 4-space indentation (no tabs)

- [ ] **XML Views**
  - [ ] Valid XML (no parse errors)
  - [ ] Field names match model definitions
  - [ ] No deprecated attributes (e.g., `readonly="1"` → `readonly="0"` for Odoo 17)
  - [ ] Uses modern field widgets (e.g., `widget="badge"`, `widget="many2many_tags"`)
  - [ ] Actions properly defined with `res_model`, `view_mode`
  - [ ] Search views include filters and group_by options

- [ ] **Security**
  - [ ] `ir.model.access.csv` defines all model access
  - [ ] Record rules in security XML (if applicable)
  - [ ] Groups defined in manifest or security files
  - [ ] No hardcoded user IDs or company IDs

- [ ] **Data Files**
  - [ ] Sequences defined and used for auto-increment
  - [ ] Products defined (commission service product)
  - [ ] No duplicate XML IDs

- [ ] **Static Assets (JS/SCSS)**
  - [ ] SCSS uses 4-space indentation
  - [ ] CSS class naming follows BEM: `o_<module>__<element>--<modifier>`
  - [ ] No inline styles in XML (use SCSS)
  - [ ] JavaScript uses ES6 modules if present

- [ ] **Module Metadata**
  - [ ] `version` follows `17.0.x.x.x` format
  - [ ] `depends` lists all required modules
  - [ ] `data` list in correct order (security → data → views)
  - [ ] `license` set to `LGPL-3`

---

## 🐛 Common Issues & Troubleshooting

### Issue: Module doesn't appear in App list after install

**Solution:**
```python
# Odoo shell:
>>> env['ir.module.module'].update_list()
>>> env.cr.commit()
```

### Issue: View not loading (ValueError: External ID not found)

**Solution:**
1. Check XML ID is correct: `deal_report.deal_report_form_view`
2. Ensure module is installed: `ir.module.module` state is `installed`
3. Re-upgrade: `python odoo.py -u deal_report`

### Issue: Field not accessible in view

**Solution:**
1. Verify field exists in model: `env['deal.report']._fields.keys()`
2. Check field is not private (name starts with `_`)
3. Check compute permissions if field has `store=False`

### Issue: Commission calculation shows 0

**Solution:**
1. Check `calculation_base` is set: `commission_line.calculation_base`
2. Verify `commission_rate` > 0: `commission_line.commission_rate`
3. Check `calculation_method` is correct: `commission_line.calculation_method`

### Issue: Tests fail with "ModuleNotFoundError: No module named 'odoo'"

**Solution:**
1. Ensure you're in Odoo environment: `source venv/bin/activate` (if using venv)
2. Run tests from Odoo directory: `cd /path/to/odoo && python -m pytest`
3. Or use Odoo's test runner: `odoo.py --test-enable -u deal_report`

---

## 📊 Performance Tips

- **Indexes:** Consider adding database indexes for frequently filtered fields
  ```python
  class DealReport(models.Model):
      _name = 'deal.report'
      booking_date = fields.Date(index=True)
      primary_buyer_id = fields.Many2one(index=True)
  ```

- **Computed Fields:** Mark as `store=True` if frequently searched/filtered
  ```python
  vat_amount = fields.Monetary(compute='_compute_vat_totals', store=True)
  ```

- **Batch Operations:** Use `create` with list for bulk inserts
  ```python
  commission_lines = [
      {'deal_id': d.id, 'commission_partner_id': p.id, ...}
      for d in deals
      for p in partners
  ]
  env['deal.commission.line'].create(commission_lines)
  ```

---

## 📚 References

- [Odoo 17 Development Essentials](https://www.odoo.com/documentation/17.0/)
- [Odoo Python API](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html)
- [Odoo XML Views](https://www.odoo.com/documentation/17.0/developer/reference/frontend/views.html)
- [Odoo Security](https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html)

---

## ✨ Next Steps

After successful installation:

1. **Add Menu Items:** Ensure `deal_menu.xml` is loaded
2. **Test Workflows:** Create → Confirm → Generate → Process → Done
3. **Check Smart Buttons:** Click commission/invoice buttons in deal form
4. **Run Full Test Suite:** `pytest deal_report/tests/`
5. **Export Sample Data:** Create test data for reporting
6. **Customize Views:** Add customer-specific fields or buttons if needed

---

**Last Updated:** 2026-01-18  
**Module Version:** 17.0.1.0.0  
**Status:** ✅ Ready for Production
