#!/usr/bin/env python3
"""
OSUS Properties Database Inspection Script
Analyzes the production database to identify potential issues before deploying enhanced modules
"""

import xmlrpc.client
import json
from datetime import datetime
from collections import defaultdict

# Production server configuration
print("Enter OSUS Properties credentials:")
PROD_CONFIG = {
    'url': input('URL (default: http://139.84.163.11:8070): ') or 'http://139.84.163.11:8070',
    'db': input('Database (default: osusproperties): ') or 'osusproperties',
    'username': input('Username (default: admin): ') or 'admin',
    'password': input('Password: ')
}

def connect_odoo():
    """Connect to Odoo and authenticate"""
    common = xmlrpc.client.ServerProxy(f"{PROD_CONFIG['url']}/xmlrpc/2/common")
    uid = common.authenticate(
        PROD_CONFIG['db'],
        PROD_CONFIG['username'],
        PROD_CONFIG['password'],
        {}
    )
    
    if not uid:
        raise Exception("Authentication failed!")
    
    models = xmlrpc.client.ServerProxy(f"{PROD_CONFIG['url']}/xmlrpc/2/object")
    print(f"✓ Connected to {PROD_CONFIG['db']} (UID: {uid})\n")
    return uid, models

def execute(models, uid, model, method, *args):
    """Execute Odoo method"""
    return models.execute_kw(
        PROD_CONFIG['db'],
        uid,
        PROD_CONFIG['password'],
        model,
        method,
        args
    )

def inspect_modules(models, uid):
    """Check installed modules and their states"""
    print("=" * 80)
    print("MODULE STATUS INSPECTION")
    print("=" * 80)
    
    target_modules = ['commission_ax', 'hr_uae', 'hr', 'sale', 'crm']
    
    for module_name in target_modules:
        modules = execute(models, uid, 'ir.module.module', 'search_read',
                         [('name', '=', module_name)],
                         {'fields': ['name', 'state', 'latest_version', 'installed_version']})
        
        if modules:
            mod = modules[0]
            status_icon = "✓" if mod['state'] == 'installed' else "✗"
            print(f"{status_icon} {mod['name']}")
            print(f"  State: {mod['state']}")
            print(f"  Installed Version: {mod.get('installed_version', 'N/A')}")
            print(f"  Latest Version: {mod.get('latest_version', 'N/A')}")
        else:
            print(f"✗ {module_name} - NOT FOUND")
        print()

def inspect_model_fields(models, uid):
    """Check if critical fields exist in models"""
    print("=" * 80)
    print("MODEL FIELD INSPECTION")
    print("=" * 80)
    
    # Check sale.order for commission fields
    try:
        sale_fields = execute(models, uid, 'sale.order', 'fields_get', 
                             ['agent1_partner', 'agent1_commission', 
                              'agent2_partner', 'agent2_commission',
                              'manager_partner', 'manager_commission',
                              'director_partner', 'director_commission',
                              'exclusive_rm_commission', 'exclusive_sm_commission'])
        
        print("✓ sale.order commission fields:")
        for field, info in sale_fields.items():
            print(f"  - {field} ({info.get('type', 'unknown')})")
    except Exception as e:
        print(f"✗ sale.order commission fields missing or error: {e}")
    print()
    
    # Check hr.employee for agent fields
    try:
        hr_fields = execute(models, uid, 'hr.employee', 'fields_get',
                           ['is_agent', 'agent_type',
                            'primary_agent_personal_commission',
                            'primary_agent_business_commission',
                            'secondary_agent_personal_commission',
                            'secondary_agent_business_commission'])
        
        print("✓ hr.employee agent commission fields:")
        for field, info in hr_fields.items():
            print(f"  - {field} ({info.get('type', 'unknown')})")
    except Exception as e:
        print(f"✗ hr.employee agent fields missing or error: {e}")
    print()

