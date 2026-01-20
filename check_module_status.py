#!/usr/bin/env python3
"""
Check module installation status
"""

import xmlrpc.client as xmlrpc
import time

# Wait for Odoo to fully restart
print('Waiting 30 seconds for Odoo to fully restart...')
time.sleep(30)

# Connect and check module status
url = 'https://erposus.com'
db = 'osusproperties'
username = 'salescompliance@osusproperties.com'
password = '8586583'

common = xmlrpc.ServerProxy(f'{url}/xmlrpc/2/common')
models = xmlrpc.ServerProxy(f'{url}/xmlrpc/2/object')

uid = common.authenticate(db, username, password, {})
print(f'Connected (UID: {uid})')

# Check module
modules = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [['name', '=', 'invoice_status_tags']])
if modules:
    module = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [modules[0], ['name', 'state', 'installed_version']])
    print(f'\nModule found:')
    print(f'  Name: {module[0]["name"]}')
    print(f'  State: {module[0]["state"]}')
    print(f'  Version: {module[0].get("installed_version", "N/A")}')
    
    if module[0]['state'] == 'installed':
        print('\n[SUCCESS] Module is installed!')
    elif module[0]['state'] == 'to install':
        print('\n[PENDING] Module is staged for installation')
        print('\nYou may need to:')
        print('  1. Click "Update Module List" in Odoo Apps')
        print('  2. Search for "Invoice Status Tags"')
        print('  3. Click "Install" button')
    else:
        print(f'\n[INFO] Module state: {module[0]["state"]}')
else:
    print('\n[WARNING] Module not found in database')
    print('The module may not have been detected yet')
    print('Try clicking "Update Module List" in Odoo Apps panel')
