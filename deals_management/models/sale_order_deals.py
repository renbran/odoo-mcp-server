# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderDeals(models.Model):
    _inherit = 'sale.order'

    # Sales Type Selection
    sales_type = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('exclusive', 'Exclusive'),
        ('rental', 'Rental'),
    ], string='Sales Type', default='primary', tracking=True)
    
    # Buyer Fields
    primary_buyer_id = fields.Many2one(
        'res.partner',
        string='Primary Buyer',
        domain="[('is_company', '=', False)]",
        tracking=True
    )
    secondary_buyer_id = fields.Many2one(
        'res.partner',
        string='Secondary Buyer',
        domain="[('is_company', '=', False)]",
        tracking=True
    )
    
    # Project and Unit
    unit_reference = fields.Char(
        string='Unit',
        help='Unit number or reference',
        tracking=True
    )
    
    # Date Fields
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
        help='Date when the deal was booked'
    )
    estimated_invoice_date = fields.Date(
        string='Estimated Invoice Date',
        tracking=True,
        help='Expected date for invoice generation'
    )
    
    # Sales Value (computed or from unit_sale_value)
    deal_sales_value = fields.Monetary(
        string='Sales Value',
        compute='_compute_deal_sales_value',
        store=True,
        currency_field='currency_id'
    )
    
    # Commission Rate (percentage)
    deal_commission_rate = fields.Float(
        string='Commission Rate (%)',
        default=0.0,
        help='Commission percentage for this deal'
    )
    
    # VAT and Total calculations
    vat_amount = fields.Monetary(
        string='VAT Amount',
        compute='_compute_vat_totals',
        store=True,
        currency_field='currency_id'
    )
    total_without_vat = fields.Monetary(
        string='Total (w/o VAT)',
        compute='_compute_vat_totals',
        store=True,
        currency_field='currency_id'
    )
    total_with_vat = fields.Monetary(
        string='Total (with VAT)',
        compute='_compute_vat_totals',
        store=True,
        currency_field='currency_id'
    )
    
    # Document Attachments
    kyc_document_ids = fields.Many2many(
        'ir.attachment',
        'deal_kyc_attachment_rel',
        'deal_id',
        'attachment_id',
        string='KYC Documents',
        help='Upload KYC documents for buyers'
    )
    kyc_document_count = fields.Integer(
        string='KYC Documents',
        compute='_compute_document_counts'
    )
    
    booking_form_ids = fields.Many2many(
        'ir.attachment',
        'deal_booking_form_attachment_rel',
        'deal_id',
        'attachment_id',
        string='Booking Forms / SPA',
        help='Upload booking forms or Sales and Purchase Agreements'
    )
    booking_form_count = fields.Integer(
        string='Booking Forms',
        compute='_compute_document_counts'
    )
    
    passport_ids = fields.Many2many(
        'ir.attachment',
        'deal_passport_attachment_rel',
        'deal_id',
        'attachment_id',
        string='Passports',
        help='Upload passport copies of buyers'
    )
    passport_count = fields.Integer(
        string='Passports',
        compute='_compute_document_counts'
    )
    
    # Smart Button Counts
    commission_count = fields.Integer(
        string='Commissions',
        compute='_compute_commission_count'
    )
    bill_count = fields.Integer(
        string='Bills',
        compute='_compute_bill_count'
    )
    
    @api.depends('amount_untaxed')
    def _compute_deal_sales_value(self):
        for record in self:
            record.deal_sales_value = record.amount_untaxed
    
    @api.depends('amount_untaxed', 'amount_tax', 'amount_total')
    def _compute_vat_totals(self):
        for record in self:
            record.total_without_vat = record.amount_untaxed
            record.vat_amount = record.amount_tax
            record.total_with_vat = record.amount_total
    
    @api.depends('kyc_document_ids', 'booking_form_ids', 'passport_ids')
    def _compute_document_counts(self):
        for record in self:
            record.kyc_document_count = len(record.kyc_document_ids)
            record.booking_form_count = len(record.booking_form_ids)
            record.passport_count = len(record.passport_ids)
    
    @api.depends('id')
    def _compute_commission_count(self):
        for record in self:
            # Count commission lines related to this deal
            record.commission_count = self.env['commission.line'].search_count([
                ('sale_order_id', '=', record.id)
            ])
    
    @api.depends('id')
    def _compute_bill_count(self):
        for record in self:
            # Count vendor bills related to this deal's commissions
            commission_lines = self.env['commission.line'].search([
                ('sale_order_id', '=', record.id)
            ])
            bill_ids = commission_lines.mapped('bill_id').ids
            record.bill_count = len(set(bill_ids))
    
    # Smart Button Actions
    def action_view_invoices(self):
        """Open invoices related to this deal"""
        self.ensure_one()
        invoices = self.invoice_ids
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def action_view_commissions(self):
        """Open commissions related to this deal"""
        self.ensure_one()
        action = self.env.ref('commission_ax.action_commission_lines').read()[0]
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {
            'default_sale_order_id': self.id,
        }
        return action
    
    def action_view_bills(self):
        """Open vendor bills related to this deal's commissions"""
        self.ensure_one()
        commission_lines = self.env['commission.line'].search([
            ('sale_order_id', '=', self.id)
        ])
        bill_ids = commission_lines.mapped('bill_id').ids
        
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        if len(bill_ids) > 1:
            action['domain'] = [('id', 'in', bill_ids)]
        elif len(bill_ids) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = bill_ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    def action_view_kyc_documents(self):
        """Open KYC documents"""
        self.ensure_one()
        return {
            'name': _('KYC Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.kyc_document_ids.ids)],
            'context': {
                'default_res_model': 'sale.order',
                'default_res_id': self.id,
            }
        }
    
    def action_view_booking_forms(self):
        """Open booking forms/SPA"""
        self.ensure_one()
        return {
            'name': _('Booking Forms / SPA'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.booking_form_ids.ids)],
            'context': {
                'default_res_model': 'sale.order',
                'default_res_id': self.id,
            }
        }
    
    def action_view_passports(self):
        """Open passport documents"""
        self.ensure_one()
        return {
            'name': _('Passports'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.passport_ids.ids)],
            'context': {
                'default_res_model': 'sale.order',
                'default_res_id': self.id,
            }
        }


