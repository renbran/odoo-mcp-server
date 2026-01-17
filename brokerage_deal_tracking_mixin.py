# -*- coding: utf-8 -*-
"""
Brokerage Deal Tracking Mixin

This mixin provides consolidated deal information fields that are
used across sale.order and account.move for complete brokerage tracking.
"""

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class BrokerageDealTrackingMixin(models.AbstractModel):
    """Mixin to provide deal tracking fields for sales and accounting"""
    
    _name = 'brokerage.deal.tracking.mixin'
    _description = 'Brokerage Deal Tracking'

    # ===== DEAL INFORMATION FIELDS =====
    
    buyer_name = fields.Char(
        string="Buyer Name",
        compute="_compute_buyer_name",
        store=True,
        help="Buyer/Customer name for deal tracking. Auto-populated from customer."
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
        help="Price per unit for deal tracking. From first order line unit price."
    )

    primary_commission_percentage = fields.Float(
        string="Primary Commission %",
        compute="_compute_primary_commission_percentage",
        store=True,
        help="Highest commission % among all partners for quick reference"
    )

    deal_summary = fields.Html(
        string="Deal Summary",
        compute="_compute_deal_summary",
        help="HTML summary of buyer, project, unit value, and commission % for reporting"
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
                # Get the first (and typically only) line
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
        """Compute highest commission percentage among all partners"""
        for record in self:
            # Collect all commission percentages
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
            # Get the highest
            record.primary_commission_percentage = max(rates) if rates else 0.0

    @api.depends(
        'buyer_name',
        'project_name',
        'unit_sale_value',
        'primary_commission_percentage',
        'currency_id'
    )
    def _compute_deal_summary(self):
        """Compute HTML summary of deal information"""
        for record in self:
            buyer = record.buyer_name or '—'
            project = record.project_name or '—'
            unit_val = f"{record.currency_id.symbol}{record.unit_sale_value:,.2f}" if record.unit_sale_value else '—'
            commission = f"{record.primary_commission_percentage:.2f}%" if record.primary_commission_percentage else '—'
            
            record.deal_summary = f"""
            <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; font-size: 12px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px; font-weight: bold; width: 30%;">Buyer:</td>
                        <td style="padding: 5px; color: #8b1538;">{buyer}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; font-weight: bold;">Project:</td>
                        <td style="padding: 5px; color: #333;">{project}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; font-weight: bold;">Unit Sale Value:</td>
                        <td style="padding: 5px; color: #333; text-align: right;">{unit_val}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; font-weight: bold;">Commission %:</td>
                        <td style="padding: 5px; color: #8b1538; text-align: right; font-weight: bold;">{commission}</td>
                    </tr>
                </table>
            </div>
            """
