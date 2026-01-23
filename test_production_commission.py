#!/usr/bin/env python3
"""
Production Commission Integration Test
Tests commission auto-population on OSUS Properties production server
"""

import xmlrpc.client
import json
from datetime import datetime

# Production configuration
PROD_URL = 'http://139.84.163.11:8070'
PROD_DB = 'osusproperties'
PROD_USER = input('Enter username: ')
PROD_PASS = input('Enter password: ')

def connect():
    """Connect to production Odoo"""
    common = xmlrpc.client.ServerProxy(f'{PROD_URL}/xmlrpc/2/common')
    uid = common.authenticate(PROD_DB, PROD_USER, PROD_PASS, {})
    
    if not uid:
        raise Exception("Authentication failed!")
    
    models = xmlrpc.client.ServerProxy(f'{PROD_URL}/xmlrpc/2/object')
    print(f"✓ Connected to {PROD_DB} (UID: {uid})\n")
    return uid, models

def execute(models, uid, model, method, *args, **kwargs):
    """Execute Odoo method"""
    return models.execute_kw(PROD_DB, uid, PROD_PASS, model, method, args, kwargs)

def test_employee_agent_setup(models, uid):
    """Check if employees have agent settings"""
    print("=" * 80)
    print("TEST 1: Employee Agent Configuration")
    print("=" * 80)
    
    # Find employees with users
    employees = execute(models, uid, 'hr.employee', 'search_read',
                       [('user_id', '!=', False)],
                       {'fields': ['name', 'user_id', 'is_agent', 
                                  'primary_agent_personal_commission',
                                  'primary_agent_business_commission'],
                        'limit': 10})
    
    print(f"Employees with user accounts: {len(employees)}\n")
    
    for emp in employees:
        print(f"Employee: {emp['name']}")
        print(f"  User ID: {emp['user_id'][0]}")
        print(f"  Is Agent: {emp.get('is_agent', False)}")
        print(f"  Personal Rate: {emp.get('primary_agent_personal_commission', 0)}%")
        print(f"  Business Rate: {emp.get('primary_agent_business_commission', 0)}%")
        print()
    
    return employees

def test_utm_sources(models, uid):
    """Verify UTM sources exist"""
    print("=" * 80)
    print("TEST 2: UTM Source Configuration")
    print("=" * 80)
    
    # Get personal/referral sources
    personal_sources = execute(models, uid, 'utm.source', 'search_read',
                              ['|', ('name', 'ilike', 'personal'), ('name', 'ilike', 'referral')],
                              {'fields': ['name'], 'limit': 10})
    
    print(f"Personal/Referral Sources: {len(personal_sources)}\n")
    for src in personal_sources:
        print(f"  - {src['name']} (ID: {src['id']})")
    
    # Get a business source
    business_sources = execute(models, uid, 'utm.source', 'search_read',
                              [('name', 'not ilike', 'personal'), ('name', 'not ilike', 'referral')],
                              {'fields': ['name'], 'limit': 5})
    
    print(f"\nBusiness Sources (sample): {len(business_sources)}\n")
    for src in business_sources[:3]:
        print(f"  - {src['name']} (ID: {src['id']})")
    
    return personal_sources[0] if personal_sources else None, business_sources[0] if business_sources else None

def test_create_order_personal(models, uid, employee, personal_source):
    """Test creating order with personal lead"""
    print("\n" + "=" * 80)
    print("TEST 3: Create Sale Order with Personal Lead")
    print("=" * 80)
    
    # Get customer
    partners = execute(models, uid, 'res.partner', 'search_read',
                      [('customer_rank', '>', 0)],
                      {'fields': ['name'], 'limit': 1})
    
    if not partners:
        print("⚠ No customers found, skipping test")
        return None
    
    customer = partners[0]
    
    # Get product
    products = execute(models, uid, 'product.product', 'search_read',
                      [('sale_ok', '=', True)],
                      {'fields': ['name', 'list_price'], 'limit': 1})
    
    if not products:
        print("⚠ No products found, skipping test")
        return None
    
    product = products[0]
    
    # Get employee's partner
    users = execute(models, uid, 'res.users', 'read',
                   [employee['user_id'][0]],
                   {'fields': ['partner_id']})
    
    if not users:
        print("⚠ User not found, skipping test")
        return None
    
    agent_partner_id = users[0]['partner_id'][0]
    
    print(f"Creating order:")
    print(f"  Customer: {customer['name']}")
    print(f"  Product: {product['name']} (${product['list_price']})")
    print(f"  Agent: {employee['name']} (Partner ID: {agent_partner_id})")
    print(f"  Source: {personal_source['name']} (PERSONAL - expect 60%)")
    
    # Create sale order
    order_vals = {
        'partner_id': customer['id'],
        'source_id': personal_source['id'],
        'agent1_partner_id': agent_partner_id,
        'order_line': [(0, 0, {
            'product_id': product['id'],
            'product_uom_qty': 1,
            'price_unit': product['list_price'],
        })]
    }
    
    try:
        order_id = execute(models, uid, 'sale.order', 'create', order_vals)
        
        # Read created order
        order = execute(models, uid, 'sale.order', 'read',
                       [order_id],
                       {'fields': ['name', 'agent1_partner_id', 'agent1_rate', 
                                  'source_id', 'amount_total']})[0]
        
        print(f"\n✅ Order Created: {order['name']}")
        print(f"   Agent 1 Rate: {order.get('agent1_rate', 0)}%")
        
        if order.get('agent1_rate') == 60:
            print("   ✅ SUCCESS: Personal lead auto-filled 60% commission!")
        elif order.get('agent1_rate') > 0:
            print(f"   ⚠ PARTIAL: Commission rate {order.get('agent1_rate')}% (expected 60%)")
        else:
            print("   ❌ FAILED: Commission rate not auto-populated")
        
        return order
        
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        return None