class CommissionLine(models.Model):
    """Extend commission line to support direct bill creation"""
    _inherit = 'commission.line'
    
    bill_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        readonly=True,
        copy=False,
        help='Vendor bill created for this commission'
    )
    
    def action_create_bill(self):
        """Create vendor bill directly instead of purchase order"""
        self.ensure_one()
        
        if self.bill_id:
            raise UserError(_('Bill already created for this commission.'))
        
        if not self.partner_id:
            raise UserError(_('Please set a partner for this commission line.'))
        
        # Create vendor bill
        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f'Commission: {self.sale_order_id.name if self.sale_order_id else "N/A"}',
                'quantity': 1,
                'price_unit': self.commission_amount,
                'account_id': self._get_commission_expense_account().id,
            })],
        }
        
        bill = self.env['account.move'].create(bill_vals)
        self.bill_id = bill.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Bill'),
            'res_model': 'account.move',
            'res_id': bill.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _get_commission_expense_account(self):
        """Get the commission expense account for the current company."""
        company = self.env.company

        account = self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('deprecated', '=', False),
            ('account_type', '=', 'expense'),
            ('name', 'ilike', 'commission'),
        ], limit=1, order='code')

        if not account:
            account = self.env['account.account'].search([
                ('company_id', '=', company.id),
                ('deprecated', '=', False),
                ('account_type', '=', 'expense'),
            ], limit=1, order='code')

        if not account:
            raise UserError(_('Please configure an expense account for commissions in company %s.') % company.display_name)

        return account
    
    def action_view_bill(self):
        """Open related vendor bill"""
        self.ensure_one()
        if not self.bill_id:
            raise UserError(_('No bill created for this commission yet.'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Bill'),
            'res_model': 'account.move',
            'res_id': self.bill_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class SaleOrderDealsConstraints(models.Model):
    _inherit = 'sale.order'

    @api.constrains('deal_commission_rate')
    def _check_deal_commission_rate(self):
        for record in self:
            if record.deal_commission_rate < 0:
                raise UserError(_('Commission rate cannot be negative.'))
            if record.deal_commission_rate > 100:
                raise UserError(_('Commission rate cannot exceed 100%.'))
