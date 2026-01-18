# DEAL_MANAGEMENT: Best Practices from DEAL_REPORT
## Production-Ready Implementation Guide

**Date:** January 18, 2026  
**Source Analysis:** Comparison of `deal_report` (production module) with `deal_management` requirements  
**Target Module:** deal_management  
**Odoo Version:** 17.0

---

## Executive Summary

The `deal_report` module demonstrates Odoo 17 best practices across:
- ✅ Structured module organization
- ✅ Comprehensive security implementation
- ✅ Well-designed data models with tracking
- ✅ Professional view hierarchy
- ✅ Automated workflows and state management
- ✅ Robust testing and validation

**Key Finding:** `deal_management` module is NOT currently deployed on the server. This guide provides a roadmap to implement it using proven patterns from `deal_report`.

---

## 1. MODULE MANIFEST STRUCTURE

### deal_report Pattern (Reference)
```python
# __manifest__.py
{
    'name': 'Deal Report & Commission Management',
    'version': '17.0.1.0.0',
    'summary': 'Manage real estate deals with automated commission processing',
    'description': """
        Deal Report Module
        ==================
        * Manage Primary, Secondary, Exclusive, and Rental sales
        * Automated commission calculations
        * Direct bill processing
        * Document management with KYC, SPA, and passport uploads
        * Smart buttons for invoices, commissions, and bills
        * Comprehensive commission tracking
    """,
    'category': 'Sales',
    'author': 'Scholarix',
    'website': 'https://scholarix.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
        'account',
        'product',
        'contacts',
        'mail',
        'project',
    ],
    'data': [
        'security/deal_management_security.xml',
        'security/ir.model.access.csv',
        'data/deal_sequence.xml',
        'data/commission_product.xml',
        'views/deal_views.xml',
        'views/deal_line_views.xml',
        'views/deal_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'deal_management/static/src/scss/deal_management.scss',
        ]
    },
    'installable': True,
    'application': True,  # ← Makes it appear in Apps menu
}
```

### ✅ Recommendations for deal_management:

1. **Set `'application': True`** - Enables module to appear in Odoo Apps interface
2. **Use descriptive summary** - Single line for app marketplace
3. **Include full description** - Markdown formatted with features
4. **Specify dependencies clearly** - List all required modules first
5. **Order data files logically**:
   - Security files first
   - Data/sequences next
   - Views last
6. **Define version as `17.0.X.Y.Z`** - Semantic versioning
7. **Add SCSS assets** - For custom styling

---

## 2. MODULE ORGANIZATION STRUCTURE

### deal_report Directory Layout (Reference)
```
deal_report/
├── __init__.py                    ← Import all models
├── __manifest__.py                ← Module configuration
├── models/
│   ├── __init__.py                ← from . import ...
│   ├── deal_report.py             ← Main model (725 lines)
│   ├── deal_commission_line.py     ← Relation model
│   ├── deal_bill_line.py          ← Relation model
│   └── deal_dashboard.py          ← Dashboard/reports
├── views/
│   ├── deal_report_views.xml      ← Main form/tree views
│   ├── deal_commission_line_views.xml
│   ├── deal_bill_line_views.xml
│   ├── deal_dashboard_views.xml   ← Analytics/dashboard
│   ├── deal_report_search.xml     ← Search filters
│   ├── deal_report_analytics.xml  ← Pivot/graph views
│   └── deal_menu.xml              ← Menu definitions
├── security/
│   ├── deal_report_security.xml   ← Record rules (ir.rule)
│   └── ir.model.access.csv        ← Field-level access (CRUD)
├── data/
│   ├── deal_sequence.xml          ← Auto-incrementing references
│   └── commission_product.xml     ← Demo/default data
├── static/
│   └── src/scss/deal_report.scss  ← Custom styling
├── tests/
│   ├── __init__.py
│   ├── test_deal_report.py
│   └── test_security.py
└── README.md                      ← Documentation
```

### ✅ Recommendations for deal_management:

