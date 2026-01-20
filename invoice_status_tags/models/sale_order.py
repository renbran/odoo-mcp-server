# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.float_utils import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Invoicing Progress Fields
    invoicing_percentage = fields.Float(
        string='Invoicing Progress',
        compute='_compute_invoicing_details',
        store=True,
        help="Percentage of order lines that have been invoiced"
    )
    
    invoice_type_tag = fields.Selection([
        ('not_started', 'Not Started'),
        ('partial', 'Partial Invoicing'),
        ('fully_invoiced', 'Fully Invoiced'),
        ('draft_only', 'Draft Only'),
        ('upsell', 'Upsell'),
        ('cancelled', 'Cancelled'),
    ], string='Invoice Type', compute='_compute_invoicing_details', store=True)
    
    # Invoice Counts by State
    posted_invoice_count = fields.Integer(
        string='Posted Invoices',
        compute='_compute_invoice_counts',
        store=True
    )
    draft_invoice_count = fields.Integer(
        string='Draft Invoices',
        compute='_compute_invoice_counts',
        store=True
    )
    cancelled_invoice_count = fields.Integer(
        string='Cancelled Invoices',
        compute='_compute_invoice_counts',
        store=True
    )
    
    # Warning Fields
    has_draft_invoice_warning = fields.Boolean(
        string='Draft Invoice Warning',
        compute='_compute_invoicing_details',
        store=True,
        help="Order has draft invoices that need validation"
    )
    
    needs_invoice_attention = fields.Boolean(
        string='Needs Attention',
        compute='_compute_invoicing_details',
        store=True,
        help="Order has invoicing issues that need attention"
    )
    
    # Amount Fields
    total_invoiced_amount = fields.Monetary(
        string='Total Invoiced',
        compute='_compute_invoicing_amounts',
        store=True,
        currency_field='currency_id'
    )
    
    remaining_to_invoice = fields.Monetary(
        string='Remaining to Invoice',
        compute='_compute_invoicing_amounts',
        store=True,
        currency_field='currency_id'
    )
    
    upsell_amount = fields.Monetary(
        string='Upsell Amount',
        compute='_compute_invoicing_amounts',
        store=True,
        currency_field='currency_id',
        help="Amount invoiced beyond order value"
    )

    @api.depends('order_line.qty_invoiced', 'order_line.product_uom_qty', 'invoice_ids.state')
    def _compute_invoicing_details(self):
        """Compute detailed invoicing status and warnings"""
        for order in self:
            if not order.order_line:
                order.invoicing_percentage = 0.0
                order.invoice_type_tag = 'not_started'
                order.has_draft_invoice_warning = False
                order.needs_invoice_attention = False
                continue
            
            # Calculate invoicing percentage
            total_qty = sum(line.product_uom_qty for line in order.order_line)
            invoiced_qty = sum(line.qty_invoiced for line in order.order_line)
            
            if total_qty > 0:
                order.invoicing_percentage = (invoiced_qty / total_qty) * 100
            else:
                order.invoicing_percentage = 0.0
            
            # Get invoice counts by state
            posted_invoices = order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.move_type == 'out_invoice'
            )
            draft_invoices = order.invoice_ids.filtered(
                lambda inv: inv.state == 'draft' and inv.move_type == 'out_invoice'
            )
            cancelled_invoices = order.invoice_ids.filtered(
                lambda inv: inv.state == 'cancel'
            )
            
            # Determine invoice type tag
            if order.invoice_status == 'upsell':
                order.invoice_type_tag = 'upsell'
            elif posted_invoices and order.invoicing_percentage >= 99.9:
                order.invoice_type_tag = 'fully_invoiced'
            elif posted_invoices and 0 < order.invoicing_percentage < 99.9:
                order.invoice_type_tag = 'partial'
            elif draft_invoices and not posted_invoices:
                order.invoice_type_tag = 'draft_only'
            elif cancelled_invoices and not posted_invoices and not draft_invoices:
                order.invoice_type_tag = 'cancelled'
            else:
                order.invoice_type_tag = 'not_started'
            
            # Set warnings
            order.has_draft_invoice_warning = bool(draft_invoices)
            
            # Needs attention if:
            # - Has draft invoices only but marked as invoiced
            # - Has posted invoices but marked as to invoice
            # - Has cancelled invoices only but not marked as no
            needs_attention = False
            if draft_invoices and not posted_invoices and order.invoice_status == 'invoiced':
                needs_attention = True  # CRITICAL: Draft only but shows invoiced
            elif posted_invoices and order.invoice_status == 'to invoice':
                needs_attention = True  # Has posted invoices but shows to invoice
            elif cancelled_invoices and not posted_invoices and not draft_invoices and order.invoice_status != 'no':
                needs_attention = True  # Only cancelled but not marked as no
            
            order.needs_invoice_attention = needs_attention

    @api.depends('invoice_ids', 'invoice_ids.state')
    def _compute_invoice_counts(self):
        """Count invoices by state"""
        for order in self:
            order.posted_invoice_count = len(order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.move_type == 'out_invoice'
            ))
            order.draft_invoice_count = len(order.invoice_ids.filtered(
                lambda inv: inv.state == 'draft' and inv.move_type == 'out_invoice'
            ))
            order.cancelled_invoice_count = len(order.invoice_ids.filtered(
                lambda inv: inv.state == 'cancel'
            ))

    @api.depends('invoice_ids.amount_total', 'invoice_ids.state', 'amount_total')
    def _compute_invoicing_amounts(self):
        """Compute invoiced amounts and remaining"""
        for order in self:
            # Calculate total invoiced (posted invoices only)
            posted_invoices = order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.move_type == 'out_invoice'
            )
            order.total_invoiced_amount = sum(posted_invoices.mapped('amount_total'))
            
            # Calculate remaining to invoice
            precision = self.env['decimal.precision'].precision_get('Product Price')
            if float_compare(order.total_invoiced_amount, order.amount_total, precision_digits=precision) >= 0:
                # Fully invoiced or upsell
                order.remaining_to_invoice = 0.0
                order.upsell_amount = order.total_invoiced_amount - order.amount_total
            else:
                # Partially invoiced or not invoiced
                order.remaining_to_invoice = order.amount_total - order.total_invoiced_amount
                order.upsell_amount = 0.0
