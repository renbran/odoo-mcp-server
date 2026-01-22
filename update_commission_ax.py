#!/usr/bin/env python3
"""Update commission_ax module after fixing address_home_id issue"""
import xmlrpc.client
import time

url = "http://localhost:8069"
db = "odoo17_test"
username = "admin"
password = "admin"

print("⏳ Waiting for Odoo to restart...")
time.sleep(10)

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("✅ Connected!")
print("\n🔄 Updating commission_ax module...")

# Find module
module_ids = models.execute_kw(db, uid, password,
    'ir.module.module', 'search',
    [[['name', '=', 'commission_ax']]])

if module_ids:
    # Trigger upgrade
    models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [module_ids])
    
    print("✅ commission_ax module updated!")
    print("\n🎯 Now test at: http://localhost:8069")
    print("   Go to Sales → Orders → Create new order")
    print("   Select an agent and watch the commission rate auto-populate!")
else:
    print("❌ Module not found!")