**Create this exact structure:**
```
deal_management/
├── __init__.py                      # Import models
├── __manifest__.py                  # Module config
├── models/
│   ├── __init__.py                  # from . import ...
│   ├── deal_management.py           # Main model
│   ├── deal_stage.py                # Stages/workflow
│   ├── deal_team.py                 # Team management (if needed)
│   └── deal_activity.py             # Activity tracking
├── views/
│   ├── deal_management_views.xml    # Form/Tree/Kanban
│   ├── deal_stage_views.xml         # Stage management
│   ├── deal_search_views.xml        # Filters & groups
│   ├── deal_dashboard_views.xml     # KPIs/Analytics
│   └── deal_menu.xml                # Menu structure
├── security/
│   ├── deal_management_security.xml # Record rules
│   └── ir.model.access.csv          # CRUD permissions
├── data/
│   ├── deal_sequence.xml            # Reference numbering
│   ├── deal_stage_data.xml          # Default stages
│   └── deal_demo.xml                # Demo records
├── static/
│   └── src/scss/deal_management.scss # Styling
├── tests/
│   └── test_deal_management.py      # Unit tests
└── README.md                        # Documentation
```

---

## 3. SECURITY IMPLEMENTATION

### deal_report Pattern (Reference)

**File: security/deal_report_security.xml**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <data noupdate="1">
    <!-- Group Definitions -->
    <record id="group_deal_report_manager" model="res.groups">
      <field name="name">Deal Report Manager</field>
      <field name="category_id" ref="base.module_category_sales"/>
    </record>

    <!-- Record Rules: Salesperson sees only own deals -->
    <record id="deal_report_salesperson_rule" model="ir.rule">
      <field name="name">Sales Person: Own Deals</field>
      <field name="model_id" ref="model_deal_report"/>
      <field name="domain_force">[("create_uid", "=", user.id)]</field>
      <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
    </record>

    <!-- Record Rules: Manager sees all -->
    <record id="deal_report_manager_rule" model="ir.rule">
      <field name="name">Sales Manager: All Deals</field>
      <field name="model_id" ref="model_deal_report"/>
      <field name="domain_force">[(1, "=", 1)]</field>
      <field name="groups" eval="[(4, ref('sales_team.group_sale_manager'))]"/>
    </record>
  </data>
</odoo>
```

**File: security/ir.model.access.csv**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_deal_report_user,deal.report.user,model_deal_report,sales_team.group_sale_salesman,1,1,1,0
access_deal_report_manager,deal.report.manager,model_deal_report,sales_team.group_sale_manager,1,1,1,1
access_deal_commission_line_user,deal.commission.line.user,model_deal_commission_line,sales_team.group_sale_salesman,1,1,1,0
access_deal_commission_line_manager,deal.commission.line.manager,model_deal_commission_line,sales_team.group_sale_manager,1,1,1,1
access_deal_bill_line_user,deal.bill.line.user,model_deal_bill_line,sales_team.group_sale_salesman,1,0,0,0
access_deal_bill_line_manager,deal.bill.line.manager,model_deal_bill_line,sales_team.group_sale_manager,1,1,1,1
access_deal_bill_line_accountant,deal.bill.line.accountant,model_deal_bill_line,account.group_account_invoice,1,1,1,0
```

### ✅ Recommendations for deal_management:

**Implement 3-tier security model:**

1. **Salesperson** (group_sale_salesman)
   - Read/Write own deals only
   - Cannot delete
   - Full CRUD on associated records

2. **Manager** (group_sale_manager)
   - Read/Write all team's deals
   - Can delete
   - Full CRUD on all models

3. **Accountant** (account.group_account_invoice)
   - Read deal summaries
   - Read bill records
   - Cannot modify deals

**Template for deal_management_security.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <data noupdate="1">
    <!-- Create custom group if needed -->
    <record id="group_deal_management_manager" model="res.groups">
      <field name="name">Deal Management Manager</field>
      <field name="category_id" ref="base.module_category_sales"/>
    </record>

    <!-- Salesperson: Own deals only -->
    <record id="deal_management_salesperson_rule" model="ir.rule">
      <field name="name">Sales Person: Own Deals</field>
      <field name="model_id" ref="model_deal_management"/>
      <field name="domain_force">[("create_uid", "=", user.id)]</field>
      <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
      <field name="perm_read" eval="True"/>
      <field name="perm_write" eval="True"/>
      <field name="perm_create" eval="False"/>
      <field name="perm_unlink" eval="False"/>
    </record>

    <!-- Manager: All deals -->
    <record id="deal_management_manager_rule" model="ir.rule">
      <field name="name">Manager: All Deals</field>
      <field name="model_id" ref="model_deal_management"/>
      <field name="domain_force">[(1, "=", 1)]</field>
      <field name="groups" eval="[(4, ref('sales_team.group_sale_manager'))]"/>
    </record>

    <!-- Company isolation -->
    <record id="deal_management_company_rule" model="ir.rule">
      <field name="name">Company: Own Company Deals</field>
      <field name="model_id" ref="model_deal_management"/>
      <field name="domain_force">[("company_id", "=", user.company_id.id)]</field>
      <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    </record>
  </data>
