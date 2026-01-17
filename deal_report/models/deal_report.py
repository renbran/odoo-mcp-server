# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class DealReport(models.Model):
    _name = 'deal.report'
    _description = 'Deal Report'
    _order = 'date desc'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Deal reference must be unique.')
    ]

    name = fields.Char(string='Deal Reference', required=True, copy=False, default=lambda self: _('New'), tracking=True)
    date = fields.Date(string='Deal Date', required=True, default=fields.Date.context_today)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', related='sale_order_id.partner_id', store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    # Financials
    total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id', compute='_compute_financials', store=True)
    vat_rate = fields.Float(string='VAT %', compute='_compute_financials', store=True)
    vat_amount = fields.Monetary(string='VAT Amount', currency_field='currency_id', compute='_compute_financials', store=True)
    net_amount = fields.Monetary(string='Net Amount', currency_field='currency_id', compute='_compute_financials', store=True)

    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id', store=True)

    # Commission
    commission_rate = fields.Float(string='Commission %', compute='_compute_commission', store=True, tracking=True)
    commission_amount = fields.Monetary(string='Commission Amount', currency_field='currency_id', compute='_compute_commission', store=True, tracking=True)
    commission_line_ids = fields.One2many('deal.commission.line', 'deal_report_id', string='Commission Lines')

    # Billing
    bill_line_ids = fields.One2many('deal.bill.line', 'deal_report_id', string='Bill Lines')
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    auto_post_invoice = fields.Boolean(string='Auto Post Invoice')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('commissioned', 'Commissioned'),
        ('billed', 'Billed'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_name = self.env['ir.sequence'].next_by_code('deal.report')
            if not seq_name:
                raise UserError(_('Sequence for code deal.report not found. Install data files.'))
            vals['name'] = seq_name
        return super().create(vals)

    @api.depends('sale_order_id.amount_total', 'sale_order_id.amount_tax', 'sale_order_id.amount_untaxed')
    def _compute_financials(self):
        for rec in self:
            rec.total_amount = rec.sale_order_id.amount_total
            # Derive VAT rate from order lines taxes if possible
            tax_rate = 0.0
            tax_amount = rec.sale_order_id.amount_tax
            untaxed = rec.sale_order_id.amount_untaxed
            if untaxed:
                tax_rate = (tax_amount / untaxed) * 100.0
            rec.vat_rate = tax_rate
            rec.vat_amount = tax_amount
            rec.net_amount = rec.sale_order_id.amount_total - tax_amount

    @api.depends('sale_order_id')
    def _compute_commission(self):
        for rec in self:
            # Commission rate can be derived from salesperson or company policy; default 5%
            rate = rec.sale_order_id.user_id and getattr(rec.sale_order_id.user_id, 'commission_rate', 5.0) or 5.0
            rec.commission_rate = rate
            rec.commission_amount = (rec.net_amount or 0.0) * (rate / 100.0)

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft reports can be confirmed.'))
            if not rec.sale_order_id:
                raise UserError(_('Sale Order is required to confirm.'))
            rec.state = 'confirmed'
        return True

    def action_generate_commissions(self):
        for rec in self:
            if rec.state not in ('confirmed', 'commissioned'):
                raise UserError(_('Confirm the report before generating commissions.'))
            if not rec.commission_line_ids:
                self._create_commission_lines(rec)
            rec.state = 'commissioned'
        return True

    def _create_commission_lines(self, rec):
        # Simple example: single commission line based on computed commission amount
        self.env['deal.commission.line'].create({
            'deal_report_id': rec.id,
            'name': _('Commission for %s') % rec.name,
            'rate': rec.commission_rate,
            'amount': rec.commission_amount,
        })

    def action_process_bills(self):
        for rec in self:
            if rec.state != 'commissioned':
                raise UserError(_('Generate commissions before processing bills.'))
            # Avoid duplicate billing
            if not rec.bill_line_ids:
                self._create_bill_lines(rec)
            rec.state = 'billed'
        return True

    def _create_bill_lines(self, rec):
        product = self.env.ref('deal_report.product_commission', raise_if_not_found=False)
        if not product:
            raise UserError(_('Commission product not found. Install data files.'))
        # create an invoice with a single line for total commission
        move_vals = {
            'move_type': 'out_invoice',
            'partner_id': rec.partner_id.id,
            'invoice_date': fields.Date.context_today(self),
            'currency_id': rec.currency_id.id,
            'company_id': rec.company_id.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'name': _('Commission for %s') % rec.name,
                'quantity': 1.0,
                'price_unit': rec.commission_amount,
                'tax_ids': []
            })]
        }
        move = self.env['account.move'].create(move_vals)
        if rec.auto_post_invoice:
            move.action_post()
        self.env['deal.bill.line'].create({
            'deal_report_id': rec.id,
            'move_id': move.id,
            'amount': rec.commission_amount,
        })

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
        return True

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
        return True

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.bill_line_ids)

    def action_view_invoices(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', 'in', self.bill_line_ids.mapped('move_id').ids)]
        return action
