# -*- coding: utf-8 -*-
from odoo import api, fields, models


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
    
    # Project and Unit from existing fields
    # project_id already exists from deal_tracking_ext
    unit_reference = fields.Char(
        string='Unit',
        help='Unit number or reference'
    )
    
    # Sales Value (computed or from unit_sale_value)
    deal_sales_value = fields.Monetary(
        string='Sales Value',
        compute='_compute_deal_sales_value',
        store=True,
        currency_field='currency_id'
    )
    
    # Commission Rate (from existing primary_commission_percentage)
    deal_commission_rate = fields.Float(
        string='Commission Rate (%)',
        compute='_compute_deal_commission_rate',
        store=True
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
    
    @api.depends('amount_untaxed', 'unit_sale_value')
    def _compute_deal_sales_value(self):
        for record in self:
            # Use unit_sale_value if available, otherwise amount_untaxed
            record.deal_sales_value = record.unit_sale_value or record.amount_untaxed
    
    @api.depends('primary_commission_percentage')
    def _compute_deal_commission_rate(self):
        for record in self:
            record.deal_commission_rate = record.primary_commission_percentage
    
    @api.depends('amount_untaxed', 'amount_tax', 'amount_total')
    def _compute_vat_totals(self):
        for record in self:
            record.total_without_vat = record.amount_untaxed
            record.vat_amount = record.amount_tax
            record.total_with_vat = record.amount_total
