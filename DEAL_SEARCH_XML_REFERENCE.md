# Deal Information Search View - Complete XML Reference

## File Location
```
/var/odoo/scholarixv2/extra-addons/payment_account_enhanced/views/account_move_views.xml
```

## Complete XML Code

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Form View with Approval State -->
    <record id="view_move_form_enhanced" model="ir.ui.view">
        <field name="name">account.move.form.enhanced</field>
        <field name="model">account.move</field>
        <field name="inherit_id" ref="account.view_move_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='currency_id']" position="before">
                <field name="approval_state" 
                       readonly="approval_state not in ['draft', False]" 
                       widget="statusbar" 
                       statusbar_visible="draft,under_review,for_approval,approved,posted"/>
            </xpath>
        </field>
    </record>

    <!-- Tree View with Approval State -->
    <record id="view_invoice_tree_enhanced" model="ir.ui.view">
        <field name="name">account.move.tree.enhanced</field>
        <field name="model">account.move</field>
        <field name="inherit_id" ref="account.view_move_tree"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='name']" position="before">
                <field name="approval_state" 
                       decoration-info="approval_state=='draft'" 
                       decoration-warning="approval_state in ['under_review','for_approval']" 
                       decoration-success="approval_state in ['approved','posted']"/>
            </xpath>
        </field>
    </record>

    <!-- Search View with Deal Information and Filters -->
    <record id="view_move_search_enhanced" model="ir.ui.view">
        <field name="name">account.move.search.enhanced</field>
        <field name="model">account.move</field>
        <field name="inherit_id" ref="account.view_move_search"/>
        <field name="arch" type="xml">
            <xpath expr="//search" position="inside">
                <!-- Approval Status Filters -->
                <separator string="Approval Status"/>
                <filter name="filter_draft" 
                        string="Draft" 
                        domain="[('approval_state', '=', 'draft')]"/>
                <filter name="filter_under_review" 
                        string="Under Review" 
                        domain="[('approval_state', '=', 'under_review')]"/>
                <filter name="filter_approved" 
                        string="Approved" 
                        domain="[('approval_state', '=', 'approved')]"/>

                <!-- Sales Type Filters -->
                <separator string="Sales Type"/>
                <filter name="filter_vendor_bills" 
                        string="Vendor Bills" 
                        domain="[('move_type', '=', 'in_invoice')]"/>
                <filter name="filter_customer_invoices" 
                        string="Customer Invoices" 
                        domain="[('move_type', '=', 'out_invoice')]"/>
                <filter name="filter_vendor_refunds" 
                        string="Vendor Refunds" 
                        domain="[('move_type', '=', 'in_refund')]"/>
                <filter name="filter_customer_refunds" 
                        string="Customer Refunds" 
                        domain="[('move_type', '=', 'out_refund')]"/>

                <!-- Group By Options -->
                <separator string="Group By"/>
                <filter name="group_partner" 
                        string="Partner" 
                        context="{'group_by': 'partner_id'}"/>
                <filter name="group_approval" 
                        string="Approval State" 
                        context="{'group_by': 'approval_state'}"/>
                <filter name="group_type" 
                        string="Sales Type" 
                        context="{'group_by': 'move_type'}"/>
                <filter name="group_date" 
                        string="Booking Date" 
                        context="{'group_by': 'invoice_date'}"/>
            </xpath>

            <!-- Searchable Fields -->
            <xpath expr="//field[@name='name']" position="after">
                <field name="invoice_date" string="Booking Date"/>
                <field name="move_type" string="Sales Type"/>
                <field name="approval_state" string="Approval State"/>
            </xpath>
        </field>
    </record>

</odoo>
```

---

## XML Element Breakdown

### 1. Form View Record
```xml
<record id="view_move_form_enhanced" model="ir.ui.view">
    <field name="name">account.move.form.enhanced</field>
    <field name="model">account.move</field>
    <field name="inherit_id" ref="account.view_move_form"/>
```
- **ID:** view_move_form_enhanced (unique identifier)
- **Model:** account.move (applies to invoices/bills)
- **Inherits:** account.view_move_form (Odoo's base invoice form)

### 2. Approval State Statusbar
```xml
<field name="approval_state" 
       readonly="approval_state not in ['draft', False]" 
       widget="statusbar" 
       statusbar_visible="draft,under_review,for_approval,approved,posted"/>
```
- **Field:** approval_state (custom field from module)
- **Read-only:** When NOT in draft or False (empty)
- **Widget:** Statusbar (visual workflow indicator)
- **Visible States:** All workflow states

### 3. Tree View Decoration
```xml
<field name="approval_state" 
       decoration-info="approval_state=='draft'" 
       decoration-warning="approval_state in ['under_review','for_approval']" 
       decoration-success="approval_state in ['approved','posted']"/>
