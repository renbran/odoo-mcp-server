# -*- coding: utf-8 -*-
from odoo import fields, models

class DealBillLine(models.Model):
    _name = 'deal.bill.line'
    _description = 'Deal Bill Line'

    deal_report_id = fields.Many2one('deal.report', string='Deal Report', required=True, ondelete='cascade')
    move_id = fields.Many2one('account.move', string='Invoice', required=True)
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='deal_report_id.currency_id', store=True)
