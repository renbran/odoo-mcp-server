# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderDealTracking(models.Model):
    _inherit = 'sale.order'

    buyer_name = fields.Char(
        string="Buyer Name",
        compute="_compute_buyer_name",
        store=True,
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        help="Optional project linked to this deal.",
    )
    project_name = fields.Char(
        string="Project Name",
        compute="_compute_project_name",
        store=True,
    )
    unit_sale_value = fields.Monetary(
        string="Unit Sale Value",
        compute="_compute_unit_sale_value",
        store=True,
        currency_field='currency_id',
    )
    primary_commission_percentage = fields.Float(
        string="Primary Commission %",
        compute="_compute_primary_commission_percentage",
        store=True,
    )
    deal_summary_html = fields.Html(
        string="Deal Summary",
        compute="_compute_deal_summary_html",
    )

    @api.depends('partner_id', 'partner_id.name')
    def _compute_buyer_name(self):
        for record in self:
            record.buyer_name = record.partner_id.name if record.partner_id else ''

    @api.depends('project_id', 'project_id.name')
    def _compute_project_name(self):
        for record in self:
            record.project_name = record.project_id.name if record.project_id else ''

    @api.depends('order_line', 'order_line.price_unit')
    def _compute_unit_sale_value(self):
        for record in self:
            record.unit_sale_value = record.order_line[0].price_unit if record.order_line else 0.0

    @api.depends(
        'broker_rate', 'referrer_rate', 'cashback_rate', 'other_external_rate',
        'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate'
    )
    def _compute_primary_commission_percentage(self):
        for record in self:
            rates = [
                record.broker_rate or 0,
                record.referrer_rate or 0,
                record.cashback_rate or 0,
                record.other_external_rate or 0,
                record.agent1_rate or 0,
                record.agent2_rate or 0,
                record.manager_rate or 0,
                record.director_rate or 0,
            ]
            record.primary_commission_percentage = max(rates) if rates else 0.0

    @api.depends('buyer_name', 'project_name', 'unit_sale_value', 'primary_commission_percentage')
    def _compute_deal_summary_html(self):
        for record in self:
            buyer = record.buyer_name or '—'
            project = record.project_name or '—'
            unit_val = (
                f"{record.currency_id.symbol} {record.unit_sale_value:,.2f}"
                if record.unit_sale_value
                else '—'
            )
            commission = (
                f"{record.primary_commission_percentage:.2f}%"
                if record.primary_commission_percentage
                else '—'
            )
            record.deal_summary_html = f"""
            <div style=\"background: #f8f9fa; padding: 12px; border-radius: 5px; border-left: 4px solid #8b1538;\">
                <table style=\"width: 100%; border-collapse: collapse; font-size: 12px;\">
                    <tr><td style=\"padding: 6px; font-weight: bold; width: 35%;\">Buyer:</td>
                        <td style=\"padding: 6px; color: #8b1538; font-weight: 500;\">{buyer}</td></tr>
                    <tr style=\"background: #ffffff;\"><td style=\"padding: 6px; font-weight: bold;\">Project:</td>
                        <td style=\"padding: 6px; color: #333;\">{project}</td></tr>
                    <tr><td style=\"padding: 6px; font-weight: bold;\">Unit Sale Value:</td>
                        <td style=\"padding: 6px; color: #333; text-align: right;\">{unit_val}</td></tr>
                    <tr style=\"background: #ffe6e6;\"><td style=\"padding: 6px; font-weight: bold;\">Commission %:</td>
                        <td style=\"padding: 6px; color: #8b1538; text-align: right; font-weight: bold;\">{commission}</td></tr>
                </table>
            </div>
            """

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'buyer_name': self.buyer_name,
            'project_name': self.project_name,
            'unit_sale_value': self.unit_sale_value,
            'commission_percentage': self.primary_commission_percentage,
            'sale_order_deal_reference': self.name,
        })
        return invoice_vals