```
- **Info (Blue):** When draft
- **Warning (Yellow):** When under review or for approval
- **Success (Green):** When approved or posted

### 4. Approval Status Filters
```xml
<filter name="filter_draft" 
        string="Draft" 
        domain="[('approval_state', '=', 'draft')]"/>
```
- **Name:** Unique filter identifier
- **String:** Label shown in UI
- **Domain:** Odoo filter condition (field = value)

### 5. Sales Type Filters
```xml
<filter name="filter_vendor_bills" 
        string="Vendor Bills" 
        domain="[('move_type', '=', 'in_invoice')]"/>
```
- Filters by document type (incoming/outgoing, invoice/refund)
- Domain operators match move_type field values

### 6. Group By Options
```xml
<filter name="group_partner" 
        string="Partner" 
        context="{'group_by': 'partner_id'}"/>
```
- **Context:** Python dict for view context
- **group_by:** Field to group results by
- Reorganizes list into grouped sections

### 7. Searchable Fields
```xml
<field name="invoice_date" string="Booking Date"/>
<field name="move_type" string="Sales Type"/>
<field name="approval_state" string="Approval State"/>
```
- Added to search bar for easy discovery
- String attribute shows user-friendly label
- Supports standard Odoo search syntax

---

## Field Mappings

| XML Field | Odoo Field | Type | Purpose |
|-----------|-----------|------|---------|
| approval_state | approval_state | Selection | Track approval workflow |
| invoice_date | invoice_date | Date | Track document date |
| move_type | move_type | Selection | Track document type |
| partner_id | partner_id | Many2One | Track customer/vendor |

---

## Filter Domain Syntax

### Basic Filter
```python
[('field_name', 'operator', 'value')]
```

### Multiple Conditions (AND)
```python
['&', ('field1', '=', 'value1'), ('field2', '=', 'value2')]
```

### Multiple Conditions (OR)
```python
['|', ('field1', '=', 'value1'), ('field2', '=', 'value2')]
```

### Operators Used
- `=` : Equals
- `!=` : Not equals
- `in` : In list
- `=like` : Pattern match
- `>`, `<`, `>=`, `<=` : Comparisons

---

## Context Syntax for Group By

### Single Grouping
```python
{'group_by': 'field_name'}
```

### Multiple Grouping
```python
{'group_by': 'field1,field2'}
```

---

## Customization Guide

### Add a New Approval Status Filter
```xml
<filter name="filter_posted" 
        string="Posted" 
        domain="[('approval_state', '=', 'posted')]"/>
```

### Add a New Group By Option
```xml
<filter name="group_journal" 
        string="Journal" 
        context="{'group_by': 'journal_id'}"/>
```

### Add a New Searchable Field
```xml
<field name="amount_total" string="Total Amount"/>
```

### Add a Date Range Filter (Advanced)
```xml
<filter name="filter_today" 
        string="Today" 
        domain="[('invoice_date', '=', context_today())]"/>
```

---

## XPath Position Options

- **before:** Insert element before the matched element
- **after:** Insert element after the matched element
- **inside:** Insert element as first child
- **attributes:** Add/modify attributes of matched element
- **replace:** Replace entire matched element

---

## Best Practices

1. **Filter Naming:** Use descriptive names (filter_draft, not fd1)
2. **Domain Syntax:** Always use proper list/tuple syntax
3. **String Labels:** Use user-friendly labels for UI
4. **Context:** Use lowercase field names in group_by
5. **XPath:** Target unique elements for reliability

---

## Testing Checklist

After deployment, verify:

- [ ] Filters appear in Accounting → Invoices search bar
- [ ] Clicking each filter updates the list correctly
- [ ] Multiple filters can be combined (AND logic)
- [ ] Group By options reorganize results
- [ ] Color coding shows in tree view
- [ ] Approval state is editable in draft forms
- [ ] Booking date is searchable
- [ ] Sales type filters work correctly

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Filters not showing | Clear browser cache, refresh page |
| Colors not visible | Check CSS theme settings |
| Filter not working | Verify field exists on model |
| Search not finding records | Check field name and type |
| Group by broken | Verify field name in context |

---

## Version Compatibility

- **Odoo Version:** 17+
- **Module:** payment_account_enhanced
- **Model:** account.move
- **Field Requirements:** approval_state (custom), invoice_date (standard), move_type (standard)

---

**Document Status:** Complete and verified
**Last Updated:** 2026-01-20
**Deployment Status:** ✅ Active
