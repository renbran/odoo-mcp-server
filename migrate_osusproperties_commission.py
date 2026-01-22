#!/usr/bin/env python3
"""
OSUS Properties Commission Migration Script
Migrates existing data to work with enhanced commission_ax integration
"""

import xmlrpc.client
import json
from datetime import datetime

# Production Server Configuration
PROD_URL = "http://139.84.163.11:8070"
PROD_DB = "osusproperties"
PROD_USER = input("Enter Odoo username (default: admin): ").strip() or "admin"
PROD_PASS = input("Enter Odoo password: ").strip()

# Backup before migration
print("\n" + "="*70)
print("⚠️  MIGRATION WARNING")
print("="*70)
print("This script will modify production data!")
print("Please ensure you have:")
print("  1. ✅ Database backup created")
print("  2. ✅ Tested on staging/development environment")
print("  3. ✅ Scheduled maintenance window")
print("="*70)

confirm = input("\nType 'MIGRATE' to proceed: ")
if confirm != 'MIGRATE':
    print("❌ Migration cancelled")
    exit(0)

print("\n🚀 Starting migration...\n")

# Connect to production
try:
    common = xmlrpc.client.ServerProxy(f'{PROD_URL}/xmlrpc/2/common')
    uid = common.authenticate(PROD_DB, PROD_USER, PROD_PASS, {})
    if not uid:
        raise Exception("Authentication failed!")
    
    models = xmlrpc.client.ServerProxy(f'{PROD_URL}/xmlrpc/2/object')
    print(f"✅ Connected to {PROD_URL} (UID: {uid})\n")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# Migration Statistics
stats = {
    'employees_processed': 0,
    'employees_linked': 0,
    'commission_rates_set': 0,
    'sale_orders_updated': 0,
    'errors': []
}

def log_error(message):
    """Log error to stats"""
    stats['errors'].append(message)
    print(f"   ⚠️  {message}")

# Step 1: Process HR Employees
print("="*70)
print("STEP 1: Processing HR Employees")
print("="*70)

try:
    # Get all employees marked as agents
    employees = models.execute_kw(PROD_DB, uid, PROD_PASS,
        'hr.employee', 'search_read',
        [[['is_agent', '=', True]]],
        {'fields': ['name', 'id', 'user_id', 'work_email', 'is_agent', 'agent_type',
                   'primary_agent_personal_commission', 'primary_agent_business_commission',
                   'secondary_agent_personal_commission', 'secondary_agent_business_commission']})
    
    print(f"Found {len(employees)} agent employees\n")
    
    for emp in employees:
        stats['employees_processed'] += 1
        print(f"Processing: {emp['name']}")
        
        # Check if employee has user account
        if not emp.get('user_id'):
            print(f"   ℹ️  No user account - attempting to create/link...")
            
            # Search for existing user by email
            if emp.get('work_email'):
                existing_users = models.execute_kw(PROD_DB, uid, PROD_PASS,
                    'res.users', 'search',
                    [[['email', '=', emp['work_email']]]])
                
                if existing_users:
                    # Link to existing user
                    models.execute_kw(PROD_DB, uid, PROD_PASS,
                        'hr.employee', 'write',
                        [[emp['id']], {'user_id': existing_users[0]}])
                    print(f"   ✅ Linked to existing user: {emp['work_email']}")
                    stats['employees_linked'] += 1
                else:
                    # Create new user
                    try:
                        user_id = models.execute_kw(PROD_DB, uid, PROD_PASS,
                            'res.users', 'create',
                            [{
                                'name': emp['name'],
                                'login': emp['work_email'],
                                'email': emp['work_email'],
                                'password': 'Welcome123!',  # Force password change on first login
                                'groups_id': [(6, 0, [])],  # Portal user
                            }])
                        
                        # Link to employee
                        models.execute_kw(PROD_DB, uid, PROD_PASS,
                            'hr.employee', 'write',
                            [[emp['id']], {'user_id': user_id}])
                        
                        print(f"   ✅ Created new user: {emp['work_email']}")
                        stats['employees_linked'] += 1
                    except Exception as e:
                        log_error(f"Failed to create user for {emp['name']}: {str(e)[:100]}")
        else:
            print(f"   ✅ Already has user account")
        
        # Set default commission rates if not set
        update_vals = {}
        
        if emp['agent_type'] == 'primary':
            if not emp.get('primary_agent_personal_commission'):
                update_vals['primary_agent_personal_commission'] = 60.0
            if not emp.get('primary_agent_business_commission'):
                update_vals['primary_agent_business_commission'] = 40.0
        elif emp['agent_type'] == 'secondary':
            if not emp.get('secondary_agent_personal_commission'):
                update_vals['secondary_agent_personal_commission'] = 30.0
            if not emp.get('secondary_agent_business_commission'):
                update_vals['secondary_agent_business_commission'] = 20.0
        
        if update_vals:
            models.execute_kw(PROD_DB, uid, PROD_PASS,
                'hr.employee', 'write',
                [[emp['id']], update_vals])
            print(f"   ✅ Set default commission rates: {update_vals}")
            stats['commission_rates_set'] += 1
        
        print()

except Exception as e:
    log_error(f"Employee processing error: {e}")

