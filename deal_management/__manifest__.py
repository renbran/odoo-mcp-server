# -*- coding: utf-8 -*-
{
    'name': 'Deal Management',
    'version': '17.0.1.0.0',
    'summary': 'Manage sales deals with workflow automation and tracking',
    'description': """
        Deal Management Module
        =====================
        * Track deals through sales pipeline
        * Manage deal stages and state transitions
        * Calculate commissions automatically
        * Generate analytics and reports
        * Activity tracking and notifications
        * Integrated with contacts, projects, and accounting
    """,
    'category': 'Sales',
    'author': 'Scholarix',
    'website': 'https://scholarix.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
        'account',
        'product',
        'contacts',
        'mail',
        'project',
    ],
    'data': [
        'security/deal_management_security.xml',
        'security/ir.model.access.csv',
        'data/deal_sequence.xml',
        'data/deal_stage_data.xml',
        'views/deal_stage_views.xml',
        'views/deal_management_views.xml',
        'views/deal_search_views.xml',
        'views/deal_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'deal_management/static/src/scss/deal_management.scss',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
