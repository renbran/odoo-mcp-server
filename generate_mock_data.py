#!/usr/bin/env python3
"""
Generate Mock Data for Commission-HR Integration Testing
Creates realistic test data to verify commission rate auto-population
"""

import xmlrpc.client
import time
from datetime import datetime, timedelta

# Connection settings
url = "http://localhost:8069"
db = "odoo17_test"
username = "admin"
password = "admin"

def connect():
    """Connect to Odoo"""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("Authentication failed!")
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print(f"✅ Connected to Odoo (UID: {uid})")
    return uid, models

def create_utm_sources(uid, models):
    """Create UTM sources for personal and business leads"""
    print("\n📊 Creating UTM Sources...")
    
    sources = [
        {'name': 'Personal Referral', 'description': 'Personal network referrals'},
        {'name': 'Personal Network', 'description': 'Direct personal connections'},
        {'name': 'Employee Referral', 'description': 'Referred by employees'},
        {'name': 'Google Ads', 'description': 'Business lead from Google'},
        {'name': 'Website Contact Form', 'description': 'Business lead from website'},
        {'name': 'Cold Call', 'description': 'Business development calls'},
        {'name': 'Trade Show', 'description': 'Business networking events'},
    ]
    
    created_sources = {}
    for source_data in sources:
        try:
            # Check if exists
            existing = models.execute_kw(
                db, uid, password,
                'utm.source', 'search',
                [[['name', '=', source_data['name']]]]
            )
            
            if existing:
                source_id = existing[0]
                print(f"   ℹ️  UTM Source '{source_data['name']}' already exists")
            else:
                source_id = models.execute_kw(
                    db, uid, password,
                    'utm.source', 'create',
                    [source_data]
                )
                print(f"   ✅ Created UTM Source: {source_data['name']}")
            
            created_sources[source_data['name']] = source_id
        except Exception as e:
            print(f"   ❌ Error creating source {source_data['name']}: {e}")
    
    return created_sources

def create_employees(uid, models):
    """Create HR employees with agent commission settings"""
    print("\n👥 Creating HR Employees with Commission Settings...")
    
    employees = [
        {
            'name': 'Ahmed Al-Rashid',
            'job_title': 'Senior Sales Agent',
            'work_email': 'ahmed.alrashid@company.ae',
            'work_phone': '+971 50 123 4567',
            'is_agent': True,
            'agent_type': 'primary',
            'primary_agent_personal_commission': 60.0,
            'primary_agent_business_commission': 40.0,
        },
        {
            'name': 'Fatima Hassan',
            'job_title': 'Sales Executive',
            'work_email': 'fatima.hassan@company.ae',
            'work_phone': '+971 50 234 5678',
            'is_agent': True,
            'agent_type': 'primary',
            'primary_agent_personal_commission': 60.0,
            'primary_agent_business_commission': 40.0,
        },
        {
            'name': 'Mohammed Abdullah',
            'job_title': 'Junior Sales Agent',
            'work_email': 'mohammed.abdullah@company.ae',
            'work_phone': '+971 50 345 6789',
            'is_agent': True,
            'agent_type': 'secondary',
            'secondary_agent_personal_commission': 30.0,
            'secondary_agent_business_commission': 20.0,
        },
        {
            'name': 'Sarah Al-Maktoum',
            'job_title': 'Sales Manager',
            'work_email': 'sarah.almaktoum@company.ae',
            'work_phone': '+971 50 456 7890',
            'is_agent': True,
            'agent_type': 'exclusive_rm',
            'exclusive_rm_personal_commission': 5.0,
            'exclusive_rm_business_commission': 5.0,
        },
        {
            'name': 'Khalid Ibrahim',
            'job_title': 'Sales Director',
            'work_email': 'khalid.ibrahim@company.ae',
            'work_phone': '+971 50 567 8901',
            'is_agent': True,
            'agent_type': 'exclusive_sm',
            'exclusive_sm_personal_commission': 2.0,
            'exclusive_sm_business_commission': 2.0,
        },
    ]
    
    created_employees = {}
    for emp_data in employees:
        try:
            # Check if exists
            existing = models.execute_kw(
                db, uid, password,
                'hr.employee', 'search',
                [[['name', '=', emp_data['name']]]]
            )
            
            if existing:
                emp_id = existing[0]
                # Update with commission settings
                models.execute_kw(
                    db, uid, password,
                    'hr.employee', 'write',
                    [emp_id, emp_data]
                )
                print(f"   ✅ Updated Employee: {emp_data['name']} ({emp_data['agent_type']})")
            else:
                emp_id = models.execute_kw(
                    db, uid, password,
                    'hr.employee', 'create',
                    [emp_data]
                )
                print(f"   ✅ Created Employee: {emp_data['name']} ({emp_data['agent_type']})")
            
            created_employees[emp_data['name']] = emp_id
        except Exception as e:
            print(f"   ❌ Error with employee {emp_data['name']}: {e}")
    
    return created_employees