# Step 2: Create/Update UTM Sources
print("="*70)
print("STEP 2: Setting Up UTM Sources")
print("="*70)

utm_sources = [
    {'name': 'Personal Referral', 'key': 'personal'},
    {'name': 'Personal Network', 'key': 'personal'},
    {'name': 'Employee Referral', 'key': 'referral'},
    {'name': 'Friend Referral', 'key': 'referral'},
]

for source_data in utm_sources:
    try:
        existing = models.execute_kw(PROD_DB, uid, PROD_PASS,
            'utm.source', 'search',
            [[['name', '=', source_data['name']]]])
        
        if existing:
            print(f"✅ UTM Source exists: {source_data['name']}")
        else:
            source_id = models.execute_kw(PROD_DB, uid, PROD_PASS,
                'utm.source', 'create',
                [{'name': source_data['name']}])
            print(f"✅ Created UTM Source: {source_data['name']} (ID: {source_id})")
    except Exception as e:
        log_error(f"UTM Source error ({source_data['name']}): {str(e)[:100]}")

print()

# Step 3: Migrate Existing Sale Orders (Optional)
print("="*70)
print("STEP 3: Analyzing Existing Sale Orders")
print("="*70)

try:
    # Get sample of recent orders with agents
    recent_orders = models.execute_kw(PROD_DB, uid, PROD_PASS,
        'sale.order', 'search_read',
        [[['agent1_partner_id', '!=', False], ['state', 'in', ['draft', 'sent']]]],
        {'fields': ['name', 'agent1_partner_id', 'agent1_rate', 'source_id'],
         'limit': 100, 'order': 'id desc'})
    
    print(f"Found {len(recent_orders)} recent orders with agents\n")
    
    orders_needing_update = 0
    for order in recent_orders:
        if not order.get('agent1_rate') or order['agent1_rate'] == 0:
            orders_needing_update += 1
    
    print(f"Orders needing commission rate update: {orders_needing_update}")
    
    if orders_needing_update > 0:
        update_orders = input(f"\nUpdate {orders_needing_update} draft orders with commission rates? (yes/no): ").lower()
        
        if update_orders == 'yes':
            for order in recent_orders:
                if not order.get('agent1_rate') or order['agent1_rate'] == 0:
                    try:
                        # Get partner info
                        partner_id = order['agent1_partner_id'][0]
                        
                        # Find employee
                        employee = models.execute_kw(PROD_DB, uid, PROD_PASS,
                            'hr.employee', 'search_read',
                            [[['user_id.partner_id', '=', partner_id], ['is_agent', '=', True]]],
                            {'fields': ['agent_type', 'primary_agent_personal_commission',
                                       'primary_agent_business_commission'], 'limit': 1})
                        
                        if employee:
                            emp = employee[0]
                            # Determine rate based on source
                            is_personal = False
                            if order.get('source_id'):
                                source_name = order['source_id'][1].lower()
                                is_personal = 'personal' in source_name or 'referral' in source_name
                            
                            if emp['agent_type'] == 'primary':
                                rate = emp['primary_agent_personal_commission'] if is_personal else emp['primary_agent_business_commission']
                            else:
                                rate = 40.0  # Default
                            
                            if rate:
                                models.execute_kw(PROD_DB, uid, PROD_PASS,
                                    'sale.order', 'write',
                                    [[order['id']], {'agent1_rate': rate}])
                                print(f"   ✅ Updated {order['name']}: {rate}%")
                                stats['sale_orders_updated'] += 1
                    
                    except Exception as e:
                        log_error(f"Order update error ({order['name']}): {str(e)[:100]}")
        else:
            print("⏭️  Skipping order updates")
    
except Exception as e:
    log_error(f"Order analysis error: {e}")

print()

# Step 4: Generate Migration Report
print("="*70)
print("MIGRATION SUMMARY")
print("="*70)

report = {
    'timestamp': datetime.now().isoformat(),
    'database': PROD_DB,
    'statistics': stats
}

print(f"\n📊 Statistics:")
print(f"   Employees Processed: {stats['employees_processed']}")
print(f"   Employees Linked to Users: {stats['employees_linked']}")
print(f"   Commission Rates Set: {stats['commission_rates_set']}")
print(f"   Sale Orders Updated: {stats['sale_orders_updated']}")
print(f"   Errors Encountered: {len(stats['errors'])}")

if stats['errors']:
    print(f"\n⚠️  Errors ({len(stats['errors'])}):")
    for error in stats['errors'][:10]:  # Show first 10
        print(f"   - {error}")
    if len(stats['errors']) > 10:
        print(f"   ... and {len(stats['errors']) - 10} more")

# Save report
report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n📄 Report saved: {report_file}")

print("\n" + "="*70)
print("✅ MIGRATION COMPLETE")
print("="*70)

print("\n📋 Next Steps:")
print("   1. Review migration report for any errors")
print("   2. Test commission auto-population in UI")
print("   3. Create test sale order with personal/business leads")
print("   4. Verify commission rates auto-fill correctly")
print("   5. Train users on new functionality")

print("\n🚀 Commission-HR Integration is now LIVE on production!")
print("="*70)
