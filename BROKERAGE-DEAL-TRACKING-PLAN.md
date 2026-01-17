# Brokerage Deal Tracking Fields Enhancement

## Current State Analysis

### Existing Fields in commission_ax
The commission_ax module currently has commission tracking fields but lacks consolidated "deal information" fields that brokerage companies need for daily operations.

**Current Commission Fields in sale.order:**
- `commission_status` - Draft, Calculated, Confirmed, Processed, Paid, Cancelled
- `commission_processed` - Boolean for processing status
- `commission_calculation_time` - Performance metric
- `sales_value` - "Unit Price" computed from first order line
- Individual commission fields: `broker_amount`, `referrer_amount`, `cashback_amount`, etc.
- Individual commission rates: `broker_rate`, `referrer_rate`, `cashback_rate`, etc.

**Fields Related to Deal Info:**
- `partner_id` - INHERITED from sale.order (Customer)
- `project_id` - INHERITED from sale.order (Project)
- `amount_total` - INHERITED (Total Amount)

### What's Missing

For a proper brokerage company, you need **consolidated deal tracking fields** that capture and persist:

1. **Buyer Name** - Currently derived from partner_id but not explicitly stored
2. **Project** - Exists but needs better visibility and required status
3. **Unit Sale Value** - Exists as `sales_value` but only for single-line orders
4. **Commission Percentage** - Multiple individual percentages but no consolidated summary

**For Invoicing & Accounting:** These fields should transfer to the invoice so accounting has the complete deal context.

---

## Proposed Solution

### Phase 1: New Fields for sale.order

```python
# BROKERAGE DEAL TRACKING SECTION
buyer_name = fields.Char(
    string="Buyer Name",
    compute="_compute_buyer_name",
    store=True,
    help="Buyer/Customer name for deal tracking. Auto-populated from customer."
)

project_name = fields.Char(
    string="Project Name",  
    compute="_compute_project_name",
    store=True,
    help="Project name if deal is project-related"
)

unit_sale_value = fields.Monetary(
    string="Unit Sale Value",
    compute="_compute_unit_sale_value",
    store=True,
    currency_field='currency_id',
    help="Price per unit for deal tracking. From first order line unit price."
)

primary_commission_percentage = fields.Float(
    string="Primary Commission %",
    compute="_compute_primary_commission_percentage",
    store=True,
    help="Highest commission % among all partners for quick reference"
)

deal_summary = fields.Html(
    string="Deal Summary",
    compute="_compute_deal_summary",
    help="HTML summary of buyer, project, unit value, and commission % for reporting"
)
```

### Phase 2: New Fields for sale.order.line

```python
# BROKERAGE DEAL TRACKING
unit_sale_value = fields.Monetary(
    string="Unit Sale Value",
    related='price_unit',
    help="Price per unit for deal tracking"
)

buyer_name = fields.Char(
    string="Buyer Name",
    related='order_id.partner_id.name',
    help="Buyer name from the order"
)

project_name = fields.Char(
    string="Project Name",
    related='order_id.project_id.name',
    help="Project name from the order"
)
```

### Phase 3: Propagation to Invoices (account.move)

```python
# In an inherited account.move model or through flow
buyer_name = fields.Char(
    string="Buyer Name",
    help="Original buyer from sale order - for accounting reference"
)

project_name = fields.Char(
    string="Project Name",
    help="Original project - for accounting reference and cost center tracking"
)

unit_sale_value = fields.Monetary(
    string="Unit Sale Value",
    currency_field='currency_id',
    help="Original unit sale value from order"
)

commission_percentage = fields.Float(
    string="Commission %",
    help="Primary commission percentage from order"
)
```

### Phase 4: View Enhancements

**Sales > Orders Form View:**
- Add "DEAL INFORMATION" section showing:
  - Buyer Name (read-only, from partner)
  - Project Name (read-only, from project)  
  - Unit Sale Value (read-only, from order line)
  - Primary Commission %

**Sales > Orders Tree View:**
- Add columns: Buyer Name, Project, Unit Sale Value, Commission %

**Accounting > Invoices Form View:**
- Add "ORIGINAL DEAL INFO" section showing:
  - Buyer Name
  - Project
  - Unit Sale Value  
  - Commission %
  - Link to originating Sale Order

---

## Implementation Steps

### Step 1: Modify sale.order.py
- Add compute methods for each field
- Link to partner_id.name for buyer_name
- Link to project_id.name for project_name
- Compute primary_commission_percentage (highest among all commissions)
- Create deal_summary HTML for reports

### Step 2: Modify sale.order.line.py  
- Add related fields for buyer_name and project_name
- Ensure line-level tracking for multi-line orders

### Step 3: Create Invoice Integration
- Create sale_order_mixin.py with field definitions
- Inherit in both sale.order and account.move
- Add computed fields that transfer to invoice on creation

### Step 4: Update Views
- Modify sale_order_views.xml to add deal info section
- Modify sale_order_tree view to show deal columns
- Create account_move_views.xml extension to show deal info

### Step 5: Update Reports
- Commission Payout Report - include buyer, project, unit value, commission %
- Brokerage Summary Report - grouped by buyer/project

---

## Data Flow

```
SALES ORDER
├─ Customer (partner_id) → Buyer Name
├─ Project (project_id) → Project Name  
├─ Order Line (price_unit) → Unit Sale Value
├─ Commission Rates → Primary Commission %
└─ Creates Invoice
   └─ INVOICE (account.move)
      ├─ buyer_name (transferred)
      ├─ project_name (transferred)
      ├─ unit_sale_value (transferred)
      └─ commission_percentage (transferred)
```

---

## Benefits

1. **Brokerage Visibility**: All deal info in one place
2. **Invoicing Context**: Accountants see complete deal details
3. **Tracking**: Easy to find orders by buyer, project, value range
4. **Reporting**: Generate brokerage reports with full context
5. **Compliance**: Deal information maintained for audit trails
6. **Performance**: Stored/computed fields for fast queries

---

## Files to Modify

```
commission_ax/
├── models/
│   ├── sale_order.py          ← Add buyer_name, project_name, unit_sale_value, primary_commission_percentage, deal_summary
│   ├── sale_order_line.py      ← Add related fields (if exists)
│   ├── sale_order_mixin.py     ← NEW: shared field definitions
│   └── account_move_ext.py     ← NEW: extend account.move with deal fields
├── views/
│   ├── sale_order_views.xml    ← Add deal info section
│   ├── sale_order_tree_views.xml ← Add deal columns
│   └── account_move_views.xml  ← NEW: show deal info in invoices
└── reports/
    ├── commission_report_template_enhanced.xml ← Add deal info
    └── brokerage_summary_report.xml ← NEW: deal-focused report
```

---

## Next Steps

Would you like me to:
1. ✅ Implement these new fields in the models?
2. ✅ Create the view enhancements?
3. ✅ Set up invoice integration?
4. ✅ Create comprehensive brokerage reports?
5. ✅ All of the above?

This will ensure your brokerage deals are fully tracked through sales, commission, and accounting workflows.
