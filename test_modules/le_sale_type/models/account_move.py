# -*- coding: utf-8 -*-
"""
Account Move Integration for Sale Order Type
==============================================
This module extends account.move (invoices) to integrate with sale.order.type,
automatically fetching the sale order type from the originating sale order.
"""

from odoo import models, fields, api


class AccountMove(models.Model):
    """
    Extension of account.move to include sale_order_type_id field.
    This enables tracking of sale order types through the invoice lifecycle.
    """
    _inherit = 'account.move'

    # Many2one field to link invoice with sale order type
    sale_order_type_id = fields.Many2one(
        comodel_name='sale.order.type',
        string='Sale Order Type',
        help='Sale Order Type from the originating Sale Order. '
             'This field is automatically populated when creating invoices from sale orders.',
        compute='_compute_sale_order_type_from_lines',  # Auto-compute from sale orders
        store=True,  # Store for filtering and reporting
        readonly=False,  # Allow manual changes if needed
        copy=True,  # Copy to credit notes and duplicated invoices
        tracking=True,  # Track changes in chatter
        index=True,  # Index for faster filtering
    )

    @api.depends('invoice_line_ids', 'invoice_line_ids.sale_line_ids')
    def _compute_sale_order_type_from_lines(self):
        """
        Compute method to fetch sale_order_type_id from sale order lines.
        This method checks all invoice lines for their originating sale orders
        and sets the sale_order_type_id from the first valid sale order found.

        Priority logic:
        1. First checks invoice_line_ids -> sale_line_ids -> order_id -> sale_order_type_id
        2. If multiple sale orders exist, uses the first one found
        3. Logs a warning if multiple different sale types are detected
        """
        for move in self:
            # Only process customer invoices and credit notes
            if move.move_type not in ('out_invoice', 'out_refund'):
                move.sale_order_type_id = False
                continue

            sale_order_types = set()
            sale_orders = self.env['sale.order']

            # Collect all related sale orders from invoice lines
            for line in move.invoice_line_ids:
                if line.sale_line_ids:
                    for sale_line in line.sale_line_ids:
                        if sale_line.order_id:
                            sale_orders |= sale_line.order_id
                            if sale_line.order_id.sale_order_type_id:
                                sale_order_types.add(sale_line.order_id.sale_order_type_id.id)

            # Set the sale order type from the first sale order found
            if sale_orders:
                first_sale_order = sale_orders[0]
                if first_sale_order.sale_order_type_id:
                    move.sale_order_type_id = first_sale_order.sale_order_type_id

                    # Log warning if multiple different sale types detected
                    if len(sale_order_types) > 1:
                        import logging
                        _logger = logging.getLogger(__name__)
                        _logger.warning(
                            'Invoice %s is linked to sale orders with different sale types: %s. '
                            'Using sale type from order %s.',
                            move.name or 'Draft',
                            sale_order_types,
                            first_sale_order.name
                        )
                else:
                    move.sale_order_type_id = False
            else:
                # No sale order found, keep existing value or set to False
                if not move.sale_order_type_id:
                    move.sale_order_type_id = False

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to automatically set sale_order_type_id when invoice is created.
        This ensures the field is populated for invoices generated from sale orders.
        """
        moves = super(AccountMove, self).create(vals_list)

        # Compute sale order type for newly created invoices
        for move in moves:
            if move.move_type in ('out_invoice', 'out_refund'):
                move._compute_sale_order_type_from_lines()

        return moves

    def write(self, vals):
        """
        Override write to recompute sale_order_type_id when invoice lines change.
        This ensures the field stays synchronized when invoice lines are added/modified.
        """
        result = super(AccountMove, self).write(vals)

        # Recompute if invoice lines were modified
        if 'invoice_line_ids' in vals:
            for move in self:
                if move.move_type in ('out_invoice', 'out_refund'):
                    # Only recompute if sale_order_type_id is not manually set
                    if not vals.get('sale_order_type_id'):
                        move._compute_sale_order_type_from_lines()

        return result

    def _reverse_moves(self, default_values_list=None, cancel=False):
        """
        Override _reverse_moves to ensure sale_order_type_id is copied to credit notes.
        This maintains the sale type relationship when creating refunds.
        """
        if default_values_list is None:
            default_values_list = [{} for _move in self]

        # Add sale_order_type_id to default values for each reversed move
        for move, default_values in zip(self, default_values_list):
            if move.sale_order_type_id and 'sale_order_type_id' not in default_values:
                default_values['sale_order_type_id'] = move.sale_order_type_id.id

        return super(AccountMove, self)._reverse_moves(
            default_values_list=default_values_list,
            cancel=cancel
        )

    @api.onchange('partner_id')
    def _onchange_partner_id_sale_type(self):
        """
        Optional: Reset sale_order_type_id when partner changes on draft invoices.
        This prevents incorrect sale type associations when manually creating invoices.
        """
        # Only reset on draft invoices that are manually created (no sale order lines yet)
        if self.state == 'draft' and not self.invoice_line_ids.filtered(lambda l: l.sale_line_ids):
            self.sale_order_type_id = False
