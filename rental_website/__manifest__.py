# -*- coding: utf-8 -*-
{
    'name': 'Rental Property Website',
    'version': '17.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Public property listing website with advanced search and filtering',
    'description': """
        Rental Property Website Integration
        ====================================
        * Public property listing showcase
        * Advanced search and filtering
        * Responsive property detail pages
        * Lead capture and inquiry forms
        * SEO optimized property pages
        * Unlimited property listings
        * Integration with portal syndication
        * Pricing and package management
    """,
    'author': 'SGC Tech AI',
    'website': 'https://erp.sgctech.ai',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_mail',
        'rental_management',
        'rental_portal_syndication',
    ],
    'auto_install': True,  # Auto-install when rental_management + website are installed
    'data': [
        'security/ir.model.access.csv',
        'security/property_rules.xml',
        'data/website_data.xml',
        'views/property_details_views.xml',
        'views/property_website_templates.xml',
        'views/property_listing_templates.xml',
        'views/property_detail_templates.xml',
        'views/snippets.xml',
        'wizards/property_publish_wizard_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'rental_website/static/src/css/property_listing.css',
            'rental_website/static/src/js/property_search.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
