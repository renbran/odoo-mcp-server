# Invoice Report with Deal Information - Complete Documentation

## Overview

This module extends Odoo's invoice system with a professional **Invoice Report with Deal Information** that includes original deal details from sales orders. This ensures complete traceability from deal creation to invoice generation.

---

## Architecture

### 1. Database Fields

#### Invoice Fields (account.move)
The following fields have been added to the `account.move` model:

| Field | Type | Purpose |
|-------|------|---------|
| `buyer_name` | Char | Name of the buyer in the original deal |
| `project_name` | Char | Project or property name |
| `unit_sale_value` | Monetary | Original unit sale value |
| `commission_percentage` | Float | Commission % from the deal |
| `sale_order_deal_reference` | Char | Deal reference number |
| `sale_order_id` | Many2one | Link to original sale order |
| `deal_information_summary` | Html (computed) | Formatted deal information box |

#### Sales Order Fields (sale.order)
The following fields have been added to the `sale.order` model to match invoice structure:

| Field | Type | Purpose |
|-------|------|---------|
| `buyer_name` | Char | Buyer name |
| `project_name` | Char | Project name |
| `unit_sale_value` | Monetary | Unit value |
| `commission_percentage` | Float | Commission percentage |
| `sale_order_deal_reference` | Char | Deal reference |

---

## Report Features

