# Invoice Status Tags & Controls Module

## Overview
This Odoo 17 module adds clear visual indicators and controls for invoice status management, providing better visibility into invoicing progress and issues.

## Features

### 📊 **Invoice Type Tags**
Visual badges showing order invoice status:
- **Not Started**: No invoicing yet
- **Partial Invoicing**: Some lines invoiced
- **Fully Invoiced**: All lines invoiced
- **Draft Only**: Has draft invoices only
- **Upsell**: Invoiced more than order value
- **Cancelled**: Only cancelled invoices

### 📈 **Progress Tracking**
- **Invoicing Percentage**: Progress bar showing % of order invoiced
- **Amount Breakdown**: 
  - Total Invoiced (Posted invoices only)
  - Remaining to Invoice
  - Upsell Amount (if applicable)

### ⚠️ **Warnings & Alerts**
- **Draft Invoice Warning**: Red ribbon when draft invoices exist
- **Needs Attention**: Yellow ribbon for invoicing issues:
  - Draft invoices marked as "invoiced"
  - Posted invoices marked as "to invoice"
  - Cancelled invoices not marked as "no"

### 📊 **Invoice Counts**
Quick view of invoice breakdown:
- Posted Invoices count
- Draft Invoices count
- Cancelled Invoices count

### 🔍 **Custom Filters**
Easy filtering in Sales Order list:
- Needs Attention
- Has Draft Invoices
- Partial Invoicing
- Upsell Orders
- Draft Only

### 📱 **Menu Items**
Quick access to:
- Orders Needing Attention
- Partial Invoicing Orders

## Installation

### Method 1: Manual Installation (Development)
1. Copy the `invoice_status_tags` folder to your Odoo addons directory:
   ```bash
   cp -r invoice_status_tags /path/to/odoo/addons/
   ```

2. Restart Odoo server:
   ```bash
   sudo systemctl restart odoo
   ```

3. Update Apps List:
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Invoice Status Tags"
   - Click Install

### Method 2: Via ZIP Upload (Production - CloudPepper)
1. Create ZIP file:
   ```bash
   cd D:/odoo17_backup/odoo-mcp-server
   zip -r invoice_status_tags.zip invoice_status_tags/
   ```

2. Upload to Odoo:
   - Login to https://erposus.com
   - Go to Apps → Upload Module
   - Select `invoice_status_tags.zip`
   - Click Upload and Install

### Method 3: Via Python Script (Automated)
Run the installation script:
```bash
python install_invoice_tags_module.py
```

## Usage

### Form View Enhancements
When viewing a Sales Order, you'll see:

**Header Ribbons:**
- 🔴 **DRAFT INVOICE WARNING** - Order has draft invoices
- 🟡 **NEEDS ATTENTION** - Invoicing issues detected
- 🔵 **UPSELL** - Invoice exceeds order value

**Invoice Progress Section:**
- Invoice Type badge (color-coded)
- Progress bar showing invoicing %
- Breakdown: X Posted | Y Draft | Z Cancelled

**Amount Details:**
- Total Invoiced (Posted): Shows validated invoice amounts
- Remaining to Invoice: Amount still to be invoiced
- Upsell Amount: Extra invoiced amount (if applicable)

### Tree View Columns
New columns available:
- **Invoice Type**: Badge showing status
- **Invoicing Progress**: Progress bar
- **Needs Attention**: Toggle indicator
- **Posted/Draft Counts**: Invoice breakdown
- **Amounts**: Invoiced and remaining

### Filtering
Use built-in filters:
1. **Needs Attention**: Shows critical issues
2. **Has Draft Invoices**: Orders with drafts needing validation
3. **Partial Invoicing**: Track in-progress invoicing
4. **Upsell Orders**: Monitor over-invoicing
5. **Draft Only**: Orders with only draft invoices

### Quick Access Menus
Navigate to:
- **Sales → Orders → Needs Attention**: Critical issues
- **Sales → Orders → Partial Invoicing**: Track progress

## Benefits

### For Sales Team
✅ **Quick Identification**: See invoice status at a glance  
✅ **Progress Tracking**: Monitor invoicing progress  
✅ **Issue Detection**: Spot draft invoices needing validation

### For Finance Team
✅ **Validation Control**: Identify draft invoices quickly  
✅ **Upsell Monitoring**: Track additional revenue  
✅ **Amount Reconciliation**: Clear invoiced vs remaining amounts

### For Management
✅ **Dashboard Ready**: Filter and group by invoice status  
✅ **Issue Prioritization**: "Needs Attention" highlights problems  
✅ **Progress Reporting**: See invoicing completion rates

## Technical Details

### Computed Fields
All fields are computed and stored for performance:
- Updates automatically when invoices change
- No manual intervention needed
- Real-time status updates

### Dependencies
- `sale`: Sales module (base)
- `account`: Accounting module (invoicing)

### Compatibility
- Odoo 17.0
- Community & Enterprise editions
- Tested with CloudPepper hosting

## Troubleshooting

### Module Not Appearing in Apps List
```bash
# Update apps list
# Go to Apps → Update Apps List
# Search again
```

### Fields Not Showing
```bash
# Upgrade module
# Apps → Invoice Status Tags → Upgrade
```

### Need to Recompute Fields
```python
# Run in Odoo shell
self.env['sale.order'].search([])._compute_invoicing_details()
self.env.cr.commit()
```

## Support
For issues or questions:
- GitHub: https://github.com/renbran/odoo-mcp-server
- Email: support@sgctechai.com

## License
LGPL-3

## Author
SGC TECH AI - 2026