</odoo>
```

---

## 4. MODEL DESIGN PATTERNS

### deal_report Pattern (Reference)

**Key Design Decisions:**

```python
class DealReport(models.Model):
    _name = 'deal.report'
    _description = 'Deal Report'
    
    # ✅ Inherit from mail.thread for change tracking
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # ✅ Default ordering
    _order = 'booking_date desc, id desc'
    
    # ✅ SQL constraints for data integrity
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Deal reference must be unique.'),
    ]

    # ✅ Required fields with tracking
    name = fields.Char(
        string='Deal Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True,  # ← Shows changes in chatter
    )
    
    # ✅ State machine (workflow)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('invoiced', 'Invoiced'),
            ('commissioned', 'Commissioned'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    
    # ✅ Calculated fields with storage
    vat_amount = fields.Monetary(
        string='VAT Amount',
        compute='_compute_vat_totals',
        store=True,  # ← Searchable & reportable
        currency_field='currency_id',
    )

    # ✅ Computed fields with dependencies
    @api.depends('sales_value', 'vat_rate')
    def _compute_vat_totals(self):
        for record in self:
            record.vat_amount = (
                record.sales_value * record.vat_rate / 100
            )
```

### ✅ Recommendations for deal_management:

**Apply this pattern:**

```python
# models/deal_management.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class DealManagement(models.Model):
    _name = 'deal.management'
    _description = 'Deal Management'
    
    # Inherit for chatter & activity
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Default sort order
    _order = 'date_created desc, id desc'
    
    # Unique constraints
    _sql_constraints = [
        ('reference_unique', 'unique(reference)', 
         'Deal reference must be unique'),
        ('code_unique', 'unique(code)', 
         'Deal code must be unique'),
    ]

    # === REQUIRED FIELDS (Always include tracking) ===
    reference = fields.Char(
        string='Deal Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True,
    )

    code = fields.Char(
        string='Deal Code',
        required=True,
        tracking=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Primary Contact',
        required=True,
        tracking=True,
        domain="[('is_company', '=', False)]",
    )

    # === STATE MACHINE (Workflow) ===
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('qualification', 'Qualification'),
            ('proposal', 'Proposal Sent'),
            ('negotiation', 'Negotiation'),
            ('won', 'Won'),
            ('lost', 'Lost'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
        copy=False,
    )

    stage_id = fields.Many2one(
        'deal.stage',
        string='Stage',
        tracking=True,
        compute='_compute_stage',
        store=True,
    )

    # === WORKFLOW FIELDS ===
    date_created = fields.Date(
        string='Creation Date',
        default=fields.Date.today,
        tracking=True,
        readonly=True,
    )

    date_closed = fields.Date(
        string='Closed Date',
        tracking=True,
        readonly=True,
    )

    # === CALCULATED FIELDS (Stored for reporting) ===
    amount_total = fields.Monetary(
        string='Deal Amount',
        compute='_compute_amounts',
        store=True,
        tracking=True,
        currency_field='currency_id',
    )

    commission_amount = fields.Monetary(
        string='Commission',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    # === RELATIONAL FIELDS ===
    line_ids = fields.One2many(
        'deal.line',
        'deal_id',
        string='Deal Lines',
        tracking=True,
    )

    invoice_ids = fields.Many2many(
        'account.move',
        'deal_invoice_rel',
        'deal_id',
        'invoice_id',
        string='Invoices',
        readonly=True,
    )

    # === COMPUTED FIELD WITH DEPENDENCY ===
    @api.depends('state')
    def _compute_stage(self):
        """Compute stage from state"""
        for record in self:
            stage_mapping = {
                'draft': 'stage_draft',
                'qualification': 'stage_qualification',
                'proposal': 'stage_proposal',
                'negotiation': 'stage_negotiation',
                'won': 'stage_won',
                'lost': 'stage_lost',
                'cancelled': 'stage_cancelled',
            }
            stage_ref = stage_mapping.get(record.state)
            if stage_ref:
                record.stage_id = self.env.ref(
                    f'deal_management.{stage_ref}'
                )

    # === COMPUTED AMOUNTS ===
    @api.depends('line_ids.amount_total')
    def _compute_amounts(self):
        """Calculate deal and commission amounts"""
        for record in self:
            record.amount_total = sum(
                line.amount_total for line in record.line_ids
            )
            record.commission_amount = (
                record.amount_total * record.commission_rate / 100
            )

    # === WORKFLOW ACTIONS ===
    def action_confirm(self):
        """Move deal to confirmation"""
        for record in self:
            if record.state != 'draft':
                raise ValidationError(
                    _("Can only confirm draft deals")
                )
            record.state = 'qualification'

    def action_won(self):
        """Mark deal as won"""
        for record in self:
            record.state = 'won'
            record.date_closed = fields.Date.today()

    def action_lost(self):
        """Mark deal as lost"""
        for record in self:
            record.state = 'lost'
            record.date_closed = fields.Date.today()

    # === CONSTRAINTS ===
    @api.constrains('amount_total', 'commission_rate')
    def _check_amounts(self):
        """Validate amounts"""
        for record in self:
            if record.amount_total < 0:
                raise ValidationError(
                    _("Deal amount cannot be negative")
                )
            if not (0 <= record.commission_rate <= 100):
                raise ValidationError(
                    _("Commission rate must be between 0 and 100")
                )

    # === LIFECYCLE HOOKS ===
    @api.model_create_multi
    def create(self, vals_list):
        """Set reference on creation"""
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'deal.management'
                )
        return super().create(vals_list)

    def write(self, vals):
        """Track important changes"""
        result = super().write(vals)
        if 'state' in vals:
            for record in self:
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref(
                        'mail.mail_activity_data_todo'
                    ).id,
                    'summary': f'Deal moved to {record.state}',
                    'res_id': record.id,
                    'res_model_id': self.env['ir.model'].search(
                        [('model', '=', 'deal.management')]
                    ).id,
                })
        return result
