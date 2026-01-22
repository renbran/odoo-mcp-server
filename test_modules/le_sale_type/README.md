# Sale Order Type with Invoice Integration

## Overview

This module provides comprehensive Sale Order Type management with seamless invoice integration for Odoo 17. It enables businesses to categorize sales orders with custom types and automatically propagates this information to generated invoices.

## Version Information

- **Current Version**: 1.1.0
- **Odoo Version**: 17.0
- **Author**: Luna ERP Solutions
- **License**: LGPL-3

## Features

### Core Features (Version 1.0)

1. **Sale Order Type Management**
   - Define custom sale order types (e.g., Retail, Wholesale, Export, Internal)
   - Assign unique sequences to each type
   - Automatic order numbering based on selected type
   - Active/inactive type management

2. **Sale Order Integration**
   - Sale Type field on sale orders
   - Auto-generated order numbers using type-specific sequences
   - Validation to prevent deletion of types in use

### New Features (Version 1.1.0)

3. **Invoice Integration**
   - Sale Order Type field automatically added to invoices
   - Auto-fetch sale type from originating sale order
   - Stored field for efficient filtering and reporting
   - Support for customer invoices and credit notes

4. **Enhanced Reporting & Analytics**
   - Filter invoices by sale order type
   - Group invoices by sale type in list views
   - Pivot table analysis by sale type
   - Graph view integration for visual analytics
   - Search capabilities on sale type field

5. **Data Integrity**
   - Automatic propagation from sale order to invoice
   - Proper handling when creating credit notes
   - Copy field value when duplicating invoices
   - Change tracking in chatter
   - Warning logs for mixed sale types

## Installation

### Prerequisites

- Odoo 17.0
- `sale` module installed
- `account` module installed

### Installation Steps

1. Copy the `le_sale_type` module to your Odoo addons directory
2. Update the apps list: Settings → Apps → Update Apps List
3. Search for "Sale Order Type"
4. Click Install

### Upgrade from Version 1.0

If you already have version 1.0 installed:

1. Update the module files
2. Restart Odoo server
3. Go to Settings → Apps
4. Remove "Apps" filter
5. Search for "Sale Order Type"
6. Click "Upgrade"

## Configuration

### Setting Up Sale Order Types

1. Navigate to: **Sales → Configuration → Sale Order Types**
2. Click **Create**
3. Fill in the details:
   - **Sale Type Name**: e.g., "Retail Sale", "Wholesale", "Export"
   - **Description**: Optional description of the sale type
   - **Prefix**: Order number prefix (e.g., "RET/", "WHO/", "EXP/")
   - **Sequence**: Select or create an IR sequence
4. Save the record

### Using Sale Order Types

#### On Sale Orders

1. Create or edit a Sale Order
2. Select the **Sale Type** field (appears after Customer field)
3. Choose the appropriate sale type
4. The order number will be auto-generated using the type's sequence

#### On Invoices (Automatic)

When you create an invoice from a sale order:
- The **Sale Type** field is automatically populated
- No manual intervention required
- Field appears in the invoice header

#### Manual Invoice Creation

If creating invoices manually:
- The **Sale Type** field can be set manually if needed
- Field is visible only on customer invoices (not supplier bills)

## Technical Architecture

### Models

#### `sale.order.type` (New Model)

Primary model for managing sale order types.

**Fields:**
- `name` (Char, required): Type name
- `description` (Text): Type description
- `sequence_id` (Many2one to ir.sequence, required): Number sequence
- `active` (Boolean, default=True): Active status
- `prefix` (Char): Sequence prefix

**Key Methods:**
- `create()`: Syncs prefix with sequence on creation
- `write()`: Updates sequence prefix when type prefix changes
- `_check_unique_sequence()`: Validates sequence uniqueness
- `unlink()`: Prevents deletion if type is used in sale orders

#### `sale.order` (Extended)

**Added Fields:**
- `sale_order_type_id` (Many2one to sale.order.type): Sale type selection

**Overridden Methods:**
- `create()`: Auto-generates order number from type sequence

#### `account.move` (Extended - Version 1.1.0)

**Added Fields:**
- `sale_order_type_id` (Many2one to sale.order.type): Sale type from originating sale order
  - Stored: Yes (for filtering/reporting)
  - Readonly: No (allows manual adjustment)
  - Copy: Yes (propagates to credit notes)
  - Tracking: Yes (changes tracked in chatter)
  - Index: Yes (optimized filtering)