def create_partners(uid, models, employees):
    """Create partners for employees"""
    print("\n🤝 Creating Partner Records for Employees...")
    
    employee_partners = {}
    for emp_name, emp_id in employees.items():
        try:
            # Get employee data
            emp_data = models.execute_kw(
                db, uid, password,
                'hr.employee', 'read',
                [emp_id], {'fields': ['work_email', 'work_phone', 'user_id', 'address_home_id']}
            )[0]
            
            # Check if employee has a partner
            if emp_data.get('user_id'):
                user_data = models.execute_kw(
                    db, uid, password,
                    'res.users', 'read',
                    [emp_data['user_id'][0]], {'fields': ['partner_id']}
                )[0]
                partner_id = user_data['partner_id'][0]
                employee_partners[emp_name] = partner_id
                print(f"   ✅ Using existing partner for {emp_name}")
            elif emp_data.get('address_home_id'):
                partner_id = emp_data['address_home_id'][0]
                employee_partners[emp_name] = partner_id
                print(f"   ✅ Using home address partner for {emp_name}")
            else:
                # Create partner
                partner_id = models.execute_kw(
                    db, uid, password,
                    'res.partner', 'create',
                    [{
                        'name': emp_name,
                        'email': emp_data.get('work_email', ''),
                        'phone': emp_data.get('work_phone', ''),
                        'is_company': False,
                        'employee': True,
                    }]
                )
                
                # Link to employee
                models.execute_kw(
                    db, uid, password,
                    'hr.employee', 'write',
                    [emp_id, {'address_home_id': partner_id}]
                )
                
                employee_partners[emp_name] = partner_id
                print(f"   ✅ Created partner for {emp_name}")
                
        except Exception as e:
            print(f"   ❌ Error creating partner for {emp_name}: {e}")
    
    return employee_partners

def create_customers(uid, models):
    """Create customer partners"""
    print("\n👤 Creating Customer Partners...")
    
    customers = [
        {'name': 'Al-Mansour Trading LLC', 'email': 'info@almansour.ae', 'phone': '+971 4 123 4567', 'is_company': True},
        {'name': 'Dubai Properties Group', 'email': 'contact@dubaiproperties.ae', 'phone': '+971 4 234 5678', 'is_company': True},
        {'name': 'Emirates Construction Co.', 'email': 'sales@emiratesconstruction.ae', 'phone': '+971 4 345 6789', 'is_company': True},
        {'name': 'Sheikh Abdullah Al-Nahyan', 'email': 'abdullah@example.ae', 'phone': '+971 50 111 2222', 'is_company': False},
        {'name': 'Ms. Noora Al-Blooshi', 'email': 'noora.alblooshi@example.ae', 'phone': '+971 50 222 3333', 'is_company': False},
    ]
    
    created_customers = {}
    for cust_data in customers:
        try:
            # Check if exists
            existing = models.execute_kw(
                db, uid, password,
                'res.partner', 'search',
                [[['name', '=', cust_data['name']]]]
            )
            
            if existing:
                cust_id = existing[0]
                print(f"   ℹ️  Customer '{cust_data['name']}' already exists")
            else:
                cust_id = models.execute_kw(
                    db, uid, password,
                    'res.partner', 'create',
                    [cust_data]
                )
                print(f"   ✅ Created Customer: {cust_data['name']}")
            
            created_customers[cust_data['name']] = cust_id
        except Exception as e:
            print(f"   ❌ Error creating customer {cust_data['name']}: {e}")
    
    return created_customers