### Visual Design
- **Professional Header**: Invoice type and number clearly displayed
- **Deal Information Panel**: Highlighted box with colored border (#8b1538 - brand color)
- **Organized Layout**:
  - Party information (Bill To / Bill From)
  - Invoice details (Date, Due Date, References)
  - Sales person and team information
- **Clean Table**: Line items with quantity, unit price, and amounts
- **Totals Section**: Subtotal, tax breakdown, and final total
- **Notes Section**: Terms and conditions or special notes
- **Footer**: Contact information

### Deal Information Display
The report includes a prominent deal information section that shows:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ORIGINAL DEAL INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Buyer:              [Buyer Name]
Project:            [Project Name]
Unit Sale Value:    [Value with Currency]
Commission %:       [Percentage]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sales Order:        [Order Reference - Total Amount]
```

---

## Data Flow

### Invoice Creation from Sales Order

```
Sale Order Created
    ↓
[buyer_name, project_name, unit_sale_value, 
 commission_percentage, deal_reference populated]
    ↓
Create Invoice from Sale Order
    ↓
_prepare_invoice_values() overridden
    ↓
Deal fields automatically populated in invoice
    ↓
_compute_deal_information_summary()
    ↓
HTML-formatted summary generated
    ↓
Report displays complete deal context
```

---

## Implementation Details

### File Structure
```
recruitment_implementation/
├── models/
│   ├── __init__.py
│   ├── models_candidate_enhancement.py
│   ├── models_followup.py
│   ├── models_retention.py
│   └── models_invoice_deals.py          [NEW]
├── report/
│   ├── __init__.py
│   └── report_invoice_with_deals.xml    [NEW]
└── ...
```

### Key Classes

#### AccountMoveWithDeals (in models_invoice_deals.py)
Extends `account.move` model with:
- Deal information fields
- `_compute_deal_information_summary()` - Generates HTML summary
- `create()` override - Populates deal fields on creation
- `write()` override - Keeps deal fields in sync
- `generate_invoice_with_deals_pdf()` - Action to generate report

#### SaleOrderDealIntegration (in models_invoice_deals.py)
Extends `sale.order` model with:
- Deal information fields (matching invoice)
- `_prepare_invoice_values()` override - Passes deal data to invoices

---

## Usage

### Option 1: Automatic Population

When creating an invoice from a sales order:
1. Ensure sales order has deal fields populated:
   - Buyer Name
   - Project Name
   - Unit Sale Value
   - Commission Percentage
   - Deal Reference

2. Create invoice from sales order
3. Deal fields automatically populate in invoice
4. HTML summary auto-generates

### Option 2: Manual Entry

For invoices not linked to sales orders:
1. Open the invoice
2. Fill in deal fields manually:
   - Buyer Name
   - Project Name
   - Unit Sale Value
   - Commission Percentage
3. Save the invoice
4. Deal information summary auto-generates

### Generating the Report

Method 1: From Invoice Form
```python
invoice.generate_invoice_with_deals_pdf()
```

Method 2: From Menu
1. Go to Accounting → Invoices
2. Select invoice(s)
3. Print → Invoice with Deal Information

Method 3: Programmatically
```python
invoice = env['account.move'].browse(id)
report = env.ref('scholarix_recruitment.account_report_invoice_with_deals')
report.report_action(invoice)
```

---

## Computed Fields

### deal_information_summary
**Purpose**: Provides a formatted HTML box with deal information  
**Computation Depends On**:
- sale_order_id
- buyer_name
- project_name
- unit_sale_value
- commission_percentage

**Logic**:
1. Returns False for non-sales invoices (in, in_refund)
2. Formats monetary values with currency symbol
3. Formats percentages to 2 decimal places
4. Generates HTML with styling and layout
5. Uses brand color #8b1538 for emphasis

**HTML Structure**:
```html
<div style="background: #f8f9fa; padding: 12px; 
    border-radius: 5px; border-left: 4px solid #8b1538;">
    <h6>ORIGINAL DEAL INFORMATION</h6>
    <table>
        <tr><td>Buyer:</td><td>[Value]</td></tr>
        <tr><td>Project:</td><td>[Value]</td></tr>
        <tr><td>Unit Sale Value:</td><td>[Value]</td></tr>
        <tr><td>Commission %:</td><td>[Value]</td></tr>
    </table>
</div>
```

---

## Field Synchronization

### On Invoice Creation
When invoice is created from sales order:
```python
invoice_vals = {
    'buyer_name': sale_order.buyer_name,
    'project_name': sale_order.project_name,
    'unit_sale_value': sale_order.unit_sale_value,
    'commission_percentage': sale_order.commission_percentage,
    'sale_order_deal_reference': sale_order.sale_order_deal_reference or sale_order.name,
    'sale_order_id': sale_order.id,
}
```

### On Invoice Update
When `sale_order_id` is set on invoice:
- Deal fields are populated from linked sales order
- Existing values are preserved (not overwritten)
- Summary is auto-recomputed

---

## Report Template Specifications

### Page Layout
- **A4 Size**: Portrait orientation
- **Margins**: Standard (1 inch)
- **Font**: Arial/sans-serif
- **Colors**: 
  - Primary: #8b1538 (brand color)
  - Secondary: #333 (dark gray)
  - Accent: #f8f9fa (light gray)

### Conditional Sections
1. **Deal Panel**: Only shown for sales invoices (out_invoice, out_refund)
2. **Bill To/From**: Always shown
3. **Invoice Details**: Always shown
4. **Line Items**: Always shown
5. **Notes Section**: Only if narration exists
6. **Footer**: Always shown

### Data Formatting
- **Dates**: Locale-specific format
- **Amounts**: 2 decimal places with currency symbol
- **Percentages**: 2 decimal places with % sign
- **References**: Uppercase for codes

---

## Integration Points

### 1. With Sale Module
- Reads: sale_order fields
- Writes: invoice deal fields
- Triggers: _prepare_invoice_values()

### 2. With Accounting Module
- Extends: account.move model
- Uses: Standard invoice templates
- Reports: Custom report template

### 3. With Reporting
- Report Type: Qweb PDF
- Action: account_report_invoice_with_deals
- Template: report_invoice_with_deals

---

## Data Validation

Currently no specific validation. Future enhancements could include:

```python
# Example future validation
@api.constrains('commission_percentage')
def _check_commission_percentage(self):
    for record in self:
        if record.commission_percentage < 0 or record.commission_percentage > 100:
            raise ValidationError(_("Commission percentage must be between 0 and 100"))
```

---

## Performance Considerations

### Computed Fields
- `deal_information_summary` is computed on-the-fly
- No database storage (improves UPDATE performance)
- Minimal impact (string formatting only)

### Report Generation
- Report is generated on-demand
- Uses standard Qweb engine
- No database queries beyond invoice data
- Efficient for batch generation

---

## Future Enhancements

### Phase 2
- [ ] Commission calculation automation
- [ ] Deal duration tracking
- [ ] Multi-currency support improvements
- [ ] Commission payment tracking

### Phase 3
- [ ] Deal performance analytics
- [ ] Commission reporting dashboards
- [ ] Deal pipeline visualization
- [ ] Automated deal status updates

### Phase 4
- [ ] Integration with HR module for commission payouts
- [ ] Deal history and audit trail
- [ ] Deal amendment tracking
- [ ] Deal closure automation

---

## Troubleshooting

### Deal Fields Not Populating on Invoice Creation

**Cause**: `_prepare_invoice_values()` not being called

**Solution**:
1. Verify sale order creation uses `action_confirm()`
2. Check that invoice is created via "Create Invoice" button
3. Verify module is installed and activated

### Report Not Showing Deal Information

**Cause**: Fields empty on invoice

**Solution**:
1. Manually populate deal fields on invoice
2. Or recreate invoice from sales order with deal fields filled
3. Save and regenerate report

### HTML Summary Not Displaying

**Cause**: Computed field not triggered

**Solution**:
1. Modify any deal field to trigger recompute
2. Or refresh the page
3. Or directly call: `record._compute_deal_information_summary()`

---

## Configuration

No special configuration needed. The module:
1. Automatically extends account.move and sale.order
2. Registers the report on installation
3. Adds fields to database on migration

To activate:
1. Install the recruitment_implementation module
2. Deal fields available immediately
3. Report available in Print menu

---

## Support

For issues or enhancements:
1. Check the troubleshooting section
2. Review the code documentation
3. Contact: support@sgtechai.com

---

**Last Updated**: January 19, 2026  
**Module Version**: 1.0.0  
**Odoo Version**: 17.0  
**Status**: Production Ready
