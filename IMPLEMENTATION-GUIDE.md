# Brokerage Deal Tracking Implementation Guide

## Overview

This enhancement adds consolidated brokerage deal information fields throughout the sales and accounting modules, ensuring complete tracking of buyer name, project, unit sale value, and commission percentage from order creation through invoicing and accounting.

## Components Created

### 1. **Model Extensions**

#### `sale_order_deal_tracking_ext.py`
Extends `sale.order` with computed deal tracking fields:
- `buyer_name` - Computed from `partner_id.name`
- `project_name` - Computed from `project_id.name`
- `unit_sale_value` - Computed from first order line `price_unit`
- `primary_commission_percentage` - Highest commission % among all partners
- `deal_summary_html` - Rich HTML summary for display

**Key Features:**
- All fields are computed and stored for performance
- `_prepare_invoice()` override ensures deal info transfers to invoices
- `action_view_deal_summary()` provides dialog view of deal details

#### `account_move_deal_tracking_ext.py`
Extends `account.move` (invoices) with deal reference fields:
- `buyer_name` - Stored reference to buyer
- `project_name` - Stored reference to project
- `unit_sale_value` - Stored reference to original unit price
- `commission_percentage` - Stored reference to commission %
- `sale_order_deal_reference` - String reference to SO number
- `deal_information_summary` - Computed HTML summary

**Key Features:**
- Automatically populates from sale order when invoice created
- `action_view_sale_order_deal()` links back to originating SO
- `action_open_related_commission_lines()` shows commission breakdown
- Rich HTML summary for accounting review

### 2. **View Enhancements**

#### `sale_order_deal_tracking_views.xml`
- **Form View**: Adds "BROKERAGE DEAL INFORMATION" section with 4-row grid
- **Tree View**: Adds columns for Buyer, Project, Unit Price, Commission %
- **Header Button**: "View Deal Summary" button for quick reference

Layout:
```
┌─────────────────────────────────────────┐
│  BROKERAGE DEAL INFORMATION             │
├──────────────────┬──────────────────────┤
│ Buyer Name       │ Project Name         │
├──────────────────┼──────────────────────┤
│ Unit Sale Value  │ Primary Commission % │
├──────────────────────────────────────────┤
│ Deal Summary HTML (Rich formatted)        │
└──────────────────────────────────────────┘
```

#### `account_move_deal_tracking_views.xml`
- **Form View**: Adds "Brokerage Deal Information" group
  - Sales Order Reference
  - Buyer Name
  - Project Name
  - Unit Sale Value
  - Commission Percentage
  - Deal Information Summary HTML
- **Tree View**: Adds deal columns for quick scanning
- **Kanban View**: NEW - Card view showing deal details

Action Buttons:
- "View Sale Order" - Navigate to originating SO
- "View Commissions" - See all commission lines

### 3. **Mixin (Optional Advanced Feature)**

#### `brokerage_deal_tracking_mixin.py`
AbstractModel providing reusable deal tracking fields for any model.

Usage:
```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['my.model', 'brokerage.deal.tracking.mixin']
```

---

## Installation Steps

### Step 1: Copy Files to Module

```bash
# Copy Python model extensions
cp sale_order_deal_tracking_ext.py /path/to/commission_ax/models/
cp account_move_deal_tracking_ext.py /path/to/commission_ax/models/
cp brokerage_deal_tracking_mixin.py /path/to/commission_ax/models/

# Copy XML views
cp sale_order_deal_tracking_views.xml /path/to/commission_ax/views/
cp account_move_deal_tracking_views.xml /path/to/commission_ax/views/
```

### Step 2: Update Module Manifest

Edit `commission_ax/__manifest__.py`:

```python
{
    # ... existing manifest entries ...
    'data': [
        # ... existing XML files ...
        'views/sale_order_deal_tracking_views.xml',
        'views/account_move_deal_tracking_views.xml',
    ],
    'depends': [
        # ... existing dependencies ...
        'account',  # Ensure account is listed
        'sale',     # Ensure sale is listed
    ],
}
```

### Step 3: Register Models in __init__.py

Edit `commission_ax/models/__init__.py`:

```python
from . import (
    # ... existing imports ...
    sale_order_deal_tracking_ext,
    account_move_deal_tracking_ext,
    brokerage_deal_tracking_mixin,
)
```

### Step 4: Update Existing sale_order.py (if needed)

If the existing `sale_order.py` has methods that conflict, integrate the compute methods directly:

```python
# In existing SaleOrder class, add these compute methods:

@api.depends('partner_id', 'partner_id.name')
def _compute_buyer_name(self):
    for record in self:
        record.buyer_name = record.partner_id.name if record.partner_id else ''

# ... other compute methods ...
```

### Step 5: Database Migration

```bash
# Via Odoo shell:
cd /var/odoo/scholarixv2
python manage.py shell << EOF
from odoo import api, SUPERUSER_ID
env = api.Environment(env.cr, SUPERUSER_ID, {})
env['ir.model.fields'].search([]).mapped('name')
EOF

# Or restart Odoo service:
systemctl restart odoo
```

### Step 6: Update Commission Module

```bash
# In Odoo web interface:
# 1. Go to Settings > Apps
# 2. Search for "commission_ax"
# 3. Click "Upgrade" button
# 4. Refresh page after upgrade completes
```

---

## Field Mapping & Data Flow