**Key Methods:**
- `_compute_sale_order_type_from_lines()`: Computes sale type from invoice lines
  - Traverses invoice lines → sale lines → sale orders
  - Uses first sale order's type if multiple exist
  - Logs warning if mixed sale types detected

- `create()`: Auto-populates sale type on invoice creation
  - Calls compute method for customer invoices only
  - Runs after standard invoice creation

- `write()`: Recomputes sale type when lines change
  - Only recomputes if not manually set
  - Triggered by invoice_line_ids changes

- `_reverse_moves()`: Copies sale type to credit notes
  - Ensures refunds maintain sale type relationship
  - Adds to default values during reversal

- `_onchange_partner_id_sale_type()`: Resets type on partner change
  - Only for manually created draft invoices
  - Prevents incorrect type associations

### Views

#### Sale Order Views

- **Form View Extension**: Adds sale_order_type_id after partner_id field
  - No create option (must be pre-configured)
  - Domain filter: active types only

#### Invoice Views (New in v1.1.0)

1. **Form View** (`view_move_form_inherit_sale_type`)
   - Sale Type field in header section
   - Visible only on customer invoices and credit notes
   - Auto-filled placeholder text
   - No quick create, no open dialog

2. **Tree/List View** (`view_invoice_tree_inherit_sale_type`)
   - Sale Type column after Partner
   - Optional display (show by default)
   - Sortable and filterable

3. **Search View** (`view_account_invoice_filter_inherit_sale_type`)
   - Sale Type search field
   - Filter option to group by sale type
   - Group By option in filters section

4. **Pivot View** (`view_invoice_pivot_inherit_sale_type`)
   - Sale Type as row/column dimension
   - Enables cross-analysis with other fields

5. **Graph View** (`view_invoice_graph_inherit_sale_type`)
   - Sale Type as grouping option
   - Visual analytics by sale type

### Security

**Access Rights** (`ir.model.access.csv`):
- Model: `sale.order.type`
- All users: Read, Write, Create, Delete
- No specific group restrictions (customize as needed)

## Usage Scenarios

### Scenario 1: Standard Sales Flow

1. **Create Sale Order**
   ```
   Customer: ABC Corp
   Sale Type: Wholesale
   → Order Number: WHO/2024/0001 (auto-generated)
   ```

2. **Create Invoice from Sale Order**
   ```
   Click "Create Invoice" button
   → Sale Type: Wholesale (auto-filled)
   → Invoice Number: INV/2024/0123
   ```

3. **Result**
   - Invoice linked to sale order
   - Sale Type automatically populated
   - Can filter invoices by "Wholesale" type

### Scenario 2: Credit Note Creation

1. **Create Credit Note**
   ```
   Open invoice → Click "Add Credit Note"
   → Sale Type: Wholesale (auto-copied)
   ```

2. **Result**
   - Credit note maintains sale type
   - Relationship preserved for reporting

### Scenario 3: Manual Invoice

1. **Create Manual Invoice**
   ```
   Invoicing → Customer Invoices → Create
   Customer: XYZ Ltd
   Add invoice lines (no sale order)
   → Sale Type: Empty (can set manually if needed)
   ```

### Scenario 4: Mixed Sale Orders (Edge Case)

1. **Invoice from Multiple Orders**
   ```
   Invoice Line 1: From Sale Order A (Type: Retail)
   Invoice Line 2: From Sale Order B (Type: Wholesale)
   → Sale Type: Retail (first order's type)
   → Warning logged about mixed types
   ```

## Reporting & Analytics

### Filtering Invoices by Sale Type

1. Navigate to: **Invoicing → Customers → Invoices**
2. Click **Filters** dropdown
3. Select **Sale Type** grouping option
4. Or use search bar: type sale type name

### Pivot Analysis

1. Navigate to: **Invoicing → Customers → Invoices**
2. Switch to **Pivot** view
3. Add **Sale Type** to rows or columns
4. Cross-analyze with:
   - Customer
   - Salesperson
   - Date period
   - Amount totals

### Graph/Chart Analysis

1. Navigate to: **Invoicing → Customers → Invoices**
2. Switch to **Graph** view
3. Group by **Sale Type**
4. Visualize revenue distribution by sale type

## Customization Guide

### Adding Custom Logic

**Example: Set Default Sale Type per Customer**

```python
# In custom module, extend res.partner
class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_sale_type_id = fields.Many2one(
        'sale.order.type',
        string='Default Sale Type'
    )

# Extend sale.order
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_sale_type(self):
        if self.partner_id.default_sale_type_id:
            self.sale_order_type_id = self.partner_id.default_sale_type_id
```