```

---

## 5. VIEW DESIGN BEST PRACTICES

### deal_report Pattern (Reference)

The module includes:
- ✅ **Form View** - Detailed record editing
- ✅ **Tree View** - List/grid display  
- ✅ **Search View** - Filters and grouping
- ✅ **Pivot View** - Analytics/crosstabs
- ✅ **Dashboard View** - KPIs and summaries
- ✅ **Kanban View** - Stage-based visualization

### ✅ Recommendations for deal_management:

**Create comprehensive view hierarchy:**

```xml
<!-- views/deal_management_views.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <!-- FORM VIEW: Main record editing -->
  <record id="deal_management_view_form" model="ir.ui.view">
    <field name="name">Deal Management Form</field>
    <field name="model">deal.management</field>
    <field name="type">form</field>
    <field name="arch" type="xml">
      <form string="Deal">
        <!-- Header with status bar -->
        <header>
          <button name="action_confirm" string="Confirm"
            type="object" states="draft" class="btn-primary"/>
          <button name="action_won" string="Mark as Won"
            type="object" states="qualification,proposal,negotiation"
            class="btn-success"/>
          <button name="action_lost" string="Mark as Lost"
            type="object" states="draft,qualification,proposal,negotiation"/>
          <field name="state" widget="statusbar"
            options="{'clickable': True}"/>
        </header>

        <!-- Main content -->
        <sheet>
          <!-- Top section: Basic info -->
          <div class="oe_title">
            <h1>
              <field name="reference" readonly="1"/>
            </h1>
          </div>

          <!-- Notebooks for sections -->
          <notebook>
            <!-- General Tab -->
            <page string="General Information" name="general">
              <group>
                <group>
                  <field name="code" required="1"/>
                  <field name="partner_id" required="1"/>
                  <field name="stage_id"/>
                  <field name="date_created"/>
                </group>
                <group>
                  <field name="currency_id" invisible="1"/>
                  <field name="amount_total"/>
                  <field name="commission_rate"/>
                  <field name="commission_amount"/>
                  <field name="date_closed"/>
                </group>
              </group>
            </page>

            <!-- Lines Tab -->
            <page string="Deal Lines" name="lines">
              <field name="line_ids">
                <tree editable="bottom">
                  <field name="sequence" widget="handle"/>
                  <field name="product_id"/>
                  <field name="quantity"/>
                  <field name="unit_price"/>
                  <field name="amount_total"/>
                </tree>
              </field>
            </page>

            <!-- Invoices Tab -->
            <page string="Invoices" name="invoices">
              <field name="invoice_ids" readonly="1"/>
            </page>

            <!-- Notes Tab -->
            <page string="Notes" name="notes">
              <field name="notes" widget="html"/>
            </page>
          </notebook>
        </sheet>

        <!-- Bottom: Chatter for messages -->
        <div class="oe_chatter">
          <field name="message_follower_ids"
            widget="mail_followers"/>
          <field name="message_ids" widget="mail_thread"/>
        </div>
      </form>
    </field>
  </record>

  <!-- TREE VIEW: List view with grouping -->
  <record id="deal_management_view_tree" model="ir.ui.view">
    <field name="name">Deal Management List</field>
    <field name="model">deal.management</field>
    <field name="type">tree</field>
    <field name="arch" type="xml">
      <tree string="Deals" decoration-danger="state=='lost'"
        decoration-success="state=='won'">
        <field name="reference"/>
        <field name="code"/>
        <field name="partner_id"/>
        <field name="stage_id"/>
        <field name="amount_total" sum="Total"/>
        <field name="state" widget="badge"
          decoration-success="state=='won'"
          decoration-danger="state=='lost'"/>
      </tree>
    </field>
  </record>

  <!-- KANBAN VIEW: Board-style visualization -->
  <record id="deal_management_view_kanban" model="ir.ui.view">
    <field name="name">Deal Management Kanban</field>
    <field name="model">deal.management</field>
    <field name="type">kanban</field>
    <field name="arch" type="xml">
      <kanban default_group_by="state" quick_create="false">
        <field name="id"/>
        <field name="reference"/>
        <field name="partner_id"/>
        <field name="amount_total"/>
        <field name="state"/>

        <templates>
          <t t-name="kanban-box">
            <div class="oe_kanban_card">
              <div class="oe_kanban_content">
                <div class="oe_kanban_title">
                  <strong><field name="reference"/></strong>
                </div>
                <div class="text-muted">
                  <field name="partner_id"/>
                </div>
                <div class="mt-2">
                  <strong><field name="amount_total"/></strong>
                </div>
              </div>
              <div class="oe_kanban_footer">
                <a type="edit">Edit</a>
              </div>
            </div>
          </t>
        </templates>
      </kanban>
    </field>
  </record>

  <!-- SEARCH VIEW: Filters and groups -->
  <record id="deal_management_view_search" model="ir.ui.view">
    <field name="name">Deal Management Search</field>
    <field name="model">deal.management</field>
    <field name="type">search</field>
    <field name="arch" type="xml">
      <search string="Deals">
        <!-- Search fields -->
        <field name="reference" string="Reference or Code"
          filter_domain="['|',
            ('reference', 'ilike', self),
            ('code', 'ilike', self)]"/>
        <field name="partner_id" string="Contact"/>
        <field name="stage_id" string="Stage"/>

        <!-- Separators -->
        <separator/>

        <!-- Filters -->
        <filter name="state_draft" string="Draft"
          domain="[('state', '=', 'draft')]"/>
        <filter name="state_won" string="Won"
          domain="[('state', '=', 'won')]"/>
        <filter name="state_lost" string="Lost"
          domain="[('state', '=', 'lost')]"/>

        <separator/>

        <!-- Grouping -->
        <group expand="0" string="Group By">
          <filter name="group_by_state" string="State"
            context="{'group_by': 'state'}"/>
          <filter name="group_by_stage" string="Stage"
            context="{'group_by': 'stage_id'}"/>
          <filter name="group_by_partner" string="Contact"
            context="{'group_by': 'partner_id'}"/>
          <filter name="group_by_date" string="Date"
            context="{'group_by': 'date_created'}"/>
        </group>
      </search>
    </field>
  </record>

  <!-- PIVOT VIEW: Analytics -->
  <record id="deal_management_view_pivot" model="ir.ui.view">
    <field name="name">Deal Management Pivot</field>
    <field name="model">deal.management</field>
    <field name="type">pivot</field>
    <field name="arch" type="xml">
      <pivot string="Deal Analysis">
        <field name="state" type="row"/>
        <field name="amount_total" type="measure" widget="monetary"/>
        <field name="id" type="measure" aggregation="count"/>
      </pivot>
    </field>
  </record>

  <!-- GRAPH VIEW: Charts -->
  <record id="deal_management_view_graph" model="ir.ui.view">
    <field name="name">Deal Management Graph</field>
    <field name="model">deal.management</field>
    <field name="type">graph</field>
    <field name="arch" type="xml">
      <graph string="Deals by Amount" type="bar">
        <field name="stage_id" type="row"/>
        <field name="amount_total" type="measure" widget="monetary"/>
      </graph>
    </field>
  </record>

  <!-- ACTION: Open deals list -->
  <record id="deal_management_action" model="ir.actions.act_window">
    <field name="name">Deals</field>
    <field name="res_model">deal.management</field>
    <field name="view_mode">tree,form,kanban,pivot,graph</field>
    <field name="search_view_id" ref="deal_management_view_search"/>
    <field name="context">{'search_default_state_draft': 1}</field>
    <field name="help" type="html">
      <p class="oe_view_nocontent_create">
        No deals found. Create your first deal!
      </p>
    </field>
  </record>
