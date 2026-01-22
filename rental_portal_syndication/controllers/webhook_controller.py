# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class WebhookController(http.Controller):
    @http.route(['/portal-webhook/<string:portal_code>'], type='json', auth='public', csrf=False)
    def portal_webhook(self, portal_code, **payload):
        """Webhook endpoint for receiving lead data from portals"""
        
        # Input validation
        if not portal_code or not portal_code.replace('_', '').isalnum():
            _logger.warning(
                "Invalid portal code in webhook: %s from IP %s",
                portal_code,
                request.httprequest.remote_addr
            )
            return {"status": "error", "message": "Invalid portal code"}
        
        # Find portal
        portal = request.env['portal.connector'].sudo().search(
            [('code', '=', portal_code)],
            limit=1
        )
        
        if not portal:
            _logger.warning(
                "Unknown portal in webhook: %s from IP %s",
                portal_code,
                request.httprequest.remote_addr
            )
            return {"status": "error", "message": "Unknown portal"}
        
        # Log webhook receipt
        _logger.info(
            "Webhook received: portal=%s, payload_size=%d, ip=%s",
            portal_code,
            len(str(payload)),
            request.httprequest.remote_addr
        )
        
        # Placeholder: store raw payload as message for visibility
        request.env['portal.sync.log'].sudo().create({
            'portal_id': portal.id,
            'status': 'failed',
            'message': f'Webhook handler not implemented. Payload keys: {list(payload.keys())}',
        })
        
        return {
            "status": "pending",
            "message": "Webhook handler not implemented"
        }
