# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DealReport(models.Model):
    _name = 'deal.report'
    _description = 'Deal Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'booking_date desc, id desc'

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Deal reference must be unique.'),
    ]

    def _default_currency(self):
        return self.env.company.currency_id

    name = fields.Char(
        string='Deal Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True,
    )
    sales_type = fields.Selection(
        [
            ('primary', 'Primary'),
            ('secondary', 'Secondary'),
            ('rental', 'Rental'),
            ('exclusive', 'Exclusive'),
        ],
        string='Sales Type',
        required=True,
        default='primary',
        tracking=True,
    )
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
    booking_date = fields.Date(required=True, tracking=True)
    estimated_invoice_date = fields.Date()

    primary_buyer_id = fields.Many2one(
        'res.partner',
        string='Primary Buyer',
        domain="[('is_company', '=', False)]",
        tracking=True,
    )
    secondary_buyer_id = fields.Many2one(
        'res.partner',
        string='Secondary Buyer',
        domain="[('is_company', '=', False)]",
        tracking=True,
    )
    customer_ids = fields.Many2many(
        'res.partner',
        'deal_report_partner_rel',
        'deal_id',
        'partner_id',
        string='Customers',
    )

    project_id = fields.Many2one('project.project', string='Project', required=True)
    unit_id = fields.Many2one('product.product', string='Unit', required=True)
    unit_type = fields.Selection(
        [
            ('apartment', 'Apartment'),
            ('villa', 'Villa'),
            ('townhouse', 'Townhouse'),
            ('plot', 'Plot'),
            ('other', 'Other'),
        ],
        string='Unit Type',
    )

    sales_value = fields.Monetary(
        string='Sales Value',
        required=True,
        tracking=True,
        currency_field='currency_id',
    )
    vat_rate = fields.Float(string='VAT Rate (%)', default=5.0)
    vat_amount = fields.Monetary(
        string='VAT Amount',
        compute='_compute_vat_totals',
        store=True,
        currency_field='currency_id',
    )
    total_without_vat = fields.Monetary(
        string='Total (w/o VAT)',
        compute='_compute_vat_totals',
        store=True,
        currency_field='currency_id',
    )
    total_with_vat = fields.Monetary(
        string='Total (with VAT)',
        compute='_compute_vat_totals',
        store=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=_default_currency,
        required=True,
    )

    kyc_document_ids = fields.Many2many(
        'ir.attachment',
        'deal_report_kyc_rel',
        'deal_id',
        'attachment_id',
        string='KYC Documents',
    )
    booking_form_ids = fields.Many2many(
        'ir.attachment',
        'deal_report_booking_rel',
        'deal_id',
        'attachment_id',
        string='Booking Forms',
    )
    spa_document_ids = fields.Many2many(
        'ir.attachment',
        'deal_report_spa_rel',
        'deal_id',
        'attachment_id',
        string='SPA Documents',
    )
    passport_ids = fields.Many2many(
        'ir.attachment',
        'deal_report_passport_rel',
        'deal_id',
        'attachment_id',
        string='Passports',
    )
    document_ids = fields.Many2many(
        'ir.attachment',
        'deal_report_doc_rel',
        'deal_id',
        'attachment_id',
        string='Other Documents',
    )

    invoice_count = fields.Integer(compute='_compute_invoice_count', store=True)
    commission_count = fields.Integer(compute='_compute_commission_count', store=True)
    bill_count = fields.Integer(compute='_compute_bill_count', store=True)

    commission_line_ids = fields.One2many('deal.commission.line', 'deal_id')
    bill_line_ids = fields.One2many('deal.bill.line', 'deal_id')

    # External commissions
    broker_partner_id = fields.Many2one('res.partner', string='Broker')
    broker_commission_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage',
    )
    broker_calculation_base = fields.Selection(
        [
            ('unit_price', 'Unit Price / Sales Value'),
            ('order_total_without_tax', 'Order Total (Without Tax)'),
            ('order_total_with_tax', 'Order Total (With Tax)'),
        ],
        default='unit_price',
    )
    broker_rate = fields.Float()
    broker_amount = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)

    referrer_partner_id = fields.Many2one('res.partner', string='Referrer')
    referrer_commission_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage',
    )
    referrer_calculation_base = fields.Selection(
        [
            ('unit_price', 'Unit Price / Sales Value'),
            ('order_total_without_tax', 'Order Total (Without Tax)'),
            ('order_total_with_tax', 'Order Total (With Tax)'),
        ],
        default='unit_price',
    )
    referrer_rate = fields.Float()
    referrer_amount = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)

    cashback_partner_id = fields.Many2one('res.partner', string='Cashback Partner')
    cashback_commission_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage',
    )
    cashback_calculation_base = fields.Selection(
        [
            ('unit_price', 'Unit Price / Sales Value'),
            ('order_total_without_tax', 'Order Total (Without Tax)'),
            ('order_total_with_tax', 'Order Total (With Tax)'),
        ],
        default='unit_price',
    )
    cashback_rate = fields.Float()
    cashback_amount = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)

    other_external_partner_id = fields.Many2one('res.partner', string='Other External Partner')
    other_external_commission_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage',
    )
    other_external_calculation_base = fields.Selection(
        [
            ('unit_price', 'Unit Price / Sales Value'),
            ('order_total_without_tax', 'Order Total (Without Tax)'),
            ('order_total_with_tax', 'Order Total (With Tax)'),
        ],
        default='unit_price',
    )
    other_external_rate = fields.Float()
    other_external_amount = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)

    # Internal commissions
    agent1_partner_id = fields.Many2one('res.partner', string='Agent 1')
    agent1_commission_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage',
    )
    agent1_calculation_base = fields.Selection(
        [
            ('unit_price', 'Unit Price / Sales Value'),
            ('order_total_without_tax', 'Order Total (Without Tax)'),
            ('order_total_with_tax', 'Order Total (With Tax)'),
        ],
        default='order_total_without_tax',
    )
    agent1_rate = fields.Float()
    agent1_amount = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)

    agent2_partner_id = fields.Many2one('res.partner', string='Agent 2')
    agent2_commission_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage',
    )
    agent2_calculation_base = fields.Selection(
        [
            ('unit_price', 'Unit Price / Sales Value'),
            ('order_total_without_tax', 'Order Total (Without Tax)'),
            ('order_total_with_tax', 'Order Total (With Tax)'),
        ],
        default='order_total_without_tax',
    )
    agent2_rate = fields.Float()
    agent2_amount = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)

    manager_partner_id = fields.Many2one('res.partner', string='Manager')
    manager_commission_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage',
    )
    manager_calculation_base = fields.Selection(
        [
            ('unit_price', 'Unit Price / Sales Value'),
            ('order_total_without_tax', 'Order Total (Without Tax)'),
            ('order_total_with_tax', 'Order Total (With Tax)'),
        ],
        default='order_total_without_tax',
    )
    manager_rate = fields.Float()
    manager_amount = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)

    director_partner_id = fields.Many2one('res.partner', string='Director')
    director_commission_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage',
    )
    director_calculation_base = fields.Selection(
        [
            ('unit_price', 'Unit Price / Sales Value'),
            ('order_total_without_tax', 'Order Total (Without Tax)'),
            ('order_total_with_tax', 'Order Total (With Tax)'),
        ],
        default='order_total_without_tax',
    )
    director_rate = fields.Float()
    director_amount = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)

    company_share = fields.Monetary(currency_field='currency_id')
    net_company_share = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)
    total_commission_amount = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)
    total_external_commission = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)
    total_internal_commission = fields.Monetary(currency_field='currency_id', compute='_compute_commissions', store=True)
    commission_status = fields.Char()
    commission_processed = fields.Boolean(default=False)
    is_fully_invoiced = fields.Boolean(default=False)
    has_posted_invoices = fields.Boolean(default=False)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('deal.report')
            if not seq:
                raise UserError(
                    _('Sequence for code deal.report not found. Install data files.')
                )
            vals['name'] = seq
        return super().create(vals)

    @api.depends('sales_value', 'vat_rate')
    def _compute_vat_totals(self):
        for rec in self:
            base = rec.sales_value or 0.0
            rec.total_without_vat = base
            rec.vat_amount = base * (rec.vat_rate or 0.0) / 100.0
            rec.total_with_vat = base + rec.vat_amount

    def _get_base_amount(self, base_key):
        self.ensure_one()
        if base_key == 'order_total_without_tax':
            return self.total_without_vat or 0.0
        if base_key == 'order_total_with_tax':
            return self.total_with_vat or 0.0
        return self.sales_value or 0.0

    def _compute_comm_value(self, rate, ctype, base_val):
        if not rate:
            return 0.0
        if ctype == 'fixed':
            return rate
        return base_val * (rate / 100.0)

    @api.depends(
        'sales_value',
        'total_without_vat',
        'total_with_vat',
        'broker_rate', 'referrer_rate', 'cashback_rate', 'other_external_rate',
        'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate',
        'broker_commission_type', 'referrer_commission_type',
        'cashback_commission_type', 'other_external_commission_type',
        'agent1_commission_type', 'agent2_commission_type',
        'manager_commission_type', 'director_commission_type',
        'broker_calculation_base', 'referrer_calculation_base',
        'cashback_calculation_base', 'other_external_calculation_base',
        'agent1_calculation_base', 'agent2_calculation_base',
        'manager_calculation_base', 'director_calculation_base',
    )
    def _compute_commissions(self):
        for rec in self:
            def compute_partner(rate, ctype, base_key):
                base_val = rec._get_base_amount(base_key)
                return rec._compute_comm_value(rate, ctype, base_val)

            rec.broker_amount = compute_partner(
                rec.broker_rate, rec.broker_commission_type, rec.broker_calculation_base
            )
            rec.referrer_amount = compute_partner(
                rec.referrer_rate, rec.referrer_commission_type, rec.referrer_calculation_base
            )
            rec.cashback_amount = compute_partner(
                rec.cashback_rate, rec.cashback_commission_type, rec.cashback_calculation_base
            )
            rec.other_external_amount = compute_partner(
                rec.other_external_rate,
                rec.other_external_commission_type,
                rec.other_external_calculation_base,
            )
            rec.agent1_amount = compute_partner(
                rec.agent1_rate, rec.agent1_commission_type, rec.agent1_calculation_base
            )
            rec.agent2_amount = compute_partner(
                rec.agent2_rate, rec.agent2_commission_type, rec.agent2_calculation_base
            )
            rec.manager_amount = compute_partner(
                rec.manager_rate, rec.manager_commission_type, rec.manager_calculation_base
            )
            rec.director_amount = compute_partner(
                rec.director_rate, rec.director_commission_type, rec.director_calculation_base
            )

            rec.total_external_commission = sum([
                rec.broker_amount,
                rec.referrer_amount,
                rec.cashback_amount,
                rec.other_external_amount,
            ])
            rec.total_internal_commission = sum([
                rec.agent1_amount,
                rec.agent2_amount,
                rec.manager_amount,
                rec.director_amount,
            ])
            rec.total_commission_amount = (
                rec.total_external_commission + rec.total_internal_commission
            )
            rec.net_company_share = (rec.sales_value or 0.0) - rec.total_commission_amount
            rec.company_share = rec.net_company_share
            rec.commission_status = 'Processed' if rec.commission_processed else 'Pending'

    @api.depends('commission_line_ids')
    def _compute_commission_count(self):
        for rec in self:
            rec.commission_count = len(rec.commission_line_ids)

    @api.depends('commission_line_ids.bill_id')
    def _compute_bill_count(self):
        for rec in self:
            rec.bill_count = len(rec.commission_line_ids.mapped('bill_id'))

    @api.depends('name')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = self.env['account.move'].search_count([
                ('invoice_origin', '=', rec.name),
                ('move_type', '=', 'out_invoice'),
            ])

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft deals can be confirmed.'))
            if not rec.primary_buyer_id or not rec.sales_value:
                raise UserError(
                    _('Primary Buyer and Sales Value are required to confirm the deal.')
                )
            rec.state = 'confirmed'
            rec.action_generate_commission_lines()
        return True

    def action_generate_commission_lines(self):
        for rec in self:
            rec.ensure_one()
            rec.commission_line_ids.unlink()
            commission_configs = [
                {
                    'partner': rec.broker_partner_id,
                    'role': 'broker',
                    'type': 'external',
                    'category': 'external',
                    'method': rec.broker_commission_type,
                    'base': rec.broker_calculation_base,
                    'rate': rec.broker_rate,
                    'amount': rec.broker_amount,
                },
                {
                    'partner': rec.referrer_partner_id,
                    'role': 'referrer',
                    'type': 'external',
                    'category': 'external',
                    'method': rec.referrer_commission_type,
                    'base': rec.referrer_calculation_base,
                    'rate': rec.referrer_rate,
                    'amount': rec.referrer_amount,
                },
                {
                    'partner': rec.cashback_partner_id,
                    'role': 'cashback',
                    'type': 'external',
                    'category': 'external',
                    'method': rec.cashback_commission_type,
                    'base': rec.cashback_calculation_base,
                    'rate': rec.cashback_rate,
                    'amount': rec.cashback_amount,
                },
                {
                    'partner': rec.other_external_partner_id,
                    'role': 'other_external',
                    'type': 'external',
                    'category': 'external',
                    'method': rec.other_external_commission_type,
                    'base': rec.other_external_calculation_base,
                    'rate': rec.other_external_rate,
                    'amount': rec.other_external_amount,
                },
                {
                    'partner': rec.agent1_partner_id,
                    'role': 'agent1',
                    'type': 'internal',
                    'category': 'internal',
                    'method': rec.agent1_commission_type,
                    'base': rec.agent1_calculation_base,
                    'rate': rec.agent1_rate,
                    'amount': rec.agent1_amount,
                },
                {
                    'partner': rec.agent2_partner_id,
                    'role': 'agent2',
                    'type': 'internal',
                    'category': 'internal',
                    'method': rec.agent2_commission_type,
                    'base': rec.agent2_calculation_base,
                    'rate': rec.agent2_rate,
                    'amount': rec.agent2_amount,
                },
                {
                    'partner': rec.manager_partner_id,
                    'role': 'manager',
                    'type': 'internal',
                    'category': 'internal',
                    'method': rec.manager_commission_type,
                    'base': rec.manager_calculation_base,
                    'rate': rec.manager_rate,
                    'amount': rec.manager_amount,
                },
                {
                    'partner': rec.director_partner_id,
                    'role': 'director',
                    'type': 'internal',
                    'category': 'internal',
                    'method': rec.director_commission_type,
                    'base': rec.director_calculation_base,
                    'rate': rec.director_rate,
                    'amount': rec.director_amount,
                },
            ]

            for config in commission_configs:
                if not config['partner']:
                    continue
                self.env['deal.commission.line'].create({
                    'deal_id': rec.id,
                    'commission_partner_id': config['partner'].id,
                    'role': config['role'],
                    'commission_type': config['type'],
                    'commission_category': config['category'],
                    'calculation_method': config['method'],
                    'calculation_base': config['base'],
                    'commission_rate': config['rate'],
                    'commission_amount': config['amount'],
                    'state': 'draft',
                })
            rec.state = 'commissioned'
        return True

    def action_process_commissions_to_bills(self):
        for rec in self:
            rec.ensure_one()
            if not rec.commission_line_ids:
                raise UserError(
                    _('No commission lines to process. Please generate commission lines first.')
                )
            partner_map = {}
            for line in rec.commission_line_ids.filtered(lambda l: l.state == 'draft'):
                partner_map.setdefault(line.commission_partner_id, []).append(line)

            created_bills = self.env['account.move']
            commission_product = self.env.ref(
                'deal_report.product_commission_service', raise_if_not_found=False
            )
            if not commission_product:
                commission_product = self.env['product.product'].create({
                    'name': 'Commission Service',
                    'type': 'service',
                    'purchase_ok': True,
                    'sale_ok': False,
                })

            for partner, comm_lines in partner_map.items():
                bill_vals = {
                    'move_type': 'in_invoice',
                    'partner_id': partner.id,
                    'invoice_date': fields.Date.context_today(self),
                    'invoice_origin': rec.name,
                    'ref': 'Commission - %s' % rec.name,
                    'invoice_line_ids': [],
                }

                for comm_line in comm_lines:
                    bill_vals['invoice_line_ids'].append((0, 0, {
                        'product_id': commission_product.id,
                        'name': 'Commission - %s - %s' % (comm_line.role.upper(), rec.name),
                        'quantity': 1.0,
                        'price_unit': comm_line.commission_amount,
                        'tax_ids': [(6, 0, [])],
                    }))

                bill = self.env['account.move'].create(bill_vals)
                created_bills |= bill

                for idx, comm_line in enumerate(comm_lines):
                    invoice_line = bill.invoice_line_ids[idx]
                    comm_line.write({
                        'bill_id': bill.id,
                        'bill_line_id': invoice_line.id,
                        'state': 'processed',
                    })
                    self.env['deal.bill.line'].create({
                        'deal_id': rec.id,
                        'bill_id': bill.id,
                        'bill_line_id': invoice_line.id,
                        'commission_line_id': comm_line.id,
                        'partner_id': partner.id,
                        'product_id': commission_product.id,
                        'description': invoice_line.name,
                        'quantity': 1.0,
                        'price_unit': comm_line.commission_amount,
                        'price_subtotal': comm_line.commission_amount,
                        'price_total': comm_line.commission_amount,
                    })

            rec.write({
                'commission_processed': True,
                'state': 'commissioned',
            })

            return {
                'name': _('Commission Bills'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', created_bills.ids)],
                'context': {'create': False},
            }

    def action_view_invoices(self):
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('invoice_origin', '=', self.name),
            ('move_type', '=', 'out_invoice'),
        ])
        return {
            'name': _('Customer Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoices.ids)],
            'context': {'default_move_type': 'out_invoice'},
        }

    def action_view_commissions(self):
        self.ensure_one()
        return {
            'name': _('Commission Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'deal.commission.line',
            'view_mode': 'tree,form',
            'domain': [('deal_id', '=', self.id)],
            'context': {'default_deal_id': self.id},
        }

    def action_view_bills(self):
        self.ensure_one()
        bills = self.commission_line_ids.mapped('bill_id')
        return {
            'name': _('Commission Bills'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bills.ids)],
            'context': {'default_move_type': 'in_invoice'},
        }

    def action_view_documents(self):
        self.ensure_one()
        all_docs = (
            self.kyc_document_ids
            | self.booking_form_ids
            | self.spa_document_ids
            | self.passport_ids
            | self.document_ids
        )
        return {
            'name': _('Deal Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', all_docs.ids)],
            'context': {
                'default_res_model': 'deal.report',
                'default_res_id': self.id,
            },
        }

    def action_set_invoiced(self):
        for rec in self:
            invoice_count = self.env['account.move'].search_count([
                ('invoice_origin', '=', rec.name),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ])
            if not invoice_count:
                raise UserError(
                    _('Cannot set to Invoiced. No posted customer invoice found.')
                )
            rec.write({
                'state': 'invoiced',
                'is_fully_invoiced': True,
                'has_posted_invoices': True,
            })
        return True

    def action_set_done(self):
        for rec in self:
            if not rec.commission_processed:
                raise UserError(_('Please process commissions before marking as done.'))
            if not rec.is_fully_invoiced:
                raise UserError(_('Deal must be fully invoiced before marking as done.'))
            rec.state = 'done'
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('Cannot cancel a completed deal.'))
            rec.state = 'cancelled'
        return True

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.commission_processed = False
            rec.is_fully_invoiced = False
            rec.has_posted_invoices = False
            rec.commission_line_ids.unlink()
        return True
