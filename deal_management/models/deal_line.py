# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DealLine(models.Model):
    _name = 'deal.line'
    _description = 'Deal Line'
    _order = 'sequence'

    deal_id = fields.Many2one(
        'deal.management',
        string='Deal',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    sequence = fields.Integer(default=1)
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
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
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='deal_id.company_id',
        store=True,
    )

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        """Calculate line total"""
        for record in self:
            record.amount_total = record.quantity * record.unit_price