```
SALE ORDER
│
├─ partner_id ──→ buyer_name (computed, stored)
├─ project_id ──→ project_name (computed, stored)
├─ order_line[0].price_unit ──→ unit_sale_value (computed, stored)
├─ broker_rate, referrer_rate, ... ──→ primary_commission_percentage (computed, stored)
│
└─ Creates: INVOICE (account.move)
    ├─ buyer_name (transferred, stored)
    ├─ project_name (transferred, stored)
    ├─ unit_sale_value (transferred, stored)
    ├─ commission_percentage (transferred, stored)
    └─ sale_order_deal_reference (transferred, stored)
```

---

## Usage Examples

### For Sales Team

**View Deal Summary:**
1. Open any Sale Order
2. Click "View Deal Summary" button
3. See buyer, project, unit value, commission % in dialog

**Find Orders by Deal Details:**
1. Go to Sales > Orders
2. Tree view now shows Buyer, Project, Unit Price, Commission % columns
3. Use search/filter on these fields

### For Accounting Team

**Review Deal Info on Invoice:**
1. Open an Invoice
2. See "Brokerage Deal Information" section showing:
   - Original buyer name
   - Original project
   - Original unit sale value
   - Commission % charged
3. Click "View Sale Order" to see full deal context
4. Click "View Commissions" to see commission breakdown

**Track Commissions with Invoices:**
1. Go to Accounting > Invoices
2. Use Kanban view to see deal info on cards
3. Filter by buyer, project, or commission % range
4. Export data for brokerage reporting

---

## Performance Considerations

### Computed & Stored Fields
All fields use `store=True` for computed fields:
- **Benefit**: Fast querying, filtering, sorting
- **Cost**: ~500KB per 10,000 records (estimate)
- **Trade-off**: Acceptable for typical brokerage volumes

### Database Indexes
Consider adding indexes for commonly searched fields:
```sql
CREATE INDEX idx_sale_order_buyer_name ON sale_order(buyer_name);
CREATE INDEX idx_sale_order_project_name ON sale_order(project_name);
CREATE INDEX idx_account_move_buyer_name ON account_move(buyer_name);
```

---

## Customization Options

### Add More Deal Tracking Fields

Edit `sale_order_deal_tracking_ext.py` to add:

```python
# Example: Add deal type
deal_type = fields.Selection([
    ('direct', 'Direct Sale'),
    ('brokerage', 'Brokerage'),
    ('referral', 'Referral'),
], string="Deal Type", default='brokerage')

# Example: Add deal value ranges for quick filtering
deal_value_range = fields.Selection([
    ('small', '< $5,000'),
    ('medium', '$5K - $50K'),
    ('large', '$50K - $250K'),
    ('enterprise', '> $250K'),
], string="Deal Size", compute="_compute_deal_value_range", store=True)
```

### Extend to Additional Models

The same pattern can be applied to:
- `purchase.order` (for purchase commissions)
- `project.project` (for project-level commission tracking)
- `commission.line` (already has order/sale order link)

---

## Testing Checklist

- [ ] Create a sale order with buyer, project, unit price, commission %
- [ ] Verify buyer_name, project_name, unit_sale_value, primary_commission_percentage compute
- [ ] Check deal_summary_html displays correctly
- [ ] Generate invoice from sale order
- [ ] Verify deal information transfers to invoice
- [ ] Test "View Sale Order" button from invoice
- [ ] Test "View Commissions" button from invoice
- [ ] Check tree view columns display correctly
- [ ] Test search/filter on deal fields
- [ ] Verify Kanban view shows deal info on cards

---

## Troubleshooting

### Fields not appearing in form/tree
1. Check XML view inherit paths are correct
2. Verify `noupdate="0"` in view XML records
3. Restart Odoo service
4. Clear browser cache (Ctrl+Shift+Delete)
5. Check for XPath errors in logs

### Computed fields empty
1. Verify `@api.depends()` decorators have correct field names
2. Check that source fields exist (partner_id, project_id, order_line)
3. For stored computed fields, try `_recompute_fields()` in Python:
   ```python
   env['sale.order'].search([])._recompute_fields(['buyer_name'])
   ```

### Invoice doesn't get deal information
1. Verify `_prepare_invoice()` override is active
2. Check sale order has deal fields populated
3. Create new invoice from SO (not manual entry)
4. Check Odoo logs for errors during invoice creation

---

## Support & Documentation

- **Models**: See docstrings in Python files
- **Views**: Comments in XML files explain each section
- **Workflow**: See data flow diagram above

---

## Files Modified/Created

```
commission_ax/
├── models/
│   ├── __init__.py (UPDATE - add imports)
│   ├── sale_order_deal_tracking_ext.py (NEW)
│   ├── account_move_deal_tracking_ext.py (NEW)
│   └── brokerage_deal_tracking_mixin.py (NEW)
├── views/
│   ├── sale_order_deal_tracking_views.xml (NEW)
│   └── account_move_deal_tracking_views.xml (NEW)
└── __manifest__.py (UPDATE - add to data)
```

---

## Summary

This enhancement provides brokerage companies with:
- ✅ Unified deal tracking across sales and accounting
- ✅ Automatic capture of buyer, project, unit value, commission %
- ✅ Persistent storage for auditing and reporting
- ✅ Rich UI with deal information displayed prominently
- ✅ Easy navigation between SO and invoices
- ✅ Foundation for advanced brokerage reporting

**Result**: Complete visibility into all brokerage deals from order creation through invoicing and accounting.