def create_products(uid, models):
    """Create products for sale orders"""
    print("\n📦 Creating Products...")
    
    products = [
        {'name': 'Premium Office Space', 'list_price': 150000.00, 'type': 'service'},
        {'name': 'Residential Villa', 'list_price': 2500000.00, 'type': 'consu'},
        {'name': 'Commercial Plot', 'list_price': 5000000.00, 'type': 'consu'},
        {'name': 'Luxury Apartment', 'list_price': 1800000.00, 'type': 'consu'},
        {'name': 'Warehouse Facility', 'list_price': 3500000.00, 'type': 'service'},
    ]
    
    created_products = {}
    for prod_data in products:
        try:
            # Check if exists
            existing = models.execute_kw(
                db, uid, password,
                'product.product', 'search',
                [[['name', '=', prod_data['name']]]]
            )
            
            if existing:
                prod_id = existing[0]
                print(f"   ℹ️  Product '{prod_data['name']}' already exists")
            else:
                prod_id = models.execute_kw(
                    db, uid, password,
                    'product.product', 'create',
                    [prod_data]
                )
                print(f"   ✅ Created Product: {prod_data['name']}")
            
            created_products[prod_data['name']] = prod_id
        except Exception as e:
            print(f"   ❌ Error creating product {prod_data['name']}: {e}")
    
    return created_products

