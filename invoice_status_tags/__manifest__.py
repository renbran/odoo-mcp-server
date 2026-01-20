# -*- coding: utf-8 -*-
{
    'name': 'Invoice Status Tags & Controls',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Clear invoice status tagging and invoicing controls for better visibility',
    'description': """
Invoice Status Tags & Controls
===============================
Adds clear visual indicators and controls for invoice status:

Features:
---------
* **Invoice Status Tags**: Visual tags showing invoice progress
* **Invoicing Percentage**: Track how much of order is invoiced
* **Draft Invoice Warning**: Alert when draft invoices exist
* **Partial Invoicing Indicator**: Show orders with partial invoicing
* **Invoice Type Badge**: Quick view of invoice types (Posted/Draft/Cancelled)
* **Custom Filters**: Easy filtering by invoice status
* **Smart Buttons**: Quick access to invoice analytics

Use Cases:
----------
- Identify orders with draft invoices that need validation
- Track partial invoicing progress
- Monitor upsell scenarios
- Control invoicing workflow visibility
    """,
    'author': 'SGC TECH AI',
    'website': 'https://github.com/renbran/odoo-mcp-server',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
