#!/usr/bin/env python3
"""
Quick Test - Commission Integration
Tests the basic commission rate auto-population without complex scenarios
"""

import xmlrpc.client

# Connection
url = "http://localhost:8069"
db = "odoo17_test"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*70)
print("🎯 COMMISSION-HR INTEGRATION TEST")
print("="*70)

# 1. Create UTM sources (simplified - no description field)
print("\n📊 Creating UTM Sources...")
personal_source = models.execute_kw(db, uid, password,
    'utm.source', 'create', [{'name': 'Personal Referral'}])
business_source = models.execute_kw(db, uid, password,
    'utm.source', 'create', [{'name': 'Google Ads'}])
print(f"   ✅ Created: Personal Referral (ID: {personal_source})")
print(f"   ✅ Created: Google Ads (ID: {business_source})")

# 2. Get existing employees (created earlier)
print("\n👥 Finding Employees...")
employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read',
    [[['is_agent', '=', True]]], {'fields': ['name', 'id', 'agent_type']})
print(f"   Found {len(employees)} employees:")
for emp in employees:
    print(f"      - {emp['name']} (ID: {emp['id']}, Type: {emp.get('agent_type', 'N/A')})")

if len(employees) < 2:
    print("   ⚠️  Need at least 2 employees for testing!")
    exit(1)

# Get employee partner IDs
emp1_data = models.execute_kw(db, uid, password,
    'hr.employee', 'read',
    [employees[0]['id']], {'fields': ['name', 'user_id']})[0]

emp2_data = models.execute_kw(db, uid, password,
    'hr.employee', 'read',
    [employees[1]['id']], {'fields': ['name', 'user_id']})[0]

# Get partners from users
if emp1_data.get('user_id'):
    user1 = models.execute_kw(db, uid, password,
        'res.users', 'read',
        [emp1_data['user_id'][0]], {'fields': ['partner_id']})[0]
    partner1_id = user1['partner_id'][0]
    print(f"\n   ✅ Employee 1: {emp1_data['name']} → Partner ID: {partner1_id}")
else:
    print(f"\n   ❌ Employee 1 has no user/partner!")
    partner1_id = None

if emp2_data.get('user_id'):
    user2 = models.execute_kw(db, uid, password,
        'res.users', 'read',
        [emp2_data['user_id'][0]], {'fields': ['partner_id']})[0]
    partner2_id = user2['partner_id'][0]
    print(f"   ✅ Employee 2: {emp2_data['name']} → Partner ID: {partner2_id}")
else:
    print(f"   ❌ Employee 2 has no user/partner!")
    partner2_id = None

# 3. Get existing customer
print("\n👤 Finding Customers...")
customers = models.execute_kw(db, uid, password,
    'res.partner', 'search',
    [[['customer_rank', '>', 0]]], {'limit': 1})

if customers:
    customer_id = customers[0]
    customer_data = models.execute_kw(db, uid, password,
        'res.partner', 'read',
        [customer_id], {'fields': ['name']})[0]
    print(f"   ✅ Using customer: {customer_data['name']} (ID: {customer_id})")
else:
    print("   ℹ️  No customers found, creating one...")
    customer_id = models.execute_kw(db, uid, password,
        'res.partner', 'create',
        [{'name': 'Test Customer LLC', 'is_company': True}])
    print(f"   ✅ Created customer ID: {customer_id}")

# 4. Get existing product
print("\n📦 Finding Products...")
products = models.execute_kw(db, uid, password,
    'product.product', 'search',
    [[('sale_ok', '=', True)]], {'limit': 1})

if products:
    product_id = products[0]
    product_data = models.execute_kw(db, uid, password,
        'product.product', 'read',
        [product_id], {'fields': ['name', 'list_price']})[0]
    print(f"   ✅ Using product: {product_data['name']} (Price: {product_data['list_price']})")
else:
    print("   ℹ️  No products found, creating one...")
    product_id = models.execute_kw(db, uid, password,
        'product.product', 'create',
        [{'name': 'Test Property', 'list_price': 1000000.00, 'type': 'service'}])
    print(f"   ✅ Created product ID: {product_id}")

# 5. Create sale orders with commission testing
print("\n💰 Creating Test Sale Orders...")
print("="*70)

if partner1_id:
    print("\n📝 TEST 1: Personal Lead with Agent 1")
    order1_data = {
        'partner_id': customer_id,
        'source_id': personal_source,
        'agent1_partner_id': partner1_id,  # Fixed field name
        'order_line': [(0, 0, {
            'product_id': product_id,
            'product_uom_qty': 1,
        })],
    }
    
    try:
        order1_id = models.execute_kw(db, uid, password,
            'sale.order', 'create', [order1_data])
        
        order1 = models.execute_kw(db, uid, password,
            'sale.order', 'read',
            [order1_id], {'fields': ['name', 'agent1_rate']})[0]
        
        print(f"   ✅ Created: {order1['name']}")
        print(f"   📊 Agent 1 Rate: {order1.get('agent1_rate', 0)}% (Expected: 60%)")
        
        if order1.get('agent1_rate') == 60.0:
            print("   🎉 SUCCESS! Commission rate auto-populated correctly!")
        else:
            print("   ⚠️  Rate doesn't match expected value")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:200]}")

if partner2_id:
    print("\n📝 TEST 2: Business Lead with Agent 2")
    order2_data = {
        'partner_id': customer_id,
        'source_id': business_source,
        'agent1_partner_id': partner2_id,  # Fixed field name
        'order_line': [(0, 0, {
            'product_id': product_id,
            'product_uom_qty': 1,
        })],
    }
    
    try:
        order2_id = models.execute_kw(db, uid, password,
            'sale.order', 'create', [order2_data])
        
        order2 = models.execute_kw(db, uid, password,
            'sale.order', 'read',
            [order2_id], {'fields': ['name', 'agent1_rate']})[0]
        
        print(f"   ✅ Created: {order2['name']}")
        print(f"   📊 Agent 1 Rate: {order2.get('agent1_rate', 0)}% (Expected: 40%)")
        
        if order2.get('agent1_rate') == 40.0:
            print("   🎉 SUCCESS! Commission rate auto-populated correctly!")
        else:
            print("   ⚠️  Rate doesn't match expected value")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:200]}")

print("\n" + "="*70)
print("✅ TEST COMPLETE!")
print("="*70)
print("\n🌐 View Results:")
print("   Open: http://localhost:8069")
print("   Navigate to: Sales → Orders")
print("   Check the commission rates on newly created orders")
print("="*70)
