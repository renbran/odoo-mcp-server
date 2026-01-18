# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DealCommissionLine(models.Model):
    _name = 'deal.commission.line'
    _description = 'Deal Commission Line'
    _order = 'id desc'

    deal_id = fields.Many2one(
        'deal.report',
        string='Deal',
        required=True,
        ondelete='cascade',
    )
    commission_partner_id = fields.Many2one(
        'res.partner',
        string='Commission Partner',
        required=True,
    )
    partner_name = fields.Char(related='commission_partner_id.name', store=True)
    commission_type = fields.Selection(
        [('external', 'External'), ('internal', 'Internal')],
        required=True,
        default='external',
    )
    role = fields.Selection(
        [
            ('broker', 'Broker'),
            ('agent1', 'Agent 1'),
            ('agent2', 'Agent 2'),
            ('manager', 'Manager'),
            ('director', 'Director'),
            ('referrer', 'Referrer'),
            ('cashback', 'Cashback'),
            ('other_external', 'Other External'),
        ],
        required=True,
    )
    commission_category = fields.Selection(
        [('external', 'External'), ('internal', 'Internal')],
        default='external',
    )
    calculation_method = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        required=True,
        default='percentage',
    )
    calculation_base = fields.Selection(
        [
            ('unit_price', 'Unit Price / Sales Value'),
            ('order_total_without_tax', 'Order Total (Without Tax)'),
            ('order_total_with_tax', 'Order Total (With Tax)'),
        ],
        default='unit_price',
    )
    commission_rate = fields.Float()
    commission_amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        related='deal_id.currency_id',
        store=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('processed', 'Processed'), ('invoiced', 'Invoiced'), ('paid', 'Paid')],
        default='draft',
    )
    bill_id = fields.Many2one('account.move', string='Vendor Bill')
    bill_line_id = fields.Many2one('account.move.line', string='Bill Line')

    @api.onchange('commission_rate', 'calculation_method', 'calculation_base')
    def _onchange_commission_amount(self):
        for rec in self:
            if not rec.deal_id:
                continue
            base_val = rec.deal_id._get_base_amount(rec.calculation_base)
            if rec.calculation_method == 'fixed':
                rec.commission_amount = rec.commission_rate
            else:
                rec.commission_amount = base_val * (rec.commission_rate / 100.0)