### Restricting Access

To restrict sale type management to Sales Managers:

1. Edit `security/ir.model.access.csv`
2. Change group_id column:
   ```csv
   access_sale_order_type,sale.order.type,model_sale_order_type,sales_team.group_sale_manager,1,1,1,1
   ```

## Troubleshooting

### Issue: Sale Type Not Appearing on Invoice

**Possible Causes:**
1. Invoice not created from sale order
2. Sale order has no sale type set
3. Invoice is a supplier bill (field only visible on customer invoices)

**Solution:**
- Verify sale order has sale type set
- Check invoice type (must be customer invoice or credit note)
- Manually set if invoice created without sale order

### Issue: Different Sale Type on Invoice

**Cause:**
- Invoice contains lines from multiple sale orders with different types

**Solution:**
- Check invoice lines to verify source sale orders
- Review logs for mixed type warnings
- Manually adjust if needed

### Issue: Cannot Delete Sale Order Type

**Cause:**
- Type is used in existing sale orders

**Solution:**
- Archive the type instead (uncheck "Active")
- Or reassign affected sale orders to different type first

## Best Practices

1. **Plan Sale Types Carefully**
   - Define types based on business needs
   - Consider reporting requirements
   - Use clear, descriptive names

2. **Sequence Management**
   - Create dedicated sequences for each type
   - Use distinctive prefixes for easy identification
   - Set appropriate padding (e.g., 4-5 digits)

3. **User Training**
   - Train sales team to always select sale type
   - Explain the impact on invoicing and reporting
   - Document your organization's type definitions

4. **Data Migration**
   - If upgrading from v1.0, existing invoices won't have types
   - Consider running a migration script if historical data is important
   - New invoices will auto-populate from sale orders

5. **Reporting Setup**
   - Create saved filters for common sale type reports
   - Set up scheduled reports by sale type
   - Use pivot views for executive dashboards

## Developer Notes

### Database Schema

**New Table:** `sale_order_type`
```sql
CREATE TABLE sale_order_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    sequence_id INTEGER REFERENCES ir_sequence(id),
    active BOOLEAN DEFAULT TRUE,
    prefix VARCHAR,
    create_uid INTEGER REFERENCES res_users(id),
    write_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP,
    write_date TIMESTAMP
);
```

**Modified Table:** `sale_order`
```sql
ALTER TABLE sale_order
ADD COLUMN sale_order_type_id INTEGER REFERENCES sale_order_type(id);
```

**Modified Table:** `account_move` (v1.1.0)
```sql
ALTER TABLE account_move
ADD COLUMN sale_order_type_id INTEGER REFERENCES sale_order_type(id);

CREATE INDEX idx_account_move_sale_type ON account_move(sale_order_type_id);
```

### API Usage

**Create Sale Order with Type:**
```python
sale_order = self.env['sale.order'].create({
    'partner_id': partner.id,
    'sale_order_type_id': sale_type.id,
    # name will be auto-generated
})
```

**Get Invoices by Sale Type:**
```python
invoices = self.env['account.move'].search([
    ('move_type', '=', 'out_invoice'),
    ('sale_order_type_id', '=', sale_type.id),
    ('state', '=', 'posted')
])
```

**Compute Sale Type for Existing Invoice:**
```python
invoice._compute_sale_order_type_from_lines()
```

## Support & Contributing

- **Support Email**: support@lunerpsolution.com
- **Website**: https://www.lunerpsolution.com
- **Issues**: Report bugs through your Odoo support channel

## Changelog

### Version 1.1.0 (2024-12-20)
- **Added**: Invoice integration with sale_order_type_id field
- **Added**: Auto-computation of sale type from sale orders
- **Added**: Enhanced invoice views (form, tree, search, pivot, graph)
- **Added**: Filtering and grouping capabilities
- **Added**: Credit note support
- **Added**: Comprehensive documentation
- **Updated**: Module dependencies to include 'account'
- **Updated**: Module description and summary

### Version 1.0.0 (Initial Release)
- **Added**: Sale Order Type model
- **Added**: Sequence management per type
- **Added**: Sale Order integration
- **Added**: Basic security configuration

## License

This module is licensed under LGPL-3. See LICENSE file for details.

---

**Note**: This module is production-ready and follows Odoo 17 best practices. For enterprise-specific features or custom requirements, please contact Luna ERP Solutions.
