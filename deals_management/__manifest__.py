# -*- coding: utf-8 -*-
{
    'name': 'Deals Management',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Comprehensive Real Estate Deals Management with Documents & Bills',
    'description': """
Deals Management - Real Estate Sales Tracking
==============================================

Manage all types of real estate deals:
- Primary Sales
- Secondary Sales  
- Exclusive Deals
- Rental Sales

Features:
- Complete deal tracking with buyers and projects
- Booking dates and estimated invoice dates
- KYC, Booking Forms/SPA, and Passport uploads
- Multiple document attachments with downloads
- Financial summaries with VAT calculations
- Smart buttons: Invoices, Commissions, Bills
- Direct bill creation (bypass purchase orders)
- Commission integration
- Advanced filtering and reporting
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'sale',
        'commission_ax',
        'account',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/deals_views.xml',
        'views/project_unit_views.xml',
        'views/commission_views.xml',
        'views/deals_menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
