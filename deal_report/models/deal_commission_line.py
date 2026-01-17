# -*- coding: utf-8 -*-
from odoo import api, fields, models

class DealCommissionLine(models.Model):
    _name = 'deal.commission.line'
    _description = 'Deal Commission Line'
    _order = 'id desc'

    deal_report_id = fields.Many2one('deal.report', string='Deal Report', required=True, ondelete='cascade')
    name = fields.Char(string='Description', required=True)
    rate = fields.Float(string='Commission %', required=True)
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='deal_report_id.currency_id', store=True)
