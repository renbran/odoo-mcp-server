# Deals Management Module - API Reference

## Model: sale.order (Extended)

### Inherited Model
- **Base Model:** `sale.order` (from sale module)
- **Module:** deals_management
- **Python File:** `models/sale_order_deals.py`

---

## 📋 Fields Reference

### Selection Fields

#### `sales_type`
- **Type:** Selection
- **Values:** primary, secondary, exclusive, rental
- **Default:** primary
- **Tracking:** Yes
- **String:** Sales Type
- **XML Widget:** radio with horizontal options
- **Description:** Type of real estate deal

---

### Many2one Fields

#### `primary_buyer_id`
- **Type:** Many2one (res.partner)
- **Domain:** `[('is_company', '=', False)]`
- **Tracking:** Yes
- **String:** Primary Buyer
- **Required:** No
- **Description:** Main buyer for the deal

#### `secondary_buyer_id`
- **Type:** Many2one (res.partner)
- **Domain:** `[('is_company', '=', False)]`
- **Tracking:** Yes
- **String:** Secondary Buyer
- **Required:** No
- **Description:** Co-buyer for the deal

#### `project_id`
- **Type:** Many2one (project.project)
- **Tracking:** Yes
- **String:** Project
- **Required:** No
- **Description:** Real estate project reference

---

### Char Fields

#### `unit_reference`
- **Type:** Char
- **Max Length:** 256
- **Tracking:** Yes
- **String:** Unit
- **Required:** No
- **Help:** Unit number or reference
- **Description:** Property unit identifier

---

### Date Fields

#### `booking_date`
- **Type:** Date
- **Tracking:** Yes
- **String:** Booking Date
- **Required:** No
- **Help:** Date when the deal was booked
- **Default:** None
- **Description:** When buyer committed to the deal

#### `estimated_invoice_date`
- **Type:** Date
- **Tracking:** Yes
- **String:** Estimated Invoice Date
- **Required:** No
- **Help:** Expected date for invoice generation
- **Default:** None
- **Description:** Projected invoice creation date

---

### Monetary Fields

#### `deal_sales_value`
- **Type:** Monetary
- **Tracking:** Yes
- **String:** Sales Value
- **Currency:** Company currency
- **Default:** 0
- **Description:** Sale price of the unit/property
- **Usage:** Base for commission calculations

#### `vat_amount`
- **Type:** Monetary (Computed)
- **Computed By:** `_compute_financial_summary`
- **String:** VAT Amount
- **Currency:** Company currency
- **Readonly:** Yes
- **Description:** Calculated VAT on sale

#### `total_without_vat`
- **Type:** Monetary (Computed)
- **Computed By:** `_compute_financial_summary`
- **String:** Total without VAT
- **Currency:** Company currency
- **Readonly:** Yes
- **Description:** Sale total before tax

#### `total_with_vat`
- **Type:** Monetary (Computed)
- **Computed By:** `_compute_financial_summary`
- **String:** Total with VAT
- **Currency:** Company currency
- **Readonly:** Yes
- **Description:** Sale total including tax

---

### Float Fields

#### `deal_commission_rate`
- **Type:** Float
- **Tracking:** Yes
- **String:** Commission Rate
- **Default:** 0
- **Digits:** (5, 2)
- **Description:** Commission percentage (0-100)
- **Example:** 5.00 = 5%

---

### Integer Fields

#### `invoice_count`
- **Type:** Integer (Computed)
- **Computed By:** `_compute_document_counts`
- **String:** Number of Invoices
- **Readonly:** Yes
- **Default:** 0
- **Description:** Count of related invoices
- **Usage:** Smart button visibility

#### `commission_count`
- **Type:** Integer (Computed)
- **Computed By:** `_compute_document_counts`
- **String:** Number of Commissions
- **Readonly:** Yes
- **Default:** 0
- **Description:** Count of commission records
- **Usage:** Smart button visibility

