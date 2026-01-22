# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class PortalWebsite(http.Controller):
    @http.route(['/portal/properties'], type='http', auth='public', website=True)
    def properties_listing(self, **kwargs):
        """Legacy portal entrypoint kept off /properties to avoid shadowing the main site."""

        return request.redirect('/properties', code=301)
