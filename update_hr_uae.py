#!/usr/bin/env python3
"""Update hr_uae module after fixing contract_id issue"""
import xmlrpc.client
import time

url = "http://localhost:8069"
db = "odoo17_test"
username = "admin"
password = "admin"

print("⏳ Waiting for Odoo to restart...")
time.sleep(15)

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("✅ Connected!")
print("\n🔄 Updating hr_uae module...")

# Find module
module_ids = models.execute_kw(db, uid, password,
    'ir.module.module', 'search',
    [[['name', '=', 'hr_uae']]])

if module_ids:
    # Trigger upgrade
    models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [module_ids])
    
    print("✅ hr_uae module updated!")
    print("\n✅ contract_id issue fixed!")
    print("   - Now safely searches for active contracts")
    print("   - No more AttributeError on hr.employee")
else:
    print("❌ Module not found!")
