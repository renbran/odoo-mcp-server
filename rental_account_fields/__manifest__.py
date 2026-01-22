{
    'name': 'Rental Account Fields',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Add rental/property management fields to account.move',
    'description': 'Extends account.move with rental and property management fields',
    'author': 'Scholarix',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,  # Auto-install when account is installed
    'license': 'LGPL-3',
}
