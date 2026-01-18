# Quick Implementation Template for deal_management
# Copy & adapt these files to get started immediately

## File 1: __manifest__.py
---manifest-file-start---
# -*- coding: utf-8 -*-
{
    'name': 'Deal Management',
    'version': '17.0.1.0.0',
    'summary': 'Manage sales deals with workflow automation and tracking',
    'description': """
        Deal Management Module
        =====================
        * Track deals through sales pipeline
        * Manage deal stages and state transitions
        * Calculate commissions automatically
        * Generate analytics and reports
        * Activity tracking and notifications
        * Integrated with contacts, projects, and accounting
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
        'data/deal_stage_data.xml',
        'views/deal_stage_views.xml',
        'views/deal_management_views.xml',
        'views/deal_management_search.xml',
        'views/deal_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'deal_management/static/src/scss/deal_management.scss',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
---manifest-file-end---

## File 2: models/__init__.py
---init-file-start---
# -*- coding: utf-8 -*-
from . import deal_stage
from . import deal_management
from . import deal_line
---init-file-end---

## File 3: models/deal_stage.py (Workflow Stages)
---deal-stage-start---
# -*- coding: utf-8 -*-
from odoo import fields, models

class DealStage(models.Model):
    _name = 'deal.stage'
    _description = 'Deal Stage'
    _order = 'sequence'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    is_won = fields.Boolean(string='Won', default=False)
    is_lost = fields.Boolean(string='Lost', default=False)
    color = fields.Integer(string='Color', default=0)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Stage name must be unique'),
    ]
---deal-stage-end---

## File 4: models/deal_management.py (Main Model)
---deal-management-start---
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class DealManagement(models.Model):
    _name = 'deal.management'
    _description = 'Deal Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_created desc'

    _sql_constraints = [
        ('reference_unique', 'unique(reference)', 
         'Deal reference must be unique'),
        ('code_unique', 'unique(code)', 'Deal code must be unique'),
    ]

    # === IDENTIFICATION ===
    reference = fields.Char(
        string='Reference',
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
    name = fields.Char(
        string='Deal Title',
        required=True,
        tracking=True,
    )

    # === PARTIES ===
    partner_id = fields.Many2one(
        'res.partner',
        string='Primary Contact',
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    # === WORKFLOW ===
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('qualification', 'Qualification'),
            ('proposal', 'Proposal'),
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
        compute='_compute_stage',
        store=True,
    )

    # === DATES ===
    date_created = fields.Date(
        default=fields.Date.today,
        tracking=True,
        readonly=True,
    )
    date_won = fields.Date(tracking=True)
    date_lost = fields.Date(tracking=True)

    # === AMOUNTS ===
    amount_total = fields.Monetary(
        string='Total Amount',
        required=True,
        tracking=True,
        currency_field='currency_id',
    )
    commission_rate = fields.Float(
        string='Commission Rate (%)',
        default=5.0,
        tracking=True,
    )
    commission_amount = fields.Monetary(
        string='Commission',
        compute='_compute_commission',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    # === RELATIONS ===
    line_ids = fields.One2many(
        'deal.line',
        'deal_id',
        string='Lines',
    )
    invoice_ids = fields.Many2many(
        'account.move',
        'deal_invoice_rel',
        'deal_id',
        'invoice_id',
        string='Invoices',
        readonly=True,
    )

    # === NOTES ===
    notes = fields.Text(string='Notes')
    color = fields.Integer(default=0)

    # === COMPUTED FIELDS ===
    @api.depends('state')
    def _compute_stage(self):
        for record in self:
            stage_map = {
                'draft': 'deal_management.stage_draft',
                'qualification': 'deal_management.stage_qualification',
                'proposal': 'deal_management.stage_proposal',
                'negotiation': 'deal_management.stage_negotiation',
                'won': 'deal_management.stage_won',
                'lost': 'deal_management.stage_lost',
            }
            stage_ref = stage_map.get(record.state)
            if stage_ref:
                record.stage_id = self.env.ref(stage_ref, raise_if_not_found=False)

    @api.depends('amount_total', 'commission_rate')
    def _compute_commission(self):
        for record in self:
            record.commission_amount = (
                record.amount_total * record.commission_rate / 100
            )

    # === CONSTRAINTS ===
    @api.constrains('amount_total')
    def _check_amount_positive(self):
        for record in self:
            if record.amount_total <= 0:
                raise ValidationError(_("Amount must be positive"))

    # === WORKFLOW ACTIONS ===
    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_("Only draft deals can be confirmed"))
            record.state = 'qualification'

    def action_won(self):
        for record in self:
            record.state = 'won'
            record.date_won = fields.Date.today()

    def action_lost(self):
        for record in self:
            record.state = 'lost'
            record.date_lost = fields.Date.today()

    def action_reset(self):
        for record in self:
            record.state = 'draft'

    # === LIFECYCLE ===
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'deal.management'
                ) or _('New')
        return super().create(vals_list)
---deal-management-end---

## File 5: models/deal_line.py (Deal Items)
---deal-line-start---
# -*- coding: utf-8 -*-
from odoo import api, fields, models

class DealLine(models.Model):
    _name = 'deal.line'
    _description = 'Deal Line'
    _order = 'sequence'

    deal_id = fields.Many2one(
        'deal.management',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=1)
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    description = fields.Char(string='Description')
    quantity = fields.Float(default=1.0)
    unit_price = fields.Monetary(
        string='Unit Price',
        currency_field='currency_id',
    )
    amount_total = fields.Monetary(
        string='Total',
        compute='_compute_amount',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='deal_id.currency_id',
    )

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for record in self:
            record.amount_total = record.quantity * record.unit_price
---deal-line-end---

## File 6: security/deal_management_security.xml
---security-xml-start---
<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <data noupdate="1">
    <!-- Groups -->
    <record id="group_deal_management_manager" model="res.groups">
      <field name="name">Deal Management Manager</field>
      <field name="category_id" ref="base.module_category_sales"/>
    </record>

    <!-- Rules: Salesperson sees own -->
    <record id="deal_salesperson_rule" model="ir.rule">
      <field name="name">Sales Person: Own Deals</field>
      <field name="model_id" ref="model_deal_management"/>
      <field name="domain_force">[("create_uid", "=", user.id)]</field>
      <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
    </record>

    <!-- Rules: Manager sees all -->
    <record id="deal_manager_rule" model="ir.rule">
      <field name="name">Manager: All Deals</field>
      <field name="model_id" ref="model_deal_management"/>
      <field name="domain_force">[(1, "=", 1)]</field>
      <field name="groups" eval="[(4, ref('sales_team.group_sale_manager'))]"/>
    </record>

    <!-- Company isolation -->
    <record id="deal_company_rule" model="ir.rule">
      <field name="name">Company: Own Company</field>
      <field name="model_id" ref="model_deal_management"/>
      <field name="domain_force">[("company_id", "=", user.company_id.id)]</field>
      <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    </record>
  </data>
</odoo>
---security-xml-end---

## File 7: security/ir.model.access.csv
---access-csv-start---
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_deal_management_user,deal.management.user,model_deal_management,sales_team.group_sale_salesman,1,1,1,0
access_deal_management_manager,deal.management.manager,model_deal_management,sales_team.group_sale_manager,1,1,1,1
access_deal_line_user,deal.line.user,model_deal_line,sales_team.group_sale_salesman,1,1,1,0
access_deal_line_manager,deal.line.manager,model_deal_line,sales_team.group_sale_manager,1,1,1,1
access_deal_stage_user,deal.stage.user,model_deal_stage,sales_team.group_sale_salesman,1,0,0,0
access_deal_stage_manager,deal.stage.manager,model_deal_stage,sales_team.group_sale_manager,1,1,1,1
---access-csv-end---

## File 8: data/deal_sequence.xml
---sequence-xml-start---
<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <data noupdate="1">
    <record id="seq_deal_reference" model="ir.sequence">
      <field name="name">Deal Reference</field>
      <field name="code">deal.management</field>
      <field name="prefix">DEAL/%(year)s/</field>
      <field name="padding">5</field>
      <field name="number_next_actual">1</field>
    </record>
  </data>
</odoo>
---sequence-xml-end---

## File 9: data/deal_stage_data.xml
---stages-xml-start---
<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <data noupdate="1">
    <record id="stage_draft" model="deal.stage">
      <field name="name">Draft</field>
      <field name="sequence">10</field>
      <field name="color">0</field>
    </record>
    <record id="stage_qualification" model="deal.stage">
      <field name="name">Qualification</field>
      <field name="sequence">20</field>
      <field name="color">2</field>
    </record>
    <record id="stage_proposal" model="deal.stage">
      <field name="name">Proposal</field>
      <field name="sequence">30</field>
      <field name="color">3</field>
    </record>
    <record id="stage_negotiation" model="deal.stage">
      <field name="name">Negotiation</field>
      <field name="sequence">40</field>
      <field name="color">4</field>
    </record>
    <record id="stage_won" model="deal.stage">
      <field name="name">Won</field>
      <field name="sequence">90</field>
      <field name="is_won" eval="True"/>
      <field name="color">10</field>
    </record>
    <record id="stage_lost" model="deal.stage">
      <field name="name">Lost</field>
      <field name="sequence">100</field>
      <field name="is_lost" eval="True"/>
      <field name="color">1</field>
    </record>
  </data>
</odoo>
---stages-xml-end---

## File 10: views/deal_menu.xml
---menu-xml-start---
<?xml version="1.0" encoding="utf-8"?>
<odoo>
  <menuitem id="menu_deal_root" name="Deals"
    sequence="50" parent="sale.sale_menu_root"/>

  <menuitem id="menu_deal_all" name="All Deals"
    parent="menu_deal_root" sequence="10"
    action="deal_management_action"/>

  <menuitem id="menu_deal_pipeline" name="Pipeline"
    parent="menu_deal_root" sequence="20"
    action="deal_management_kanban_action"/>
</odoo>
---menu-xml-end---

## Deployment Steps:

1. Copy this to `/var/lib/odoo/addons/deal_management/`
2. Edit manifest.py with correct paths
3. Create all XML/CSV files
4. Run tests:
   ```bash
   odoo-bin -d scholarixv2 -c /etc/odoo/odoo.conf -i deal_management
   ```
5. Verify in Odoo UI at https://erp.sgctech.ai/app/apps

---

**All files follow deal_report best practices!**
