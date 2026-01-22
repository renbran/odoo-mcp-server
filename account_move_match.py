# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class AccountMoveMatch(models.Model):
    """
    Extends account.move to add a direct link to matched sale orders.
    This allows invoices that were created outside the normal sale flow
    to be linked to their corresponding deals for accurate reporting.
    """
    _inherit = 'account.move'

    # Direct link to matched sale order (for invoices not created from SO)
    matched_sale_order_id = fields.Many2one(
        'sale.order',
        string='Matched Sale Order',
        help='Sale order matched by deal info (project/unit/buyer/deal_id). '
             'Used for invoices not created directly from sale orders.',
        index=True,
        copy=False,
        tracking=True,
    )

    # Computed field to get the effective sale order (either from lines or matched)
    effective_sale_order_id = fields.Many2one(
        'sale.order',
        string='Effective Sale Order',
        compute='_compute_effective_sale_order',
        store=True,
        help='The sale order this invoice belongs to - either from invoice lines or matched.',
    )

    is_manually_matched = fields.Boolean(
        string='Manually Matched',
        default=False,
        help='True if this invoice was matched to a sale order manually or via auto-match',
    )

    @api.depends('line_ids.sale_line_ids.order_id', 'matched_sale_order_id')
    def _compute_effective_sale_order(self):
        """
        Determine the effective sale order for this invoice.
        Priority:
        1. Sale order from invoice lines (standard Odoo linkage)
        2. Matched sale order (from deal info matching)
        """
        for move in self:
            # First try standard linkage via invoice lines
            sale_orders = move.line_ids.sale_line_ids.order_id
            if sale_orders:
                move.effective_sale_order_id = sale_orders[0]
            elif move.matched_sale_order_id:
                move.effective_sale_order_id = move.matched_sale_order_id
            else:
                move.effective_sale_order_id = False

    def action_match_to_sale_order(self):
        """
        Action to manually trigger matching for selected invoices.
        Can be called from a button or server action.
        """
        matched_count = 0
        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund'):
                continue
            # Skip if already linked via lines
            if move.line_ids.sale_line_ids.order_id:
                continue
            # Skip if already matched
            if move.matched_sale_order_id:
                continue

            # Try to find matching sale order
            matched_order = move._find_matching_sale_order()
            if matched_order:
                move.write({
                    'matched_sale_order_id': matched_order.id,
                    'is_manually_matched': True,
                })
                matched_count += 1
                _logger.info(f'Matched invoice {move.name} to order {matched_order.name}')

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Matching Complete',
                'message': f'Successfully matched {matched_count} invoice(s) to sale orders.',
                'type': 'success',
                'sticky': False,
            }
        }

    def _find_matching_sale_order(self):
        """
        Find a matching sale order based on deal information.

        Matching priority:
        1. deal_id (most reliable - unique identifier)
        2. project_id + unit_id (property identifier)
        3. project_id + buyer_id (buyer purchase in project)
        4. booking_date + buyer_id (date and buyer combination)

        Returns: sale.order record or empty recordset
        """
        self.ensure_one()
        SaleOrder = self.env['sale.order']

        # Get deal info from invoice
        deal_id = getattr(self, 'deal_id', None)
        project_id = getattr(self, 'project_id', None)
        unit_id = getattr(self, 'unit_id', None)
        buyer_id = getattr(self, 'buyer_id', None)
        booking_date = getattr(self, 'booking_date', None)

        base_domain = [('state', 'in', ['draft', 'sale', 'done'])]

        # Priority 1: Match by deal_id
        if deal_id:
            orders = SaleOrder.search(base_domain + [('deal_id', '=', deal_id)], limit=1)
            if orders:
                return orders

        # Priority 2: Match by project + unit
        if project_id and unit_id:
            proj_id = project_id.id if hasattr(project_id, 'id') else project_id
            un_id = unit_id.id if hasattr(unit_id, 'id') else unit_id
            orders = SaleOrder.search(base_domain + [
                ('project_id', '=', proj_id),
                ('unit_id', '=', un_id),
            ], limit=1)
            if orders:
                return orders

        # Priority 3: Match by project + buyer
        if project_id and buyer_id:
            proj_id = project_id.id if hasattr(project_id, 'id') else project_id
            buy_id = buyer_id.id if hasattr(buyer_id, 'id') else buyer_id
            orders = SaleOrder.search(base_domain + [
                ('project_id', '=', proj_id),
                ('buyer_id', '=', buy_id),
            ], limit=1)
            if orders:
                return orders

        # Priority 4: Match by booking_date + buyer
        if booking_date and buyer_id:
            buy_id = buyer_id.id if hasattr(buyer_id, 'id') else buyer_id
            orders = SaleOrder.search(base_domain + [
                ('booking_date', '=', booking_date),
                ('buyer_id', '=', buy_id),
            ], limit=1)
            if orders:
                return orders

        return SaleOrder.browse([])

    @api.model
    def cron_match_unlinked_invoices(self):
        """
        Scheduled action to automatically match unlinked invoices.
        Run periodically to catch new invoices that need matching.
        """
        # Find posted invoices without any linkage
        unlinked = self.search([
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('matched_sale_order_id', '=', False),
        ])

        # Filter to those not linked via lines
        to_match = unlinked.filtered(
            lambda m: not m.line_ids.sale_line_ids.order_id
        )

        _logger.info(f'Auto-matching {len(to_match)} unlinked invoices...')

        matched_count = 0
        for move in to_match:
            matched_order = move._find_matching_sale_order()
            if matched_order:
                move.write({
                    'matched_sale_order_id': matched_order.id,
                    'is_manually_matched': False,
                })
                matched_count += 1

        _logger.info(f'Auto-matched {matched_count} invoices to sale orders')
        return matched_count