#### `bill_count`
- **Type:** Integer (Computed)
- **Computed By:** `_compute_document_counts`
- **String:** Number of Bills
- **Readonly:** Yes
- **Default:** 0
- **Description:** Count of vendor bills
- **Usage:** Smart button visibility

#### `kyc_document_count`
- **Type:** Integer (Computed)
- **Computed By:** `_compute_document_counts`
- **String:** KYC Documents Count
- **Readonly:** Yes
- **Default:** 0
- **Description:** Number of KYC documents
- **Usage:** Smart button visibility

#### `booking_form_count`
- **Type:** Integer (Computed)
- **Computed By:** `_compute_document_counts`
- **String:** Booking Forms Count
- **Readonly:** Yes
- **Default:** 0
- **Description:** Number of booking/SPA forms
- **Usage:** Smart button visibility

#### `passport_count`
- **Type:** Integer (Computed)
- **Computed By:** `_compute_document_counts`
- **String:** Passport Count
- **Readonly:** Yes
- **Default:** 0
- **Description:** Number of passport copies
- **Usage:** Smart button visibility

---

### Many2many Fields

#### `kyc_document_ids`
- **Type:** Many2many (ir.attachment)
- **String:** KYC Documents
- **Widget:** many2many_binary
- **Description:** Know Your Customer documents

#### `booking_form_ids`
- **Type:** Many2many (ir.attachment)
- **String:** Booking/SPA Forms
- **Widget:** many2many_binary
- **Description:** Booking forms and Sales & Purchase Agreements

#### `passport_ids`
- **Type:** Many2many (ir.attachment)
- **String:** Passport Copies
- **Widget:** many2many_binary
- **Description:** Scanned passport documents

---

## 🔧 Computed Fields & Methods

### Computed Field Methods

#### `_compute_deal_sales_value()`
```python
@api.depends('amount_untaxed', 'unit_sale_value')
def _compute_deal_sales_value(self)
```
- **Depends On:** `amount_untaxed`, `unit_sale_value`
- **Returns:** Monetary value
- **Purpose:** Calculate actual sales value from order
- **Logic:** Uses order amount if available, falls back to unit_sale_value

#### `_compute_primary_commission()`
```python
@api.depends('primary_commission_percentage')
def _compute_primary_commission(self)
```
- **Depends On:** `primary_commission_percentage`
- **Returns:** Monetary value
- **Purpose:** Calculate commission amount based on rate
- **Formula:** deal_sales_value × (deal_commission_rate ÷ 100)

#### `_compute_financial_summary()`
```python
@api.depends('amount_untaxed', 'amount_tax', 'amount_total')
def _compute_financial_summary(self)
```
- **Depends On:** `amount_untaxed`, `amount_tax`, `amount_total`
- **Returns:** Multiple values (VAT, totals)
- **Purpose:** Calculate financial totals
- **Calculates:**
  - `vat_amount` = amount_tax
  - `total_without_vat` = amount_untaxed
  - `total_with_vat` = amount_total

#### `_compute_document_counts()`
```python
@api.depends('kyc_document_ids', 'booking_form_ids', 'passport_ids')
def _compute_document_counts(self)
```
- **Depends On:** `kyc_document_ids`, `booking_form_ids`, `passport_ids`
- **Returns:** Multiple integer values
- **Purpose:** Count attached documents
- **Calculates:**
  - `kyc_document_count` = len(kyc_document_ids)
  - `booking_form_count` = len(booking_form_ids)
  - `passport_count` = len(passport_ids)

---

### Action Methods

#### `action_view_invoices()`
```python
def action_view_invoices(self)
```
- **Accessible:** From smart button
- **Context:** self (deal record)
- **Returns:** Action (dict)
- **Purpose:** Open related invoices
- **Domain:** Filters invoices for this deal

#### `action_view_commissions()`
```python
def action_view_commissions(self)
```
- **Accessible:** From smart button
- **Context:** self (deal record)
- **Returns:** Action (dict)
- **Purpose:** Open related commissions
- **Domain:** Filters commissions for this deal

