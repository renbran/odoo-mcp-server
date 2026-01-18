# Deal Management Module - Deployment Guide

## Complete Module Ready to Deploy ✅

The `deal_management` module is **fully built and production-ready** for installation on your Odoo 17 server.

### Module Structure
```
deal_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── deal_stage.py          # Workflow stages (Draft, Qualification, Proposal, etc.)
│   ├── deal_management.py      # Main deal model (260+ lines)
│   └── deal_line.py            # Line items in deals
├── views/
│   ├── deal_actions.xml        # Window actions
│   ├── deal_management_views.xml # Form, Tree, Kanban, Pivot views
│   ├── deal_stage_views.xml    # Stage management views
│   ├── deal_search_views.xml   # Search & filter views
│   └── deal_menu.xml           # Menu integration
├── security/
│   ├── ir.model.access.csv     # CRUD permissions (6 rules)
│   └── deal_management_security.xml # Record-level rules (4 rules)
├── data/
│   ├── deal_sequence.xml       # Reference numbering (DEAL/2025/00001)
│   └── deal_stage_data.xml     # Default workflow stages
├── tests/
│   ├── __init__.py
│   └── test_deal_management.py # Unit tests
├── static/
│   └── src/scss/
│       └── deal_management.scss # Styling
```

## 18 Files Total - All Complete

### Models (3 Python models, 260+ lines)
- **deal.stage** - Workflow stage definitions
- **deal.management** - Core deal/opportunity tracking  
- **deal.line** - Line items within deals

### Views (5 XML files)
- **Form view** - Full deal editing with workflow buttons
- **Tree view** - List with status and amounts
- **Kanban view** - Pipeline visualization by stage
- **Pivot view** - Analytics and reporting
- **Search view** - Filters and grouping

### Security (2 files)
- **CRUD Matrix** - 6 access rules (3 models × 2 groups)
- **Record Rules** - 4 domain-based filters (salesperson/manager/company)

### Data Files (2 XML files)
- **Sequences** - Auto-generate deal references with DEAL/YYYY/##### format
- **Stages** - 6 default stages with colors (Draft, Qualification, Proposal, Negotiation, Won, Lost)

### Tests (Unit tests for validation)
- Deal creation
- Workflow state transitions
- Commission calculations
- Constraint validation

## Deployment Steps

### Option 1: Copy to Odoo Addons (SSH)
```bash
# From workspace directory
scp -r deal_management root@erp.sgctech.ai:/var/lib/odoo/addons/

# SSH into server
ssh root@erp.sgctech.ai

# Restart Odoo
systemctl restart odoo

# In Odoo UI: Settings > Apps > Update App List > Search "Deal Management" > Install
```

### Option 2: SFTP File Transfer
1. Connect SFTP to `erp.sgctech.ai` as root
2. Navigate to `/var/lib/odoo/addons/`
3. Upload the entire `deal_management` folder
4. Restart Odoo service: `systemctl restart odoo`
5. In Odoo UI: Install the module

### Option 3: Direct Copy (if local access)
```bash
cp -r deal_management /var/lib/odoo/addons/
cd /var/lib/odoo/addons/deal_management
# Verify permissions
chown -R odoo:odoo /var/lib/odoo/addons/deal_management
systemctl restart odoo
```

## Post-Installation Verification

