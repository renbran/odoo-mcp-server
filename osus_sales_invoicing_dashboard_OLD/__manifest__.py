# -*- coding: utf-8 -*-
{
    "name": "OSUS Sales & Invoicing Dashboard",
    "version": "17.0.1.0.0",
    "category": "Sales",
    "summary": "Mini dashboard for invoicing KPIs and sale order tags.",
    "description": (
        "Provides a compact dashboard with clickable KPIs for posted "
        "invoices, pending to invoice orders, and unpaid invoices. Also "
        "adds helper badges/ribbons on sale orders to visualize invoicing "
        "progress."
    ),
    "author": "OSUS Properties",
    "license": "LGPL-3",
    "depends": ["sale", "account", "le_sale_type", "website"],
    "assets": {
        "web.assets_backend": [
            "osus_sales_invoicing_dashboard/static/src/xml/dashboard_charts.xml",
            "osus_sales_invoicing_dashboard/static/src/scss/dashboard_charts.scss",
            "osus_sales_invoicing_dashboard/static/src/js/dashboard_charts.js",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/website_layout_fix.xml",
        "views/dashboard_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