def inspect_employees(models, uid):
    """Check employee records and user associations"""
    print("=" * 80)
    print("EMPLOYEE RECORDS INSPECTION")
    print("=" * 80)
    
    employees = execute(models, uid, 'hr.employee', 'search_read',
                       [],
                       {'fields': ['name', 'user_id', 'work_email']})
    
    print(f"Total Employees: {len(employees)}\n")
    
    employees_without_users = []
    employees_with_users = []
    
    for emp in employees:
        if not emp.get('user_id'):
            employees_without_users.append(emp)
        else:
            employees_with_users.append(emp)
    
    print(f"✓ Employees WITH user accounts: {len(employees_with_users)}")
    for emp in employees_with_users:
        print(f"  - {emp['name']} (User ID: {emp['user_id'][0]})")
    
    print(f"\n⚠ Employees WITHOUT user accounts: {len(employees_without_users)}")
    for emp in employees_without_users:
        print(f"  - {emp['name']} (Email: {emp.get('work_email', 'N/A')})")
    
    print()

def inspect_commission_rates(models, uid):
    """Check existing commission rate data on employees"""
    print("=" * 80)
    print("COMMISSION RATE DATA INSPECTION")
    print("=" * 80)
    
    try:
        employees = execute(models, uid, 'hr.employee', 'search_read',
                           [('is_agent', '=', True)],
                           {'fields': ['name', 'is_agent', 'agent_type',
                                      'primary_agent_personal_commission',
                                      'primary_agent_business_commission',
                                      'secondary_agent_personal_commission',
                                      'secondary_agent_business_commission']})
        
        if employees:
            print(f"✓ Agents found: {len(employees)}\n")
            for emp in employees:
                print(f"Agent: {emp['name']}")
                print(f"  Type: {emp.get('agent_type', 'N/A')}")
                print(f"  Primary Personal: {emp.get('primary_agent_personal_commission', 0)}%")
                print(f"  Primary Business: {emp.get('primary_agent_business_commission', 0)}%")
                print(f"  Secondary Personal: {emp.get('secondary_agent_personal_commission', 0)}%")
                print(f"  Secondary Business: {emp.get('secondary_agent_business_commission', 0)}%")
                print()
        else:
            print("ℹ No agents (is_agent=True) found in database")
    except Exception as e:
        print(f"✗ Unable to check commission rates: {e}")
    print()

def inspect_utm_sources(models, uid):
    """Check UTM sources for lead type detection"""
    print("=" * 80)
    print("UTM SOURCE INSPECTION")
    print("=" * 80)
    
    sources = execute(models, uid, 'utm.source', 'search_read',
                     [],
                     {'fields': ['name', 'active']})
    
    print(f"Total UTM Sources: {len(sources)}\n")
    
    personal_sources = []
    business_sources = []
    
    for source in sources:
        name_lower = source['name'].lower()
        if 'personal' in name_lower or 'referral' in name_lower:
            personal_sources.append(source)
        else:
            business_sources.append(source)
    
    print(f"✓ Personal/Referral Sources: {len(personal_sources)}")
    for src in personal_sources:
        status = "Active" if src.get('active') else "Inactive"
        print(f"  - {src['name']} ({status})")
    
    print(f"\n✓ Business Sources: {len(business_sources)}")
    for src in business_sources[:10]:  # Show first 10
        status = "Active" if src.get('active') else "Inactive"
        print(f"  - {src['name']} ({status})")
    
    if len(business_sources) > 10:
        print(f"  ... and {len(business_sources) - 10} more")
    
    print()

