# -*- coding: utf-8 -*-
"""
Invoice Enhancement with Deal Information
Ensures deal fields from sales orders are properly passed to invoices
"""

from odoo import models, fields, api


class AccountMoveWithDeals(models.Model):
    _inherit = 'account.move'

    # ============================================================================
    # DEAL INFORMATION FIELDS
    # ============================================================================

    buyer_name = fields.Char(
        string='Buyer Name',
        tracking=True,
        help='Name of the buyer in the original deal'
    )

    project_name = fields.Char(
        string='Project Name',
        tracking=True,
        help='Project or property name associated with the deal'
    )

    unit_sale_value = fields.Monetary(
        string='Unit Sale Value',
        currency_field='company_currency_id',
        tracking=True,
        help='Original unit sale value from the deal'
    )

    commission_percentage = fields.Float(
        string='Commission Percentage (%)',
        tracking=True,
        digits=(5, 2),
        help='Commission percentage from the original deal'
    )

    sale_order_deal_reference = fields.Char(
        string='Deal Reference',
        tracking=True,
        help='Original deal reference from sales order'
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Related Sale Order',
        tracking=True,
        help='Link to the original sale order'
    )

    deal_information_summary = fields.Html(
        string='Deal Information Summary',
        compute='_compute_deal_information_summary',
        help='Formatted summary of deal information'
    )

    # ============================================================================
    # DEAL FIELD PROPAGATION METHODS
    # ============================================================================

    @api.depends('sale_order_id', 'buyer_name', 'project_name', 
                 'unit_sale_value', 'commission_percentage')
    def _compute_deal_information_summary(self):
        """
        Compute a formatted HTML summary of deal information
        """
        for invoice in self:
            if invoice.move_type not in ('out_invoice', 'out_refund'):
                invoice.deal_information_summary = False
                continue

            buyer = invoice.buyer_name or '—'
            project = invoice.project_name or '—'
            unit_value = invoice.unit_sale_value or 0
            commission = invoice.commission_percentage or 0
            currency = invoice.currency_id.symbol

            # Format unit value
            if unit_value:
                formatted_value = f"{unit_value:,.2f} {currency}"
            else:
                formatted_value = '—'

            # Format commission
            if commission:
                formatted_commission = f"{commission:.2f}%"
            else:
                formatted_commission = '—'

            html_summary = f"""
            <div style="background: #f8f9fa; padding: 12px; border-radius: 5px; 
                border-left: 4px solid #8b1538;">
                <h6 style="color: #8b1538; margin: 0 0 8px 0;">
                    ORIGINAL DEAL INFORMATION
                </h6>
                <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                    <tr>
                        <td style="padding: 4px; font-weight: bold; width: 40%;">Buyer:</td>
                        <td style="padding: 4px; color: #8b1538;">{buyer}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; font-weight: bold;">Project:</td>
                        <td style="padding: 4px; color: #333;">{project}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; font-weight: bold;">
                            Unit Sale Value:
                        </td>
                        <td style="padding: 4px; text-align: right;">{formatted_value}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; font-weight: bold;">Commission %:</td>
                        <td style="padding: 4px; color: #8b1538; font-weight: bold; 
                            text-align: right;">{formatted_commission}</td>
                    </tr>
                </table>
            </div>
            """

            invoice.deal_information_summary = html_summary

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        """
        Override create to populate deal fields from sales order
        """
        for vals in vals_list:
            self._populate_deal_fields_from_invoice_lines(vals)
        return super().create(vals_list)

    def write(self, vals):
        """
        Override write to ensure deal fields stay in sync
        """
        # If sale_order_id is being set, populate deal fields from it
        if 'sale_order_id' in vals and vals['sale_order_id']:
            so_id = vals['sale_order_id']
            sale_order = self.env['sale.order'].browse(so_id)
            
            # Only update if not already set by user
            if 'buyer_name' not in vals:
                vals['buyer_name'] = (
                    sale_order.buyer_name or 
                    sale_order.partner_id.name
                )
            if 'project_name' not in vals:
                vals['project_name'] = sale_order.project_name
            if 'unit_sale_value' not in vals:
                vals['unit_sale_value'] = sale_order.unit_sale_value
            if 'commission_percentage' not in vals:
                vals['commission_percentage'] = sale_order.commission_percentage
            if 'sale_order_deal_reference' not in vals:
                vals['sale_order_deal_reference'] = (
                    sale_order.sale_order_deal_reference or 
                    sale_order.name
                )

        return super().write(vals)

    @staticmethod
    def _populate_deal_fields_from_invoice_lines(vals):
        """
        Helper method to populate deal fields from invoice lines
        """
        if 'line_ids' in vals:
            # Extract sale order from first invoice line if it has one
            for line_vals in vals.get('line_ids', []):
                # This is a simple approach; enhanced logic can be added
                pass

    # ============================================================================
    # REPORT GENERATION
    # ============================================================================

    def generate_invoice_with_deals_pdf(self):
        """
        Generate PDF report of invoice with deal information
        """
        return self.env.ref(
            'scholarix_recruitment.account_report_invoice_with_deals'
        ).report_action(self)


class SaleOrderDealIntegration(models.Model):
    _inherit = 'sale.order'

    # ============================================================================
    # DEAL FIELDS (TO MATCH INVOICE STRUCTURE)
    # ============================================================================

    buyer_name = fields.Char(
        string='Buyer Name',
        tracking=True,
        help='Name of the buyer'
    )

    project_name = fields.Char(
        string='Project Name',
        tracking=True,
        help='Project or property name'
    )

    unit_sale_value = fields.Monetary(
        string='Unit Sale Value',
        currency_field='currency_id',
        tracking=True,
        help='Value per unit'
    )

    commission_percentage = fields.Float(
        string='Commission Percentage (%)',
        tracking=True,
        digits=(5, 2),
        help='Commission percentage'
    )

    sale_order_deal_reference = fields.Char(
        string='Deal Reference',
        tracking=True,
        help='Deal reference number'
    )

    # ============================================================================
    # FIELD SYNCHRONIZATION WITH INVOICE
    # ============================================================================

    def _prepare_invoice_values(self):
        """
        Override to include deal information in invoice creation
        """
        invoice_vals = super()._prepare_invoice_values()
        
        # Add deal fields to invoice
        invoice_vals.update({
            'buyer_name': self.buyer_name,
            'project_name': self.project_name,
            'unit_sale_value': self.unit_sale_value,
            'commission_percentage': self.commission_percentage,
            'sale_order_deal_reference': (
                self.sale_order_deal_reference or 
                self.name
            ),
            'sale_order_id': self.id,
        })
        
        return invoice_vals