def test_create_order_business(models, uid, employee, business_source):
    """Test creating order with business lead"""
    print("\n" + "=" * 80)
    print("TEST 4: Create Sale Order with Business Lead")
    print("=" * 80)
    
    # Get customer
    partners = execute(models, uid, 'res.partner', 'search_read',
                      [('customer_rank', '>', 0)],
                      {'fields': ['name'], 'limit': 1, 'offset': 1})
    
    if not partners:
        print("⚠ No customers found, skipping test")
        return None
    
    customer = partners[0]
    
    # Get product
    products = execute(models, uid, 'product.product', 'search_read',
                      [('sale_ok', '=', True)],
                      {'fields': ['name', 'list_price'], 'limit': 1, 'offset': 1})
    
    if not products:
        products = execute(models, uid, 'product.product', 'search_read',
                          [('sale_ok', '=', True)],
                          {'fields': ['name', 'list_price'], 'limit': 1})
    
    product = products[0]
    
    # Get employee's partner
    users = execute(models, uid, 'res.users', 'read',
                   [employee['user_id'][0]],
                   {'fields': ['partner_id']})
    
    agent_partner_id = users[0]['partner_id'][0]
    
    print(f"Creating order:")
    print(f"  Customer: {customer['name']}")
    print(f"  Product: {product['name']} (${product['list_price']})")
    print(f"  Agent: {employee['name']} (Partner ID: {agent_partner_id})")
    print(f"  Source: {business_source['name']} (BUSINESS - expect 40%)")
    
    # Create sale order
    order_vals = {
        'partner_id': customer['id'],
        'source_id': business_source['id'],
        'agent1_partner_id': agent_partner_id,
        'order_line': [(0, 0, {
            'product_id': product['id'],
            'product_uom_qty': 1,
            'price_unit': product['list_price'],
        })]
    }
    
    try:
        order_id = execute(models, uid, 'sale.order', 'create', order_vals)
        
        # Read created order
        order = execute(models, uid, 'sale.order', 'read',
                       [order_id],
                       {'fields': ['name', 'agent1_partner_id', 'agent1_rate',
                                  'source_id', 'amount_total']})[0]
        
        print(f"\n✅ Order Created: {order['name']}")
        print(f"   Agent 1 Rate: {order.get('agent1_rate', 0)}%")
        
        if order.get('agent1_rate') == 40:
            print("   ✅ SUCCESS: Business lead auto-filled 40% commission!")
        elif order.get('agent1_rate') > 0:
            print(f"   ⚠ PARTIAL: Commission rate {order.get('agent1_rate')}% (expected 40%)")
        else:
            print("   ❌ FAILED: Commission rate not auto-populated")
        
        return order
        
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        return None

def main():
    """Main test flow"""
    print("=" * 80)
    print("PRODUCTION COMMISSION INTEGRATION TEST")
    print("=" * 80)
    print()
    
    try:
        uid, models = connect()
        
        # Test 1: Check employee setup
        employees = test_employee_agent_setup(models, uid)
        
        if not employees:
            print("\n⚠ No employees with users found. Cannot test commission auto-fill.")
            print("   Run migration script first to link employees to users.")
            return
        
        # Test 2: Check UTM sources
        personal_src, business_src = test_utm_sources(models, uid)
        
        if not personal_src or not business_src:
            print("\n⚠ Required UTM sources not found. Cannot test.")
            return
        
        # Use first employee for tests
        test_employee = employees[0]
        
        # Test 3: Personal lead
        personal_order = test_create_order_personal(models, uid, test_employee, personal_src)
        
        # Test 4: Business lead
        business_order = test_create_order_business(models, uid, test_employee, business_src)
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'database': PROD_DB,
            'employees_tested': len(employees),
            'personal_order': personal_order['name'] if personal_order else 'FAILED',
            'personal_rate': personal_order.get('agent1_rate', 0) if personal_order else 0,
            'business_order': business_order['name'] if business_order else 'FAILED',
            'business_rate': business_order.get('agent1_rate', 0) if business_order else 0,
        }
        
        # Save report
        filename = f"production_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Test completed - Report saved: {filename}")
        
        if personal_order and personal_order.get('agent1_rate') == 60:
            if business_order and business_order.get('agent1_rate') == 40:
                print("\n🎉 ALL TESTS PASSED - Commission auto-population working perfectly!")
            else:
                print("\n⚠ PARTIAL SUCCESS - Personal works, business needs review")
        else:
            print("\n❌ TESTS FAILED - Commission auto-population not working as expected")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
