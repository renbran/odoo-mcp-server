# -*- coding: utf-8 -*-
"""
Account Move Extension - Brokerage Deal Reference

This module extends account.move (invoices) with references to original
brokerage deal information from the sale order for accounting context.
"""

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class AccountMoveWithDealTracking(models.Model):
    """Extend account.move with brokerage deal tracking fields"""
    
    _inherit = 'account.move'
    _description = 'Invoice with Brokerage Deal Information'

    # ===== DEAL INFORMATION FROM SALE ORDER =====
    
    buyer_name = fields.Char(
        string="Buyer Name",
        help="Original buyer/customer from sale order"
    )

    project_name = fields.Char(
        string="Project Name",
        help="Original project from sale order"
    )

    unit_sale_value = fields.Monetary(
        string="Unit Sale Value",
        currency_field='currency_id',
        help="Original unit sale value from order"
    )

    commission_percentage = fields.Float(
        string="Commission %",
        help="Primary commission percentage from order"
    )

    sale_order_deal_reference = fields.Char(
        string="Sale Order Reference",
        help="Link back to originating sale order for deal tracking"
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Source Sale Order",
        help="Sale order that generated this invoice"
    )

    # ===== COMPUTED FIELDS =====

    deal_information_summary = fields.Html(
        string="Deal Information Summary",
        compute="_compute_deal_information_summary",
        help="Summary of deal details for accounting review"
    )

    # ===== COMPUTE METHODS =====

    @api.depends(
        'buyer_name',
        'project_name',
        'unit_sale_value',
        'commission_percentage',
        'currency_id'
    )
    def _compute_deal_information_summary(self):
        """Compute HTML summary of deal information for invoice"""
        for record in self:
            buyer = record.buyer_name or '—'
            project = record.project_name or '—'
            unit_val = (
                f"{record.currency_id.symbol} {record.unit_sale_value:,.2f}"
                if record.unit_sale_value else '—'
            )
            commission = (
                f"{record.commission_percentage:.2f}%"
                if record.commission_percentage else '—'
            )
            
            record.deal_information_summary = f"""
            <div style="background: #f8f9fa; padding: 12px; border-radius: 5px;
                        border-left: 4px solid #8b1538; margin: 10px 0;">
                <h6 style="color: #8b1538; font-weight: bold; margin: 0 0 8px 0;">
                    ORIGINAL DEAL INFORMATION
                </h6>
                <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                    <tr>
                        <td style="padding: 4px; font-weight: bold; width: 40%;">
                            Buyer:
                        </td>
                        <td style="padding: 4px; color: #8b1538;">
                            {buyer}
                        </td>
                    </tr>
                    <tr style="background: #ffffff;">
                        <td style="padding: 4px; font-weight: bold;">
                            Project:
                        </td>
                        <td style="padding: 4px; color: #333;">
                            {project}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; font-weight: bold;">
                            Unit Sale Value:
                        </td>
                        <td style="padding: 4px; color: #333; text-align: right;">
                            {unit_val}
                        </td>
                    </tr>
                    <tr style="background: #ffe6e6;">
                        <td style="padding: 4px; font-weight: bold;">
                            Commission %:
                        </td>
                        <td style="padding: 4px; color: #8b1538; text-align: right;
                                  font-weight: bold;">
                            {commission}
                        </td>
                    </tr>
                </table>
            </div>
            """

    # ===== OVERRIDE METHODS =====

    def _get_invoice_intrastat_line_values(self):
        """
        Override to include deal information in intrastat lines
        Used for EU invoicing with deal context
        """
        lines = super()._get_invoice_intrastat_line_values()
        
        # Enhance line values with deal information
        for line in lines:
            if self.sale_order_id:
                line['buyer_name'] = self.buyer_name
                line['commission_percentage'] = self.commission_percentage
        
        return lines

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to ensure deal information is properly set
        when invoice is created from sale order
        """
        records = super().create(vals_list)
        
        for record in records:
            # If no deal information but there's a sale order, copy from it
            if record.sale_order_id and not record.buyer_name:
                sale_order = record.sale_order_id
                record.write({
                    'buyer_name': sale_order.buyer_name,
                    'project_name': sale_order.project_name,
                    'unit_sale_value': sale_order.unit_sale_value,
                    'commission_percentage': sale_order.primary_commission_percentage,
                    'sale_order_deal_reference': sale_order.name,
                })
                _logger.info(
                    f"Copied deal information to invoice {record.name} "
                    f"from sale order {sale_order.name}"
                )
        
        return records

    def action_view_sale_order_deal(self):
        """Action to view the related sale order and its deal information"""
        self.ensure_one()
        
        if not self.sale_order_id:
            # Try to find sale order by reference
            sale_orders = self.env['sale.order'].search([
                ('name', '=', self.sale_order_deal_reference)
            ], limit=1)
            
            if not sale_orders:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('No Sale Order Found'),
                        'message': _('Could not find related sale order for deal reference: %s') %
                                  self.sale_order_deal_reference,
                        'type': 'warning',
                    }
                }
            sale_order = sale_orders
        else:
            sale_order = self.sale_order_id
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order - %s') % sale_order.name,
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_related_commission_lines(self):
        """Action to view commission lines related to this invoice"""
        self.ensure_one()
        
        if not self.sale_order_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Commission Data'),
                    'message': _('No sale order is linked to this invoice'),
                    'type': 'info',
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Lines - %s') % self.name,
            'res_model': 'commission.line',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.sale_order_id.id)],
            'context': {'default_sale_order_id': self.sale_order_id.id},
        }