def create_sale_orders(uid, models, sources, employees, employee_partners, customers, products):
    """Create sale orders to test commission integration"""
    print("\n💰 Creating Sale Orders with Commission Testing...")
    
    test_cases = [
        {
            'name': 'Test Case 1: Personal Lead - Primary Agent (60%)',
            'customer': 'Sheikh Abdullah Al-Nahyan',
            'product': 'Luxury Apartment',
            'source': 'Personal Referral',
            'agent1': 'Ahmed Al-Rashid',
            'expected_rate': 60.0,
        },
        {
            'name': 'Test Case 2: Business Lead - Primary Agent (40%)',
            'customer': 'Al-Mansour Trading LLC',
            'product': 'Premium Office Space',
            'source': 'Google Ads',
            'agent1': 'Fatima Hassan',
            'expected_rate': 40.0,
        },
        {
            'name': 'Test Case 3: Personal Lead - Secondary Agent (30%)',
            'customer': 'Ms. Noora Al-Blooshi',
            'product': 'Residential Villa',
            'source': 'Personal Network',
            'agent2': 'Mohammed Abdullah',
            'expected_rate2': 30.0,
        },
        {
            'name': 'Test Case 4: Multi-Agent Commission',
            'customer': 'Dubai Properties Group',
            'product': 'Commercial Plot',
            'source': 'Employee Referral',
            'agent1': 'Ahmed Al-Rashid',
            'agent2': 'Mohammed Abdullah',
            'manager': 'Sarah Al-Maktoum',
            'director': 'Khalid Ibrahim',
            'expected_rate': 60.0,
            'expected_rate2': 30.0,
            'expected_manager_rate': 5.0,
            'expected_director_rate': 2.0,
        },
        {
            'name': 'Test Case 5: Business Lead - Multi-Agent',
            'customer': 'Emirates Construction Co.',
            'product': 'Warehouse Facility',
            'source': 'Trade Show',
            'agent1': 'Fatima Hassan',
            'manager': 'Sarah Al-Maktoum',
            'expected_rate': 40.0,
            'expected_manager_rate': 5.0,
        },
    ]
    
    created_orders = []
    for idx, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n   📝 {test_case['name']}")
            
            # Prepare order data
            order_data = {
                'partner_id': customers[test_case['customer']],
                'source_id': sources.get(test_case['source']),
                'order_line': [(0, 0, {
                    'product_id': products[test_case['product']],
                    'product_uom_qty': 1,
                })],
            }
            
            # Add agents
            if 'agent1' in test_case:
                order_data['agent1_partner'] = employee_partners[test_case['agent1']]
            if 'agent2' in test_case:
                order_data['agent2_partner'] = employee_partners[test_case['agent2']]
            if 'manager' in test_case:
                order_data['manager_partner'] = employee_partners[test_case['manager']]
            if 'director' in test_case:
                order_data['director_partner'] = employee_partners[test_case['director']]
            
            # Create order
            order_id = models.execute_kw(
                db, uid, password,
                'sale.order', 'create',
                [order_data]
            )
            
            # Read back the order to check commission rates
            order = models.execute_kw(
                db, uid, password,
                'sale.order', 'read',
                [order_id], {
                    'fields': ['name', 'agent1_rate', 'agent2_rate', 'manager_rate', 'director_rate']
                }
            )[0]
            
            print(f"      ✅ Created: {order['name']}")
            
            # Verify commission rates
            if 'expected_rate' in test_case:
                actual_rate = order.get('agent1_rate', 0)
                if actual_rate == test_case['expected_rate']:
                    print(f"      ✅ Agent 1 Rate: {actual_rate}% (Expected: {test_case['expected_rate']}%) ✓")
                else:
                    print(f"      ❌ Agent 1 Rate: {actual_rate}% (Expected: {test_case['expected_rate']}%) ✗")
            
            if 'expected_rate2' in test_case:
                actual_rate = order.get('agent2_rate', 0)
                if actual_rate == test_case['expected_rate2']:
                    print(f"      ✅ Agent 2 Rate: {actual_rate}% (Expected: {test_case['expected_rate2']}%) ✓")
                else:
                    print(f"      ❌ Agent 2 Rate: {actual_rate}% (Expected: {test_case['expected_rate2']}%) ✗")
            
            if 'expected_manager_rate' in test_case:
                actual_rate = order.get('manager_rate', 0)
                if actual_rate == test_case['expected_manager_rate']:
                    print(f"      ✅ Manager Rate: {actual_rate}% (Expected: {test_case['expected_manager_rate']}%) ✓")
                else:
                    print(f"      ❌ Manager Rate: {actual_rate}% (Expected: {test_case['expected_manager_rate']}%) ✗")
            
            if 'expected_director_rate' in test_case:
                actual_rate = order.get('director_rate', 0)
                if actual_rate == test_case['expected_director_rate']:
                    print(f"      ✅ Director Rate: {actual_rate}% (Expected: {test_case['expected_director_rate']}%) ✓")
                else:
                    print(f"      ❌ Director Rate: {actual_rate}% (Expected: {test_case['expected_director_rate']}%) ✗")
            
            created_orders.append(order_id)
            
        except Exception as e:
            print(f"      ❌ Error creating order: {e}")
    
    return created_orders

def main():
    """Main data generation process"""
    print("=" * 70)
    print("🎯 COMMISSION-HR INTEGRATION MOCK DATA GENERATOR")
    print("=" * 70)
    
    try:
        # Connect
        uid, models = connect()
        
        # Create test data
        sources = create_utm_sources(uid, models)
        employees = create_employees(uid, models)
        employee_partners = create_partners(uid, models, employees)
        customers = create_customers(uid, models)
        products = create_products(uid, models)
        orders = create_sale_orders(uid, models, sources, employees, employee_partners, customers, products)
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 GENERATION SUMMARY")
        print("=" * 70)
        print(f"✅ UTM Sources: {len(sources)}")
        print(f"✅ HR Employees: {len(employees)}")
        print(f"✅ Employee Partners: {len(employee_partners)}")
        print(f"✅ Customers: {len(customers)}")
        print(f"✅ Products: {len(products)}")
        print(f"✅ Sale Orders: {len(orders)}")
        print("=" * 70)
        
        print("\n🎉 Mock data generation completed!")
        print("\n📋 Next Steps:")
        print("   1. Open http://localhost:8069")
        print("   2. Go to Sales → Orders")
        print("   3. Check the commission rates on each order")
        print("   4. Verify auto-population based on lead source")
        print("   5. Try changing the UTM source and see rates update")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
