# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date
from dateutil.relativedelta import relativedelta

class DealDashboard(models.TransientModel):
    _name = 'deal.dashboard'
    _description = 'Deal KPI Dashboard'

    period = fields.Selection([
        ('this_month', 'This Month'),
        ('last_month', 'Last Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Year'),
        ('custom', 'Custom')
    ], default='this_month', required=True)

    date_from = fields.Date()
    date_to = fields.Date()

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

    total_deals = fields.Integer(readonly=True)
    total_amount = fields.Monetary(currency_field='currency_id', readonly=True)
    net_amount = fields.Monetary(currency_field='currency_id', readonly=True)
    commission_amount = fields.Monetary(currency_field='currency_id', readonly=True)
    avg_commission_rate = fields.Float(readonly=True)

    state_draft = fields.Integer(string='Draft', readonly=True)
    state_confirmed = fields.Integer(string='Confirmed', readonly=True)
    state_commissioned = fields.Integer(string='Commissioned', readonly=True)
    state_billed = fields.Integer(string='Billed', readonly=True)

    top_customer_id = fields.Many2one('res.partner', readonly=True)
    top_customer_amount = fields.Monetary(currency_field='currency_id', readonly=True)

    @api.onchange('period')
    def _onchange_period(self):
        today = fields.Date.context_today(self)
        if self.period == 'this_month':
            start = date(today.year, today.month, 1)
            end = (start + relativedelta(months=1)) - relativedelta(days=1)
            self.date_from, self.date_to = start, end
        elif self.period == 'last_month':
            start = (date(today.year, today.month, 1) - relativedelta(months=1))
            end = (date(today.year, today.month, 1) - relativedelta(days=1))
            self.date_from, self.date_to = start, end
        elif self.period == 'this_quarter':
            quarter = ((today.month - 1) // 3) + 1
            start_month = (quarter - 1) * 3 + 1
            start = date(today.year, start_month, 1)
            end = (start + relativedelta(months=3)) - relativedelta(days=1)
            self.date_from, self.date_to = start, end
        elif self.period == 'this_year':
            start = date(today.year, 1, 1)
            end = date(today.year, 12, 31)
            self.date_from, self.date_to = start, end
        else:
            # custom: leave dates as-is
            return

    def _domain(self):
        domain = []
        if self.date_from:
            domain.append(('date', '>=', self.date_from))
        if self.date_to:
            domain.append(('date', '<=', self.date_to))
        return domain

    def action_refresh(self):
        domain = self._domain()
        DealReport = self.env['deal.report']
        records = DealReport.search(domain)

        self.total_deals = len(records)
        self.total_amount = sum(records.mapped('total_amount'))
        self.net_amount = sum(records.mapped('net_amount'))
        self.commission_amount = sum(records.mapped('commission_amount'))
        self.avg_commission_rate = self.total_deals and (sum(records.mapped('commission_rate')) / self.total_deals) or 0.0

        grouped_states = DealReport.read_group(domain, ['id'], ['state'])
        counts = {g['state']: g['state_count'] for g in grouped_states}
        self.state_draft = counts.get('draft', 0)
        self.state_confirmed = counts.get('confirmed', 0)
        self.state_commissioned = counts.get('commissioned', 0)
        self.state_billed = counts.get('billed', 0)

        top = DealReport.read_group(domain, ['total_amount:sum'], ['partner_id'], limit=1, orderby='total_amount_sum desc')
        if top:
            self.top_customer_id = top[0].get('partner_id') and top[0]['partner_id'][0]
            self.top_customer_amount = top[0].get('total_amount_sum') or 0.0
        else:
            self.top_customer_id = False
            self.top_customer_amount = 0.0
        return True

    def action_open_analytics(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Deal Analytics'),
            'res_model': 'deal.report',
            'view_mode': 'graph,pivot,kanban,tree',
            'views': [
                (self.env.ref('deal_report.view_deal_report_graph').id, 'graph'),
                (self.env.ref('deal_report.view_deal_report_pivot').id, 'pivot'),
                (self.env.ref('deal_report.view_deal_report_kanban').id, 'kanban'),
                (self.env.ref('deal_report.view_deal_report_tree').id, 'tree'),
            ],
            'domain': self._domain(),
            'target': 'current',
        }
