{
    'name': 'Sale Order Type',
    'version': '1.1.0',
    'author': 'Luna ERP Solutions',
    'website': 'https://www.lunerpsolution.com',
    'license': 'LGPL-3',
    'support': 'support@lunerpsolution.com',
    'category': 'Sales',
    'summary': 'Sale Order Type with Invoice Integration',
    'description': """
        Sale Order Type Management with Invoice Integration
        =====================================================

        Features:
        ---------
        * Define custom sale order types with sequences
        * Automatically assign order numbers based on sale type
        * Integrate sale order type into invoices
        * Auto-fetch sale type from sale orders to invoices
        * Filter and report invoices by sale type
        * Support for customer invoices and credit notes

        Version 1.1.0:
        --------------
        * Added sale_order_type_id field to account.move (invoices)
        * Auto-computation of sale type from originating sale orders
        * Enhanced invoice views with sale type filtering
        * Pivot and graph view integration for analytics
        * Proper handling of credit notes and refunds
    """,
    'depends': [
        'sale',
        'account',  # Added dependency for invoice integration
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_type_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',  # New invoice views
    ],
    'images': ["static/description/banner.png"],
    'installable': True,
    'application': False,
    'auto_install': False,
}
