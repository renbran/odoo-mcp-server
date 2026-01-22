# -*- coding: utf-8 -*-
from odoo import models, fields


class PortalConnector(models.Model):
    _inherit = 'portal.connector'

    include_in_bulk_publish = fields.Boolean(
        string='Include in Bulk Publish',
        default=True,
        help='Include this portal when using "Publish to All Portals" option'
    )
