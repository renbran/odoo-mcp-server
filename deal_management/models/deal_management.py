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
        tracking=True,
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
        tracking=True,
    )

    # === DATES ===
    date_created = fields.Date(
        default=fields.Date.today,
        tracking=True,
        readonly=True,
    )
    date_won = fields.Date(tracking=True, readonly=True)
    date_lost = fields.Date(tracking=True, readonly=True)

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
        tracking=True,
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

    # === NOTES ===
    notes = fields.Text(string='Notes')
    color = fields.Integer(default=0)
    active = fields.Boolean(default=True)

    # === COMPUTED FIELDS ===
    @api.depends('state')
    def _compute_stage(self):
        """Compute stage from state"""
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
                try:
                    record.stage_id = self.env.ref(stage_ref, raise_if_not_found=False)
                except:
                    record.stage_id = False

    @api.depends('amount_total', 'commission_rate')
    def _compute_commission(self):
        """Calculate commission amount"""
        for record in self:
            if record.amount_total and record.commission_rate:
                record.commission_amount = (
                    record.amount_total * record.commission_rate / 100
                )
            else:
                record.commission_amount = 0

    # === CONSTRAINTS ===
    @api.constrains('amount_total')
    def _check_amount_positive(self):
        """Amount must be positive"""
        for record in self:
            if record.amount_total and record.amount_total <= 0:
                raise ValidationError(_("Amount must be positive"))

    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        """Commission rate must be 0-100"""
        for record in self:
            if not (0 <= record.commission_rate <= 100):
                raise ValidationError(
                    _("Commission rate must be between 0 and 100")
                )

    # === WORKFLOW ACTIONS ===
    def action_confirm(self):
        """Move from draft to qualification"""
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_("Only draft deals can be confirmed"))
            record.state = 'qualification'

    def action_move_proposal(self):
        """Move to proposal"""
        for record in self:
            if record.state not in ['qualification']:
                raise ValidationError(
                    _("Only qualified deals can move to proposal")
                )
            record.state = 'proposal'

    def action_move_negotiation(self):
        """Move to negotiation"""
        for record in self:
            if record.state not in ['proposal']:
                raise ValidationError(
                    _("Proposal must be sent before negotiation")
                )
            record.state = 'negotiation'

    def action_won(self):
        """Mark deal as won"""
        for record in self:
            record.state = 'won'
            record.date_won = fields.Date.today()

    def action_lost(self):
        """Mark deal as lost"""
        for record in self:
            record.state = 'lost'
            record.date_lost = fields.Date.today()

    def action_cancel(self):
        """Cancel deal"""
        for record in self:
            record.state = 'cancelled'

    def action_reset(self):
        """Reset to draft"""
        for record in self:
            record.state = 'draft'
            record.date_won = False
            record.date_lost = False

    # === LIFECYCLE HOOKS ===
    @api.model_create_multi
    def create(self, vals_list):
        """Generate reference on creation"""
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                sequence = self.env['ir.sequence'].next_by_code('deal.management')
                vals['reference'] = sequence or _('New')
        return super().create(vals_list)

    def write(self, vals):
        """Track state changes"""
        if 'state' in vals and vals['state'] != self.state:
            for record in self:
                old_state = dict(
                    self._fields['state'].selection
                ).get(record.state, record.state)
                new_state = dict(
                    self._fields['state'].selection
                ).get(vals['state'], vals['state'])
                
        return super().write(vals)
