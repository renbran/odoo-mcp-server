# -*- coding: utf-8 -*-
{
    'name': 'Deal Report & Commissions',
    'version': '17.0.1.0.0',
    'summary': 'Deal reporting, commissions, and billing workflow for property deals',
    'description': 'Manage property deal reports with commission generation and billing integration.',
    'category': 'Sales',
    'author': 'Scholarix',
    'website': 'https://scholarix.com',
    'license': 'OPL-1',
    'depends': ['sale', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/deal_report_security.xml',
        'data/deal_sequence.xml',
        'data/commission_product.xml',
        'views/deal_report_views.xml',
        'views/deal_menu.xml',
        'views/deal_report_search.xml',
        'views/deal_dashboard_views.xml',
        'views/deal_report_analytics.xml',
        'reports/deal_report_templates.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'deal_report/static/src/scss/deal_report.scss',
        ]
    },
    'installable': True,
    'application': True,
}