#### `action_view_bills()`
```python
def action_view_bills(self)
```
- **Accessible:** From smart button
- **Context:** self (deal record)
- **Returns:** Action (dict)
- **Purpose:** Open related vendor bills
- **Domain:** Filters bills for this deal

#### `action_view_kyc_documents()`
```python
def action_view_kyc_documents(self)
```
- **Accessible:** From smart button
- **Context:** self (deal record)
- **Returns:** Action (dict) or ir.attachment view
- **Purpose:** Display KYC documents
- **Returns:** Attachment records

#### `action_view_booking_forms()`
```python
def action_view_booking_forms(self)
```
- **Accessible:** From smart button
- **Context:** self (deal record)
- **Returns:** Action (dict) or ir.attachment view
- **Purpose:** Display booking/SPA forms
- **Returns:** Attachment records

#### `action_view_passports()`
```python
def action_view_passports(self)
```
- **Accessible:** From smart button
- **Context:** self (deal record)
- **Returns:** Action (dict) or ir.attachment view
- **Purpose:** Display passport copies
- **Returns:** Attachment records

---

## 📊 Views & Actions

### Views Defined

#### `view_order_deals_tree`
- **Type:** Tree (List) View
- **Model:** sale.order
- **String:** Deals
- **Decorations:**
  - info: state == 'draft'
  - success: state == 'sale'
  - muted: state == 'cancel'
- **Fields Displayed:** name, sales_type, dates, buyers, project, unit, values, counts

#### `view_order_deals_form`
- **Type:** Form View
- **Model:** sale.order
- **String:** Deal Form
- **Inherits:** sale.view_order_form
- **Adds:**
  - Sales Type field (radio widget)
  - Smart buttons (6 buttons)
  - Deals Information page
  - Document attachment sections

#### `view_order_deals_search`
- **Type:** Search View
- **Model:** sale.order
- **String:** Search Deals
- **Filters:**
  - By sales type (4 filters)
  - By dates (2 filters)
  - Group by options (5 groupings)
- **Searchable Fields:** name, buyers, project, unit, dates

### Actions Defined

#### `action_all_deals`
- **View Mode:** tree, form, pivot, graph
- **Default View:** tree
- **Context:** {}
- **Help Text:** "Create your first deal!"

#### `action_primary_deals`
- **View Mode:** tree, form, pivot, graph
- **Domain:** `[('sales_type', '=', 'primary')]`
- **Default Context:** `{'default_sales_type': 'primary'}`
- **Filter:** search_default_filter_primary

#### `action_secondary_deals`
- **View Mode:** tree, form, pivot, graph
- **Domain:** `[('sales_type', '=', 'secondary')]`
- **Default Context:** `{'default_sales_type': 'secondary'}`

#### `action_exclusive_deals`
- **View Mode:** tree, form, pivot, graph
- **Domain:** `[('sales_type', '=', 'exclusive')]`
- **Default Context:** `{'default_sales_type': 'exclusive'}`

#### `action_rental_deals`
- **View Mode:** tree, form, pivot, graph
- **Domain:** `[('sales_type', '=', 'rental')]`
- **Default Context:** `{'default_sales_type': 'rental'}`

---

## 🔐 Security Access

### User Level (base.group_user)
- **Read:** ✅ Yes
- **Write:** ✅ Yes
- **Create:** ✅ Yes
- **Delete:** ✅ Yes
- **Fields:** All fields accessible

### Manager Level (sales_team.group_sale_manager)
- **Read:** ✅ Yes
- **Write:** ✅ Yes
- **Create:** ✅ Yes
- **Delete:** ✅ Yes
- **Fields:** All fields accessible

---

## 🎯 Usage Examples

### Create Deal via Python API
```python
deal = env['sale.order'].create({
    'partner_id': partner_id,
    'sales_type': 'primary',
    'primary_buyer_id': buyer_id,
    'booking_date': fields.Date.today(),
    'estimated_invoice_date': fields.Date.today() + timedelta(days=30),
    'deal_sales_value': 500000.00,
    'deal_commission_rate': 5.0,
})
```

