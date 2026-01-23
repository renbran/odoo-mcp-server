#!/usr/bin/env python3
"""
OSUS Properties Database Health & Integrity Check
Comprehensive database verification after module upgrade
"""

import xmlrpc.client
import json
from datetime import datetime

# Production configuration
PROD_URL = 'http://139.84.163.11:8070'
PROD_DB = 'osusproperties'
print("Enter credentials:")
PROD_USER = input('Username (default: admin): ') or 'admin'
PROD_PASS = input('Password: ')

def connect():
    """Connect to Odoo"""
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

def check_module_health(models, uid):
    """Check installed modules status"""
    print("=" * 80)
    print("MODULE HEALTH CHECK")
    print("=" * 80)
    
    critical_modules = ['base', 'sale', 'hr', 'commission_ax', 'hr_uae']
    
    for module_name in critical_modules:
        modules = execute(models, uid, 'ir.module.module', 'search_read',
                         [('name', '=', module_name)],
                         {'fields': ['name', 'state', 'latest_version', 'demo']})
        
        if modules:
            mod = modules[0]
            status = "✓" if mod['state'] == 'installed' else "✗"
            print(f"{status} {mod['name']}: {mod['state']} (v{mod.get('latest_version', 'N/A')})")
        else:
            print(f"✗ {module_name}: NOT FOUND")
    
    # Check for modules in error state
    error_modules = execute(models, uid, 'ir.module.module', 'search_read',
                           [('state', 'in', ['to upgrade', 'to remove', 'to install'])],
                           {'fields': ['name', 'state']})
    
    if error_modules:
        print(f"\n⚠ Modules pending action: {len(error_modules)}")
        for mod in error_modules[:5]:
            print(f"  - {mod['name']}: {mod['state']}")
    else:
        print("\n✓ No modules pending action")
    print()

def check_data_integrity(models, uid):
    """Check data integrity and consistency"""
    print("=" * 80)
    print("DATA INTEGRITY CHECK")
    print("=" * 80)
    
    issues = []
    
    # Check employees without users but marked as agents
    agents_no_users = execute(models, uid, 'hr.employee', 'search_count',
                              [('is_agent', '=', True), ('user_id', '=', False)])
    
    if agents_no_users > 0:
        issues.append(f"{agents_no_users} agents without linked users (commission auto-fill won't work)")
        print(f"⚠ Agents without users: {agents_no_users}")
    else:
        print("✓ All agents have linked users")
    
    # Check sale orders with agents but no commission rates
    orders_no_rates = execute(models, uid, 'sale.order', 'search_count',
                              ['&', '|', ('agent1_partner_id', '!=', False), ('agent2_partner_id', '!=', False),
                               '&', ('agent1_rate', '=', 0), ('agent2_rate', '=', 0)])
    
    if orders_no_rates > 0:
        issues.append(f"{orders_no_rates} orders with agents but zero commission rates")
        print(f"⚠ Orders with agents but no rates: {orders_no_rates}")
    else:
        print("✓ All orders with agents have commission rates")
    
    # Check for orphaned commission lines
    try:
        orphaned_lines = execute(models, uid, 'commission.line', 'search_count',
                                [('sale_order_id', '=', False)])
        if orphaned_lines > 0:
            issues.append(f"{orphaned_lines} orphaned commission lines")
            print(f"⚠ Orphaned commission lines: {orphaned_lines}")
        else:
            print("✓ No orphaned commission lines")
    except Exception as e:
        print(f"ℹ Commission lines check skipped: {str(e)[:50]}")
    
    print()
    return issues

def check_commission_consistency(models, uid):
    """Check commission data consistency"""
    print("=" * 80)
    print("COMMISSION DATA CONSISTENCY")
    print("=" * 80)
    
    # Check total sale orders
    total_orders = execute(models, uid, 'sale.order', 'search_count', [])
    print(f"Total Sale Orders: {total_orders}")
    
    # Orders with agents
    with_agent1 = execute(models, uid, 'sale.order', 'search_count',
                         [('agent1_partner_id', '!=', False)])
    with_agent2 = execute(models, uid, 'sale.order', 'search_count',
                         [('agent2_partner_id', '!=', False)])
    
    print(f"Orders with Agent 1: {with_agent1} ({with_agent1/total_orders*100:.1f}%)")
    print(f"Orders with Agent 2: {with_agent2} ({with_agent2/total_orders*100:.1f}%)")
    
    # Orders with commission rates
    with_rates = execute(models, uid, 'sale.order', 'search_count',
                        ['|', ('agent1_rate', '>', 0), ('agent2_rate', '>', 0)])
    
    print(f"Orders with commission rates: {with_rates} ({with_rates/total_orders*100:.1f}%)")
    
    # Recent orders (last 30 days)
    from datetime import timedelta
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    recent_orders = execute(models, uid, 'sale.order', 'search_count',
                           [('create_date', '>=', thirty_days_ago)])
    
    recent_with_rates = execute(models, uid, 'sale.order', 'search_count',
                               ['&', ('create_date', '>=', thirty_days_ago),
                                '|', ('agent1_rate', '>', 0), ('agent2_rate', '>', 0)])
    
    print(f"\nRecent orders (30 days): {recent_orders}")
    print(f"Recent with rates: {recent_with_rates} ({recent_with_rates/recent_orders*100 if recent_orders > 0 else 0:.1f}%)")
    print()