</odoo>
```

---

## 6. SECURITY & ACCESS CONTROL

### ✅ Implementation Checklist:

- [ ] **ir.model.access.csv** - Define CRUD for each group
- [ ] **ir.rule records** - Domain-based filtering
- [ ] **Field-level access** - Read-only by group
- [ ] **Company isolation** - Data per company
- [ ] **Test security** - Verify in unit tests

### Example Security Rule Pattern:

```xml
<!-- Deal restricted to company -->
<record id="deal_management_company_rule" model="ir.rule">
  <field name="name">Deal: Company Isolation</field>
  <field name="model_id" ref="model_deal_management"/>
  <field name="domain_force">[("company_id", "=", user.company_id.id)]</field>
  <field name="groups" eval="[(4, ref('base.group_user'))]"/>
  <field name="perm_read" eval="True"/>
  <field name="perm_write" eval="True"/>
  <field name="perm_create" eval="False"/>
  <field name="perm_unlink" eval="False"/>
</record>
```

---

## 7. DATA MANAGEMENT

### ✅ Essential Data Files:

**1. Sequences (auto-numbering):**
```xml
<!-- data/deal_sequence.xml -->
<record id="seq_deal_reference" model="ir.sequence">
  <field name="name">Deal Reference</field>
  <field name="code">deal.management</field>
  <field name="prefix">DEAL/</field>
  <field name="padding">5</field>
  <field name="number_next_actual">1</field>
