# -*- coding: utf-8 -*-
from odoo import fields, models


class DealBillLine(models.Model):
    _name = 'deal.bill.line'
    _description = 'Deal Bill Line'

    deal_id = fields.Many2one(
        'deal.report',
        string='Deal',
        required=True,
        ondelete='cascade',
    )
    bill_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        domain="[('move_type', '=', 'in_invoice')]",
    )
    bill_line_id = fields.Many2one('account.move.line', string='Bill Line')
    commission_line_id = fields.Many2one('deal.commission.line', string='Commission Line')
    partner_id = fields.Many2one('res.partner', string='Partner')
    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Text()
    quantity = fields.Float(default=1.0)
    price_unit = fields.Monetary(currency_field='currency_id')
    tax_ids = fields.Many2many('account.tax')
    price_subtotal = fields.Monetary(currency_field='currency_id')
    price_total = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        related='deal_id.currency_id',
        store=True,
    )
    state = fields.Selection(related='bill_id.state', store=True)