def check_utm_source_coverage(models, uid):
    """Check UTM source setup and coverage"""
    print("=" * 80)
    print("UTM SOURCE COVERAGE")
    print("=" * 80)
    
    # Total sources
    total_sources = execute(models, uid, 'utm.source', 'search_count', [])
    active_sources = execute(models, uid, 'utm.source', 'search_count', [('active', '=', True)])
    
    print(f"Total UTM Sources: {total_sources} (Active: {active_sources})")
    
    # Personal/Referral sources
    personal_count = execute(models, uid, 'utm.source', 'search_count',
                            ['|', ('name', 'ilike', 'personal'), ('name', 'ilike', 'referral')])
    
    print(f"Personal/Referral Sources: {personal_count}")
    
    # Orders with sources
    orders_with_source = execute(models, uid, 'sale.order', 'search_count',
                                 [('source_id', '!=', False)])
    total_orders = execute(models, uid, 'sale.order', 'search_count', [])
    
    print(f"Orders with UTM source: {orders_with_source}/{total_orders} ({orders_with_source/total_orders*100:.1f}%)")
    
    # Most used sources
    print("\nMost used UTM sources (top 10):")
    sources = execute(models, uid, 'utm.source', 'search_read',
                     [],
                     {'fields': ['name', 'active'], 'limit': 100})
    
    source_usage = {}
    for src in sources:
        count = execute(models, uid, 'sale.order', 'search_count',
                       [('source_id', '=', src['id'])])
        if count > 0:
            source_usage[src['name']] = count
    
    sorted_sources = sorted(source_usage.items(), key=lambda x: x[1], reverse=True)[:10]
    for name, count in sorted_sources:
        print(f"  {name}: {count} orders")
    print()

def check_employee_health(models, uid):
    """Check employee records health"""
    print("=" * 80)
    print("EMPLOYEE RECORDS HEALTH")
    print("=" * 80)
    
    total_employees = execute(models, uid, 'hr.employee', 'search_count', [])
    active_employees = execute(models, uid, 'hr.employee', 'search_count', [('active', '=', True)])
    
    print(f"Total Employees: {total_employees} (Active: {active_employees})")
    
    # Employees with users
    with_users = execute(models, uid, 'hr.employee', 'search_count', [('user_id', '!=', False)])
    print(f"Employees with user accounts: {with_users} ({with_users/total_employees*100:.1f}%)")
    
    # Agents
    agents = execute(models, uid, 'hr.employee', 'search_count', [('is_agent', '=', True)])
    print(f"Marked as agents: {agents}")
    
    if agents > 0:
        # Agents with commission rates
        agents_with_rates = execute(models, uid, 'hr.employee', 'search_count',
                                    ['&', ('is_agent', '=', True),
                                     '|', ('primary_agent_personal_commission', '>', 0),
                                     ('primary_agent_business_commission', '>', 0)])
        
        print(f"Agents with commission rates: {agents_with_rates}/{agents}")
        
        # Show agent details
        agent_details = execute(models, uid, 'hr.employee', 'search_read',
                               [('is_agent', '=', True)],
                               {'fields': ['name', 'primary_agent_personal_commission',
                                          'primary_agent_business_commission'],
                                'limit': 5})
        
        print("\nSample agent commission rates:")
        for agent in agent_details:
            print(f"  {agent['name']}: Personal={agent.get('primary_agent_personal_commission', 0)}%, "
                  f"Business={agent.get('primary_agent_business_commission', 0)}%")
    print()

def check_field_definitions(models, uid):
    """Verify critical field definitions exist"""
    print("=" * 80)
    print("FIELD DEFINITION VERIFICATION")
    print("=" * 80)
    
    critical_fields = {
        'sale.order': ['agent1_partner_id', 'agent1_rate', 'agent2_partner_id', 'agent2_rate', 
                      'manager_partner_id', 'manager_rate', 'source_id'],
        'hr.employee': ['is_agent', 'primary_agent_personal_commission', 
                       'primary_agent_business_commission', 'user_id']
    }
    
    for model, fields in critical_fields.items():
        print(f"\n{model}:")
        try:
            field_defs = execute(models, uid, model, 'fields_get', fields)
            for field_name in fields:
                if field_name in field_defs:
                    field_type = field_defs[field_name].get('type', 'unknown')
                    print(f"  ✓ {field_name} ({field_type})")
                else:
                    print(f"  ✗ {field_name} MISSING")
        except Exception as e:
            print(f"  ✗ Error checking fields: {str(e)[:60]}")
    print()

def generate_health_report(all_issues):
    """Generate comprehensive health report"""
    print("=" * 80)
    print("DATABASE HEALTH REPORT SUMMARY")
    print("=" * 80)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'database': PROD_DB,
        'issues': all_issues,
        'health_score': 100 - (len(all_issues) * 10)
    }
    
    if all_issues:
        print(f"\n⚠ Issues Found: {len(all_issues)}\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        
        health_score = max(0, 100 - (len(all_issues) * 10))
        print(f"\nHealth Score: {health_score}/100")
        
        if health_score >= 80:
            print("Status: ✓ GOOD - Minor issues only")
        elif health_score >= 60:
            print("Status: ⚠ FAIR - Some attention needed")
        else:
            print("Status: ✗ POOR - Immediate action required")
    else:
        print("\n✓ NO ISSUES FOUND - Database is healthy")
        print("Health Score: 100/100")
        print("Status: ✓ EXCELLENT")
    
    # Save report
    filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved: {filename}")
    print("=" * 80)

def main():
    """Main health check flow"""
    print("=" * 80)
    print("OSUS PROPERTIES DATABASE HEALTH CHECK")
    print("=" * 80)
    print()
    
    try:
        uid, models = connect()
        
        all_issues = []
        
        # Run all health checks
        check_module_health(models, uid)
        integrity_issues = check_data_integrity(models, uid)
        all_issues.extend(integrity_issues)
        
        check_commission_consistency(models, uid)
        check_utm_source_coverage(models, uid)
        check_employee_health(models, uid)
        check_field_definitions(models, uid)
        
        # Generate summary report
        generate_health_report(all_issues)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
