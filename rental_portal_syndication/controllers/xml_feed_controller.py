# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class XmlFeedController(http.Controller):
    @http.route(['/portal-feed/<string:portal_code>'], type='http', auth='public', csrf=False)
    def portal_feed(self, portal_code, token=None, **kwargs):
        """Public XML feed endpoint with token authentication"""
        
        # Input validation: portal_code should be alphanumeric or underscore
        if not portal_code or not portal_code.replace('_', '').isalnum():
            _logger.warning(
                "Invalid portal code attempted: %s from IP %s",
                portal_code, request.httprequest.remote_addr
            )
            return request.make_response(
                'Invalid portal code',
                [('Content-Type', 'text/plain')],
                status=400
            )
        
        # Search for portal connector
        portal = request.env['portal.connector'].sudo().search(
            [('code', '=', portal_code)],
            limit=1
        )
        
        # Verify portal exists and token matches
        if not portal or (portal.xml_feed_token and token != portal.xml_feed_token):
            _logger.warning(
                "Unauthorized feed access: portal=%s, token_provided=%s, ip=%s",
                portal_code,
                bool(token),
                request.httprequest.remote_addr
            )
            return request.make_response(
                'Unauthorized',
                [('Content-Type', 'text/plain')],
                status=401
            )
        
        # Log successful access and update usage tracking
        _logger.info(
            "Feed accessed successfully: portal=%s, ip=%s",
            portal_code,
            request.httprequest.remote_addr
        )
        
        # Update token usage statistics
        portal.sudo().write({
            'token_last_used': fields.Datetime.now(),
            'token_usage_count': portal.token_usage_count + 1,
        })
        
        # Placeholder: will render XML once generators are added
        body = "<?xml version='1.0' encoding='UTF-8'?><feed><status>not_implemented</status></feed>"
        return request.make_response(
            body,
            [('Content-Type', 'application/xml')]
        )
