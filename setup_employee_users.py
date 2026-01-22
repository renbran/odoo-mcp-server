#!/usr/bin/env python3
"""
Setup employee users for commission testing
"""

import xmlrpc.client

url = "http://localhost:8069"
db = "odoo17_test"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*70)
print("🔧 SETUP: Creating Users for Employees")
print("="*70)

# Get employees
employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read',
    [[['is_agent', '=', True]]], {'fields': ['name', 'id', 'work_email', 'user_id']})

print(f"\nFound {len(employees)} agent employees")

for emp in employees:
    print(f"\n👤 Processing: {emp['name']}")
    
    if emp.get('user_id'):
        print(f"   ✅ Already has user ID: {emp['user_id'][0]}")
        continue
    
    # Create user
    try:
        user_login = emp['work_email'] or f"{emp['name'].lower().replace(' ', '.')}@example.ae"
        
        user_data = {
            'name': emp['name'],
            'login': user_login,
            'email': emp.get('work_email', user_login),
            'password': 'demo123',  # Default password
            'groups_id': [(6, 0, [])],  # Portal user (minimal permissions)
        }
        
        user_id = models.execute_kw(db, uid, password,
            'res.users', 'create', [user_data])
        
        # Link user to employee
        models.execute_kw(db, uid, password,
            'hr.employee', 'write',
            [[emp['id']], {'user_id': user_id}])
        
        print(f"   ✅ Created user: {user_login} (ID: {user_id})")
        print(f"   ✅ Linked to employee")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:200]}")

print("\n" + "="*70)
print("✅ SETUP COMPLETE!")
print("="*70)
print("\nNow run: python test_commission_integration.py")