def inspect_sale_orders(models, uid):
    """Check existing sale orders with commission data"""
    print("=" * 80)
    print("SALE ORDER COMMISSION DATA INSPECTION")
    print("=" * 80)
    
    try:
        orders = execute(models, uid, 'sale.order', 'search_read',
                        [],
                        {'fields': ['name', 'state', 'agent1_partner', 'agent1_commission',
                                   'agent2_partner', 'agent2_commission',
                                   'manager_partner', 'manager_commission',
                                   'source_id'],
                         'limit': 100})
        
        print(f"Total Orders (sample): {len(orders)}\n")
        
        stats = {
            'with_agent1': 0,
            'with_agent2': 0,
            'with_manager': 0,
            'with_commission_rates': 0,
            'draft': 0,
            'confirmed': 0
        }
        
        for order in orders:
            if order.get('agent1_partner'):
                stats['with_agent1'] += 1
            if order.get('agent2_partner'):
                stats['with_agent2'] += 1
            if order.get('manager_partner'):
                stats['with_manager'] += 1
            if order.get('agent1_commission', 0) > 0:
                stats['with_commission_rates'] += 1
            if order.get('state') == 'draft':
                stats['draft'] += 1
            elif order.get('state') in ['sale', 'done']:
                stats['confirmed'] += 1
        
        print("Order Statistics:")
        print(f"  Orders with Agent 1: {stats['with_agent1']}")
        print(f"  Orders with Agent 2: {stats['with_agent2']}")
        print(f"  Orders with Manager: {stats['with_manager']}")
        print(f"  Orders with Commission Rates: {stats['with_commission_rates']}")
        print(f"  Draft Orders: {stats['draft']}")
        print(f"  Confirmed Orders: {stats['confirmed']}")
        
    except Exception as e:
        print(f"✗ Error inspecting sale orders: {e}")
    
    print()

def inspect_partners(models, uid):
    """Check partner/employee associations"""
    print("=" * 80)
    print("PARTNER-EMPLOYEE ASSOCIATIONS")
    print("=" * 80)
    
    # Get all employees with users
    employees = execute(models, uid, 'hr.employee', 'search_read',
                       [('user_id', '!=', False)],
                       {'fields': ['name', 'user_id']})
    
    print(f"Employees with user accounts: {len(employees)}\n")
    
    # For each employee, get their user's partner
    for emp in employees[:5]:  # Show first 5
        user = execute(models, uid, 'res.users', 'read',
                      [emp['user_id'][0]],
                      {'fields': ['name', 'partner_id']})
        
        if user:
            print(f"Employee: {emp['name']}")
            print(f"  User: {user[0]['name']} (ID: {user[0]['id']})")
            print(f"  Partner: {user[0]['partner_id'][1]} (ID: {user[0]['partner_id'][0]})")
            print()
    
    if len(employees) > 5:
        print(f"... and {len(employees) - 5} more employee-user associations\n")

def generate_report(issues):
    """Generate deployment readiness report"""
    print("=" * 80)
    print("DEPLOYMENT READINESS REPORT")
    print("=" * 80)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'database': PROD_CONFIG['db'],
        'issues': issues,
        'recommendations': []
    }
    
    # Generate recommendations
    if any('employee' in issue.lower() and 'user' in issue.lower() for issue in issues):
        report['recommendations'].append(
            "Run migration script step 1 to link employees to users"
        )
    
    if any('commission rate' in issue.lower() for issue in issues):
        report['recommendations'].append(
            "Run migration script step 1 to set default commission rates"
        )
    
    if any('utm' in issue.lower() for issue in issues):
        report['recommendations'].append(
            "Run migration script step 2 to create required UTM sources"
        )
    
    # Print summary
    if issues:
        print(f"\n⚠ POTENTIAL ISSUES FOUND: {len(issues)}\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        
        print(f"\n📋 RECOMMENDATIONS:\n")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
    else:
        print("\n✓ NO CRITICAL ISSUES FOUND - Ready for deployment")
    
    # Save report
    filename = f"inspection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved: {filename}")
    print("=" * 80)

def main():
    """Main inspection flow"""
    print("=" * 80)
    print("OSUS PROPERTIES DATABASE INSPECTION")
    print("=" * 80)
    print()
    
    try:
        uid, models = connect_odoo()
        
        issues = []
        
        # Run all inspections
        inspect_modules(models, uid)
        inspect_model_fields(models, uid)
        inspect_employees(models, uid)
        inspect_commission_rates(models, uid)
        inspect_utm_sources(models, uid)
        inspect_sale_orders(models, uid)
        inspect_partners(models, uid)
        
        # Generate final report
        generate_report(issues)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
