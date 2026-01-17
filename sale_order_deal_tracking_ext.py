# -*- coding: utf-8 -*-
"""
Sale Order Extension - Brokerage Deal Tracking

This module extends sale.order with brokerage-specific deal tracking fields
to ensure all deal information (buyer, project, unit value, commission %)
is captured and available for invoicing and reporting.
"""

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class SaleOrderDealTracking(models.Model):
    """Extend sale.order with brokerage deal tracking fields"""
    
    _inherit = 'sale.order'
    _description = 'Sale Order with Deal Tracking'

    # Inherit deal tracking fields from mixin
    _inherits = {'brokerage.deal.tracking.mixin': 'deal_tracking_id'}

    deal_tracking_id = fields.Many2one(
        'brokerage.deal.tracking.mixin',
        string="Deal Tracking",
        ondelete='cascade',
        auto_join=True
    )

    # For backward compatibility, expose mixin fields as Many2one related
    # This allows the fields to be used directly without the mixin overhead
    buyer_name = fields.Char(
        string="Buyer Name",
        compute="_compute_buyer_name",
        store=True,
        help="Buyer/Customer name for deal tracking"
    )

    project_name = fields.Char(
        string="Project Name",
        compute="_compute_project_name",
        store=True,
        help="Project name if deal is project-related"
    )

    unit_sale_value = fields.Monetary(
        string="Unit Sale Value",
        compute="_compute_unit_sale_value",
        store=True,
        currency_field='currency_id',
        help="Price per unit for deal tracking"
    )

    primary_commission_percentage = fields.Float(
        string="Primary Commission %",
        compute="_compute_primary_commission_percentage",
        store=True,
        help="Highest commission % among all partners"
    )

    deal_summary_html = fields.Html(
        string="Deal Summary",
        compute="_compute_deal_summary_html",
        help="HTML summary of deal information for reporting"
    )

    # ===== COMPUTE METHODS =====

    @api.depends('partner_id', 'partner_id.name')
    def _compute_buyer_name(self):
        """Compute buyer name from customer"""
        for record in self:
            record.buyer_name = record.partner_id.name if record.partner_id else ''

    @api.depends('project_id', 'project_id.name')
    def _compute_project_name(self):
        """Compute project name from project field"""
        for record in self:
            record.project_name = record.project_id.name if record.project_id else ''

    @api.depends('order_line', 'order_line.price_unit')
    def _compute_unit_sale_value(self):
        """Compute unit sale value from first order line"""
        for record in self:
            if record.order_line:
                line = record.order_line[0]
                record.unit_sale_value = line.price_unit
            else:
                record.unit_sale_value = 0.0

    @api.depends(
        'broker_rate',
        'referrer_rate',
        'cashback_rate',
        'other_external_rate',
        'agent1_rate',
        'agent2_rate',
        'manager_rate',
        'director_rate'
    )
    def _compute_primary_commission_percentage(self):
        """Compute highest commission percentage"""
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

    @api.depends(
        'buyer_name',
        'project_name',
        'unit_sale_value',
        'primary_commission_percentage',
        'currency_id'
    )
    def _compute_deal_summary_html(self):
        """Compute HTML summary for display and reporting"""
        for record in self:
            buyer = record.buyer_name or '—'
            project = record.project_name or '—'
            unit_val = (
                f"{record.currency_id.symbol} {record.unit_sale_value:,.2f}"
                if record.unit_sale_value else '—'
            )
            commission = (
                f"{record.primary_commission_percentage:.2f}%"
                if record.primary_commission_percentage else '—'
            )
            
            record.deal_summary_html = f"""
            <div style="background: #f8f9fa; padding: 12px; border-radius: 5px; 
                        border-left: 4px solid #8b1538; font-size: 12px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 6px; font-weight: bold; width: 35%;">
                            Buyer:
                        </td>
                        <td style="padding: 6px; color: #8b1538; font-weight: 500;">
                            {buyer}
                        </td>
                    </tr>
                    <tr style="background: #ffffff;">
                        <td style="padding: 6px; font-weight: bold;">
                            Project:
                        </td>
                        <td style="padding: 6px; color: #333;">
                            {project}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 6px; font-weight: bold;">
                            Unit Sale Value:
                        </td>
                        <td style="padding: 6px; color: #333; text-align: right;">
                            {unit_val}
                        </td>
                    </tr>
                    <tr style="background: #ffe6e6;">
                        <td style="padding: 6px; font-weight: bold;">
                            Commission %:
                        </td>
                        <td style="padding: 6px; color: #8b1538; 
                                  text-align: right; font-weight: bold;">
                            {commission}
                        </td>
                    </tr>
                </table>
            </div>
            """

    # ===== OVERRIDE METHODS =====

    def _prepare_invoice(self):
        """Override to pass deal tracking info to invoice"""
        invoice_vals = super()._prepare_invoice()
        
        # Add deal tracking fields to invoice
        invoice_vals.update({
            'buyer_name': self.buyer_name,
            'project_name': self.project_name,
            'unit_sale_value': self.unit_sale_value,
            'commission_percentage': self.primary_commission_percentage,
            'sale_order_deal_reference': self.name,
        })
        
        return invoice_vals

    def action_view_deal_summary(self):
        """Action to display deal summary in a dialog"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Deal Information - %s') % self.name,
            'res_model': 'ir.ui.view',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_name': f'Deal Summary: {self.name}',
                'default_type': 'html',
                'default_arch': self.deal_summary_html,
            }
        }
