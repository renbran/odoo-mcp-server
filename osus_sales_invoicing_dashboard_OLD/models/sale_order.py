# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_progress = fields.Selection(
        selection=[
            ('none', 'Not Invoiced'),
            ('partial', 'Pending to Invoice'),
            ('full', 'Fully Invoiced'),
        ],
        string='Invoicing Progress',
        compute='_compute_invoice_progress',
        store=False,
    )

    @api.depends('invoice_status')
    def _compute_invoice_progress(self):
        for order in self:
            status = order.invoice_status
            if status == 'invoiced':
                order.invoice_progress = 'full'
            elif status == 'to invoice':
                order.invoice_progress = 'partial'
            else:
                order.invoice_progress = 'none'
