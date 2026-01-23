#!/usr/bin/env python3
"""
OSUS Properties - Agent Activation Script
Marks employees with user accounts as agents and sets commission rates
"""

import xmlrpc.client
import json
from datetime import datetime

# Server configuration
PROD_URL = "http://localhost:8070"  # Use localhost when running on server
PROD_DB = "osusproperties"
PROD_USER = "salescompliance@osusproperties.com"
PROD_PASS = "8586583"

def activate_agents(dry_run=True):
    """
    Activate employees with user accounts as commission agents
    
    Args:
        dry_run: If True, only preview changes without applying
    """
    print("=" * 80)
    print("OSUS PROPERTIES - AGENT ACTIVATION")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (Preview Only)' if dry_run else 'LIVE EXECUTION'}")
    print()
    
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f"{PROD_URL}/xmlrpc/2/common")
    uid = common.authenticate(PROD_DB, PROD_USER, PROD_PASS, {})
    
    if not uid:
        print("❌ Authentication failed!")
        return
    
    print(f"✓ Connected to {PROD_DB} (UID: {uid})")
    print()
    
    models = xmlrpc.client.ServerProxy(f"{PROD_URL}/xmlrpc/2/object")
    
    # Get all employees
    employee_ids = models.execute_kw(
        PROD_DB, uid, PROD_PASS,
        'hr.employee', 'search',
        [[]]
    )
    
    employees = models.execute_kw(
        PROD_DB, uid, PROD_PASS,
        'hr.employee', 'read',
        [employee_ids, ['name', 'user_id', 'is_agent', 
                        'primary_agent_personal_commission', 
                        'primary_agent_business_commission']]
    )
    
    # Categorize employees
    with_user = [e for e in employees if e.get('user_id')]
    without_user = [e for e in employees if not e.get('user_id')]
    already_agents = [e for e in with_user if e.get('is_agent')]
    to_activate = [e for e in with_user if not e.get('is_agent')]
    
    print(f"📊 EMPLOYEE SUMMARY")
    print(f"   Total Employees:        {len(employees)}")
    print(f"   With User Accounts:     {len(with_user)}")
    print(f"   Without User Accounts:  {len(without_user)}")
    print(f"   Already Agents:         {len(already_agents)}")
    print(f"   To Activate:            {len(to_activate)}")
    print()
    
    if already_agents:
        print("✓ Already Activated as Agents:")
        for emp in already_agents:
            personal_rate = emp.get('primary_agent_personal_commission', 0)
            business_rate = emp.get('primary_agent_business_commission', 0)
            print(f"   • {emp['name']} (Personal: {personal_rate}%, Business: {business_rate}%)")
        print()
    
    if to_activate:
        print(f"{'🔍 PREVIEW' if dry_run else '✅ ACTIVATING'}: Employees to mark as agents")
        print()
        
        for emp in to_activate:
            print(f"   • {emp['name']}")
            print(f"     - Set is_agent = TRUE")
            print(f"     - Set primary_agent_personal_commission = 60%")
            print(f"     - Set primary_agent_business_commission = 40%")
            print()
        
        if not dry_run:
            # Activate agents
            for emp in to_activate:
                try:
                    models.execute_kw(
                        PROD_DB, uid, PROD_PASS,
                        'hr.employee', 'write',
                        [[emp['id']], {
                            'is_agent': True,
                            'agent_type': 'primary',
                            'primary_agent_personal_commission': 60,
                            'primary_agent_business_commission': 40
                        }]
                    )
                    print(f"   ✓ Activated: {emp['name']}")
                except Exception as e:
                    print(f"   ❌ Failed to activate {emp['name']}: {e}")
            
            print()
            print("=" * 80)
            print("✅ ACTIVATION COMPLETE")
            print("=" * 80)
        else:
            print("=" * 80)
            print("ℹ️  DRY RUN COMPLETE - No changes made")
            print("   Run with dry_run=False to apply changes")
            print("=" * 80)
    else:
        print("ℹ️  No employees to activate")
        print("   All employees with user accounts are already agents")
        print()
    
    # Recommendations for employees without users
    if without_user:
        print()
        print("📋 NEXT STEPS FOR REMAINING EMPLOYEES")
        print(f"   {len(without_user)} employees need user accounts to become agents:")
        print()
        print("   Option 1: Create user accounts via Odoo UI")
        print("   • Navigate to: Employees → Select employee")
        print("   • Edit → Related User field → Create user")
        print()
        print("   Option 2: Run this script again after creating users")
        print()
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'dry_run' if dry_run else 'live',
        'total_employees': len(employees),
        'employees_with_users': len(with_user),
        'employees_without_users': len(without_user),
        'already_agents': len(already_agents),
        'newly_activated': len(to_activate) if not dry_run else 0,
        'pending_activation': len(to_activate) if dry_run else 0,
        'employees_activated': [e['name'] for e in to_activate] if not dry_run else [],
        'employees_pending': [e['name'] for e in to_activate] if dry_run else []
    }
    
    report_file = f"agent_activation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Report saved: {report_file}")
    print()
    
    return report

if __name__ == "__main__":
    import sys
    
    # Default to dry run for safety
    dry_run = True
    
    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        confirm = input("⚠️  This will modify production data. Type 'ACTIVATE' to confirm: ")
        if confirm == 'ACTIVATE':
            dry_run = False
        else:
            print("❌ Activation cancelled")
            sys.exit(1)
    
    activate_agents(dry_run=dry_run)
    
    if dry_run:
        print()
        print("💡 To apply changes, run:")
        print("   python3 activate_agents.py --live")
