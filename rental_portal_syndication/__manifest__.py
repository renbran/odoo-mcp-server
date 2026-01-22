# -*- coding: utf-8 -*-
{
    "name": "Property Portal Syndication",
    "version": "17.0.0.1",
    "summary": "Multi-portal listing syndication, feeds, and website for rental_management",
    "description": "Initial scaffold for portal connectors, feeds, lead intake, and website listings on top of rental_management.",
    "author": "Scholarix",
    "website": "https://scholarix.ai",
    "category": "Real Estate",
    "license": "LGPL-3",
    "depends": [
        "rental_management",
        "website",
        "portal",
        "mail",
        "base",
        "web",
    ],
    "auto_install": True,  # Auto-install when rental_management is installed
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/portal_connector_views.xml",
        "views/portal_lead_views.xml",
        "views/portal_sync_log_views.xml",
        "views/xml_feed_config_views.xml",
        "views/property_portal_line_views.xml",
        "views/property_details_inherit_views.xml",
    ],
    "assets": {
        "web.assets_backend": [],
        "web.assets_frontend": [],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