### Access Commission Amount
```python
deal = env['sale.order'].browse(deal_id)
commission = deal.primary_commission
```

### Attach KYC Document
```python
attachment = env['ir.attachment'].create({
    'name': 'KYC Document',
    'res_model': 'sale.order',
    'res_id': deal.id,
    'datas': base64.b64encode(file_content),
})
deal.kyc_document_ids |= attachment
```

### Filter Deals by Sales Type
```python
primary_deals = env['sale.order'].search([
    ('sales_type', '=', 'primary')
])
```

### Get Deal Count by Type
```python
counts = {}
for sale_type in ['primary', 'secondary', 'exclusive', 'rental']:
    counts[sale_type] = env['sale.order'].search_count([
        ('sales_type', '=', sale_type)
    ])
```

### Access Related Invoices
```python
deal = env['sale.order'].browse(deal_id)
invoices = deal.invoice_ids
```

### Access Related Commissions
```python
deal = env['sale.order'].browse(deal_id)
commissions = env['commission.line'].search([
    ('sale_id', '=', deal.id)
])
```

---

## 🚀 Extending the Module

### Add New Field
```python
# In models/sale_order_deals.py
new_field = fields.Char(
    string='New Field',
    tracking=True
)

# Then add to view in deals_views.xml
<field name="new_field"/>
```

### Add New Computed Field
```python
# In models/sale_order_deals.py
@api.depends('deal_sales_value', 'some_other_field')
def _compute_new_field(self):
    for record in self:
        record.new_field = record.deal_sales_value * 0.5

new_computed_field = fields.Monetary(
    compute='_compute_new_field',
    string='New Computed Field'
)
```

### Add New Action Method
```python
# In models/sale_order_deals.py
def action_new_operation(self):
    """Perform custom operation"""
    for record in self:
        # Custom logic here
        pass
    return {
        'type': 'ir.actions.act_window',
        'res_model': 'target.model',
        'view_mode': 'tree,form',
        'domain': [('parent_id', '=', self.id)],
    }

# Then add button in deals_views.xml
<button name="action_new_operation" 
    type="object" 
    string="New Operation"/>
```

---

## 📈 Performance Considerations

### Expensive Operations
- Loading all documents (kyc_document_ids, booking_form_ids, passport_ids)
- Computing counts on large datasets
- Filtering by multiple dates

### Optimization Tips
1. **Use `optional="hide"`** for rarely-viewed fields
2. **Index fields used in domains:**
   - sales_type
   - booking_date
   - estimated_invoice_date
3. **Avoid computing counts in list views**
4. **Use `search_default_filter_X`** for pre-filtered views

### Database Queries
```sql
-- Index recommendations
CREATE INDEX idx_sale_order_sales_type ON sale_order(sales_type);
CREATE INDEX idx_sale_order_booking_date ON sale_order(booking_date);
CREATE INDEX idx_sale_order_estimated_invoice_date ON sale_order(estimated_invoice_date);
```

---

## 🐛 Error Handling

### Common Errors

#### "No primary buyer specified"
```python
try:
    invoice = deal.action_invoice_create()
except UserError as e:
    if 'primary_buyer' in str(e):
        # Handle missing primary buyer
        pass
```

#### "Invalid sales type"
```python
valid_types = ['primary', 'secondary', 'exclusive', 'rental']
if sales_type not in valid_types:
    raise ValueError(f"Invalid sales type: {sales_type}")
```

#### "Document attachment failed"
```python
try:
    deal.kyc_document_ids |= attachment
except Exception as e:
    _logger.error(f"Failed to attach document: {e}")
```

---

## 📚 Dependencies

### Odoo Modules
- `sale` - Sale order model
- `commission_ax` - Commission management
- `account` - Financial data
- `project` - Project management

### External Dependencies
- None (uses standard Odoo libraries)

---

**Last Updated:** 2024  
**Odoo Version:** 17.0  
**API Version:** 1.0