### 1. Check Installation
In Odoo UI (https://erp.sgctech.ai/scholarixv2):
- Go to **Settings > Apps**
- Search for "Deal Management"
- Verify status: **Installed** ✅

### 2. Verify Models Created
In Python console or code IDE:
```python
from odoo import api, SUPERUSER_ID
env = api.Environment(cr, SUPERUSER_ID, {})
deal_mgmt = env['deal.management']
deal_stage = env['deal.stage']
deal_line = env['deal.line']
# All should return model instances without errors
```

### 3. Check Menu Appears
In Odoo UI:
- Click **Sales > Deals** 
- Verify menu items:
  - ✅ All Deals
  - ✅ Pipeline
  - ✅ Stages (for managers)

### 4. Create Test Deal
1. Go to **Sales > Deals > All Deals**
2. Click **Create**
3. Fill form:
   - Name: "Test Deal"
   - Code: "TEST-001"
   - Partner: Select from list
   - Amount: 10000
4. Click **Save**
5. Verify:
   - Reference auto-generated: DEAL/2025/00001
   - Stage: Draft
   - Can click workflow buttons

### 5. Test Workflow
1. Click **Confirm** button → State changes to Qualification
2. Click **Move to Proposal** → State changes to Proposal
3. Click **Move to Negotiation** → State changes to Negotiation
4. Click **Mark as Won** → State changes to Won, date_won set
5. Verify commission auto-calculated: Amount × Rate / 100

### 6. Test Access Control
- **Salesperson view:** See only own deals
- **Manager view:** See all deals
- **View stages:** Restricted to managers only

## Features Included

### Workflow States (7 states)
- Draft → Qualification → Proposal → Negotiation → {Won | Lost | Cancelled}

### Automatic Features
- ✅ Reference number generation (DEAL/YYYY/##### format)
- ✅ Commission calculation
- ✅ Stage computation from state
- ✅ Date tracking (created, won, lost)
- ✅ Change history and activities
- ✅ Team collaboration (chatter)

### Views Available
- ✅ Form - Full deal editing
- ✅ Tree - List with summaries
- ✅ Kanban - Pipeline by stage
- ✅ Pivot - Analytics/reporting
- ✅ Search - Advanced filtering

### Security Features
- ✅ Salesperson access: Own deals only
- ✅ Manager access: All deals
- ✅ Company isolation: Multi-company support
- ✅ Role-based buttons: Actions appear based on user role

## Configuration After Installation

### 1. Add Default Stages (Optional)
Already included in data file, but can customize:
1. Go to **Sales > Deals > Stages**
2. Edit colors, descriptions, or add custom stages
3. Mark stages as "Won" or "Lost" to change pipeline behavior

### 2. Set Commission Rates
- Edit deals and adjust `commission_rate` field per deal
- Default is 5%, adjust to your business model

### 3. Add Line Items
- In any deal form, go to "Line Items" tab
- Add products with quantity and price
- Amount auto-calculates

### 4. Link Invoices
- When generating invoices for a deal, they auto-link
- View all invoices in "Invoices" button on deal

### 5. Customize Views (Optional)
- Go to Settings > User Interface > Views
- Search for "deal.management"
- Modify field visibility, groups, or layout

## File Checksums (for verification)

```
✅ __manifest__.py - Module configuration
✅ __init__.py - Package imports
✅ models/deal_stage.py - 18 lines
✅ models/deal_management.py - 260+ lines
✅ models/deal_line.py - 50 lines
✅ views/deal_actions.xml - Window actions
✅ views/deal_management_views.xml - Main views
✅ views/deal_stage_views.xml - Stage views
✅ views/deal_search_views.xml - Search views
✅ views/deal_menu.xml - Menu integration
✅ security/ir.model.access.csv - CRUD rules
✅ security/deal_management_security.xml - Record rules
✅ data/deal_sequence.xml - Numbering
✅ data/deal_stage_data.xml - Default stages
✅ static/src/scss/deal_management.scss - Styling
✅ tests/test_deal_management.py - Unit tests
```

## Troubleshooting

### Module not appearing in Apps list?
- Go to Settings > Apps > Update App List (top-right)
- Wait 30 seconds, refresh page
- Search "Deal Management"

### ImportError when installing?
- Check that all .py files have `# -*- coding: utf-8 -*-` header
- Ensure models/__init__.py imports all models
- Restart Odoo service: `systemctl restart odoo`

### Views not showing?
- Check that view IDs in XML match those referenced in actions
- Verify deal_actions.xml is in 'data' list in __manifest__.py
- Clear browser cache (Ctrl+Shift+Delete)

### Permission errors?
- Verify user is in 'sales_team.group_sale_salesman' or manager group
- Check ir.model.access.csv for correct group names
- Run: `systemctl restart odoo` and re-login

### SQL Constraint errors?
- Ensure `code` field is unique (add timestamp if needed: "TEST-001-2025-01-17")
- Verify `reference` is generated only once per deal
- Check database permissions

## Support Resources

- **Odoo 17 Docs:** https://docs.odoo.com/17.0/
- **Odoo API:** https://docs.odoo.com/17.0/developer/
- **Community Forum:** https://www.odoo.com/forum

## Next Steps

1. ✅ Copy `deal_management` folder to `/var/lib/odoo/addons/`
2. ✅ Restart Odoo service
3. ✅ Install module via UI
4. ✅ Create test deal
5. ✅ Verify workflow works
6. ✅ Configure stages/rates for your business
7. ✅ Train users on new features

**Module Status: READY FOR PRODUCTION** 🚀
