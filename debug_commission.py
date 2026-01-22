#!/usr/bin/env python3
"""
Debug commission integration - detailed output
"""
import xmlrpc.client
import json

url = "http://localhost:8069"
db = "odoo17_test"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("="*70)
print("🔍 DETAILED COMMISSION INTEGRATION DEBUG")
print("="*70)

# Get an employee with user
employees = models.execute_kw(db, uid, password,
    'hr.employee', 'search_read',
    [[['is_agent', '=', True], ['user_id', '!=', False]]], 
    {'fields': ['name', 'id', 'user_id', 'is_agent', 'agent_type',
                'primary_agent_personal_commission', 'primary_agent_business_commission',
                'secondary_agent_personal_commission', 'secondary_agent_business_commission'],
     'limit': 1})

if not employees:
    print("❌ No employees with users found!")
    exit(1)

emp = employees[0]
print(f"\n✅ Using Employee: {emp['name']}")
print(f"   ID: {emp['id']}")
print(f"   Agent Type: {emp.get('agent_type', 'N/A')}")
print(f"   Is Agent: {emp.get('is_agent')}")
print(f"   Primary Personal: {emp.get('primary_agent_personal_commission', 0)}%")
print(f"   Primary Business: {emp.get('primary_agent_business_commission', 0)}%")
print(f"   Secondary Personal: {emp.get('secondary_agent_personal_commission', 0)}%")
print(f"   Secondary Business: {emp.get('secondary_agent_business_commission', 0)}%")

# Get partner from user
user = models.execute_kw(db, uid, password,
    'res.users', 'read',
    [emp['user_id'][0]], {'fields': ['partner_id', 'name']})[0]

partner_id = user['partner_id'][0]
print(f"\n✅ Partner: {user['name']} (ID: {partner_id})")

# Get UTM source
sources = models.execute_kw(db, uid, password,
    'utm.source', 'search_read',
    [[['name', 'ilike', 'personal']]], {'limit': 1})

if not sources:
    source_id = models.execute_kw(db, uid, password,
        'utm.source', 'create',
        [{'name': 'Personal Lead Test'}])
    print(f"\n✅ Created UTM Source: Personal Lead Test (ID: {source_id})")
else:
    source_id = sources[0]['id']
    print(f"\n✅ Using UTM Source: {sources[0]['name']} (ID: {source_id})")

# Get customer
customer = models.execute_kw(db, uid, password,
    'res.partner', 'search',
    [[['customer_rank', '>', 0]]], {'limit': 1})[0]

# Get product
product = models.execute_kw(db, uid, password,
    'product.product', 'search',
    [[['sale_ok', '=', True]]], {'limit': 1})[0]

print(f"\n📝 Creating Sale Order...")
print(f"   Customer ID: {customer}")
print(f"   Product ID: {product}")
print(f"   Agent Partner ID: {partner_id}")
print(f"   Source ID: {source_id}")

# Create order
order_data = {
    'partner_id': customer,
    'source_id': source_id,
    'agent1_partner_id': partner_id,
    'order_line': [(0, 0, {
        'product_id': product,
        'product_uom_qty': 1,
    })],
}

print(f"\n📤 Order Data:")
print(json.dumps(order_data, indent=2))

try:
    order_id = models.execute_kw(db, uid, password,
        'sale.order', 'create',
        [order_data])
    
    print(f"\n✅ Order Created: {order_id}")
    
    # Read order back
    order = models.execute_kw(db, uid, password,
        'sale.order', 'read',
        [order_id], {
            'fields': ['name', 'partner_id', 'source_id', 'agent1_partner_id', 
                      'agent1_rate', 'agent1_commission_type', 'agent1_calculation_base']
        })[0]
    
    print(f"\n📊 ORDER DETAILS:")
    print(f"   Name: {order['name']}")
    print(f"   Customer: {order['partner_id'][1] if order.get('partner_id') else 'N/A'}")
    print(f"   Source: {order['source_id'][1] if order.get('source_id') else 'N/A'}")
    print(f"   Agent: {order['agent1_partner_id'][1] if order.get('agent1_partner_id') else 'N/A'}")
    print(f"   Agent1 Rate: {order.get('agent1_rate', 0)}%")
    print(f"   Commission Type: {order.get('agent1_commission_type', 'N/A')}")
    print(f"   Calculation Base: {order.get('agent1_calculation_base', 'N/A')}")
    
    if order.get('agent1_rate') == 60.0:
        print(f"\n🎉 SUCCESS! Commission auto-populated correctly (60% for personal lead)!")
    elif order.get('agent1_rate') == 0.0:
        print(f"\n⚠️  FAILURE: Commission rate is 0%")
        print(f"\n🔍 Possible Issues:")
        print(f"   1. Onchange method not triggered during create")
        print(f"   2. Employee not found by partner search")
        print(f"   3. Field names mismatch")
        print(f"   4. Agent type or is_agent check failing")
    else:
        print(f"\n⚠️  Unexpected rate: {order.get('agent1_rate')}%")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