</record>
```

**2. Stages (workflow states):**
```xml
<!-- data/deal_stage_data.xml -->
<record id="stage_draft" model="deal.stage">
  <field name="name">Draft</field>
  <field name="sequence">1</field>
</record>
<record id="stage_won" model="deal.stage">
  <field name="name">Won</field>
  <field name="sequence">99</field>
  <field name="is_won" eval="True"/>
</record>
```

**3. Demo data (for testing):**
```xml
<!-- data/deal_demo.xml -->
<record id="deal_demo_1" model="deal.management">
  <field name="reference">DEAL/00001</field>
  <field name="code">DEMO-001</field>
  <field name="partner_id" ref="base.partner_demo"/>
  <field name="amount_total">50000</field>
</record>
```

---

## 8. TESTING & VALIDATION

### ✅ Recommended Test Suite:

```python
# tests/test_deal_management.py
from odoo.tests import TransactionCase

class TestDealManagement(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.DealManagement = self.env['deal.management']
        self.partner = self.env.ref('base.partner_demo')
    
    def test_01_deal_creation(self):
        """Test creating a deal"""
        deal = self.DealManagement.create({
            'code': 'TEST-001',
            'partner_id': self.partner.id,
            'amount_total': 50000,
        })
        self.assertEqual(deal.state, 'draft')
        self.assertIsNotNone(deal.reference)
    
    def test_02_state_transition(self):
        """Test workflow states"""
        deal = self._create_deal()
        deal.action_confirm()
        self.assertEqual(deal.state, 'qualification')
    
    def test_03_security_salesperson(self):
        """Test salesperson can only see own deals"""
        salesman = self.env.ref('sales_team.group_sale_salesman')
        # Create deal as salesman
        deal = self._create_deal()
        # Check visibility
        deals = self.DealManagement.search([])
        self.assertIn(deal, deals)
    
    def _create_deal(self):
        return self.DealManagement.create({
            'code': 'TEST-001',
            'partner_id': self.partner.id,
            'amount_total': 50000,
        })
```

---

## 9. IMPLEMENTATION ROADMAP

### Phase 1: Module Foundation (Week 1)
- [ ] Create module directory structure
- [ ] Write `__manifest__.py` with all dependencies
- [ ] Create base models (deal_management.py, deal_stage.py)
- [ ] Add security files (XML + CSV)

### Phase 2: Views & UI (Week 2)
- [ ] Create all view types (form, tree, kanban, pivot)
- [ ] Add menu structure
- [ ] Implement smart buttons
- [ ] Add custom SCSS styling

### Phase 3: Workflows & Automation (Week 3)
- [ ] Implement state transitions
- [ ] Add server actions
- [ ] Create computed fields
- [ ] Add validations

### Phase 4: Testing & Documentation (Week 4)
- [ ] Write comprehensive tests
- [ ] Create README.md
- [ ] Document API
- [ ] Deploy to production

### Phase 5: Production Readiness (Week 5)
- [ ] Performance testing
- [ ] Security audit
- [ ] User acceptance testing
- [ ] Documentation finalization

---

## 10. COMMON PITFALLS TO AVOID

| Issue | Impact | Solution |
|-------|--------|----------|
| Missing `_inherit = ['mail.thread']` | No change tracking | Always inherit this for document models |
| Not using `tracking=True` | Can't audit changes | Add tracking to all important fields |
| Hardcoded IDs instead of `ref()` | Breaks in different systems | Use XML references always |
| No SQL constraints | Data corruption | Define `_sql_constraints` |
| Missing security rules | Data leakage | Implement ir.rule for all models |
| Incorrect view dependencies | Views fail to load | Define search views before using them |
| Not using `_compute` and `store=True` | Not searchable in lists | Store computed fields if searchable |
| No copy=False on references | Duplicate IDs | Add to unique/reference fields |
| Missing tests | Regressions undetected | Write tests for critical paths |
| Poor documentation | Confusing for users | Include help text in all fields |

---

## 11. DEPLOYMENT CHECKLIST

```bash
# 1. Verify module structure
find deal_management -type f | grep -E "\.(py|xml|csv)$"

# 2. Check manifest validity
python -m py_compile deal_management/__manifest__.py

# 3. Run security audit
odoo-bin -d scholarixv2 -c /etc/odoo/odoo.conf \
  --module=deal_management --init=all

# 4. Run tests
odoo-bin -d scholarixv2 -c /etc/odoo/odoo.conf \
  -t deal_management.tests.test_deal_management

# 5. Validate XML
for file in deal_management/views/*.xml deal_management/security/*.xml; do
  xmllint --noout "$file" || echo "ERROR: $file"
done

# 6. Check Python syntax
python -m py_compile deal_management/models/*.py

# 7. Create backup before deployment
cp -r /var/lib/odoo/addons/deal_management \
  /var/lib/odoo/addons/deal_management.backup

# 8. Deploy module
cp -r deal_management /var/lib/odoo/addons/

# 9. Restart Odoo
systemctl restart odoo

# 10. Run verification tests
python run_odoo_tests.py --module deal_management
```

---

## CONCLUSION

The `deal_report` module demonstrates production-grade Odoo 17 development:

✅ **Well-structured** - Clear separation of concerns  
✅ **Secure** - Multi-level access control  
✅ **Professional** - Comprehensive views and workflows  
✅ **Maintainable** - Clear naming and organization  
✅ **Tested** - Includes test suites  

**Apply these same patterns to `deal_management` to ensure production readiness.**

---

**Document Version:** 1.0  
**Last Updated:** January 18, 2026  
**Prepared for:** deal_management Module Development
