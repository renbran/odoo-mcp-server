# -*- coding: utf-8 -*-
{
    'name': 'Deal Report & Commission Management',
    'version': '17.0.1.0.0',
    'summary': 'Manage real estate deals with automated commission processing and direct bill generation',
    'description': """
        Deal Report Module
        ==================
        * Manage Primary, Secondary, Exclusive, and Rental sales
        * Automated commission calculations for internal and external partners
        * Direct bill processing without purchase orders
        * Document management with KYC, SPA, and passport uploads
        * Smart buttons for invoices, commissions, and bills navigation
        * Comprehensive commission tracking and reporting
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
        'security/deal_report_security.xml',
        'security/ir.model.access.csv',
        'data/deal_sequence.xml',
        'data/commission_product.xml',
        'views/deal_report_views.xml',
        'views/deal_commission_line_views.xml',
        'views/deal_bill_line_views.xml',
        'views/deal_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'deal_report/static/src/scss/deal_report.scss',
        ]
    },
    'installable': True,
    'application': True,
}
