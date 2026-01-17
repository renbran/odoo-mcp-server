#!/usr/bin/env python3
"""
Diagnose the action reference issue and prepare for fix.
"""

import xmlrpc.client
import json
from datetime import datetime

# Configuration
URL = "https://erp.sgctech.ai"
DB = "scholarixv2"
USERNAME = "info@scholarixglobal.com"
PASSWORD = "123456"

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║  Diagnose Deals Management Module Issue                          ║
    ║  Check if action definitions exist and module state              ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Connect to Odoo
    print("\n▶ Connecting to Odoo server...")
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        objects = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        print(f"✅ Connected! User ID: {uid}\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Check module state
    print("▶ Checking deals_management module state...")
    try:
        ir_module = objects.execute_kw(
            DB, uid, PASSWORD, 'ir.module.module', 'search_read',
            [['name', '=', 'deals_management']],
            {'fields': ['id', 'name', 'state', 'installed_version', 'latest_version']}
        )
        
        if ir_module:
            mod = ir_module[0]
            print(f"""
Module State:
  Name: {mod['name']}
  State: {mod['state']}
  Installed Version: {mod['installed_version']}
  Latest Version: {mod['latest_version']}
            """)
        else:
            print("❌ Module not found on server!")
            return False
    except Exception as e:
        print(f"❌ Error checking module: {e}")
        return False
    
    # Check if actions exist
    print("\n▶ Checking action definitions...")
    actions_to_check = [
        'deals_management.action_deals_all_commissions',
        'deals_management.action_deals_pending_bills',
        'deals_management.action_deals_paid_bills',
    ]
    
    for action_id in actions_to_check:
        try:
            result = objects.execute_kw(
                DB, uid, PASSWORD, 'ir.model.data', 'search_read',
                [['complete_name', '=', action_id]],
                {'fields': ['id', 'complete_name', 'res_id', 'model']}
            )
            if result:
                print(f"  ✅ {action_id} - FOUND")
            else:
                print(f"  ❌ {action_id} - NOT FOUND")
        except Exception as e:
            print(f"  ⚠️  Error checking {action_id}: {e}")
    
    # Check menu items
    print("\n▶ Checking menu items...")
    try:
        menus = objects.execute_kw(
            DB, uid, PASSWORD, 'ir.ui.menu', 'search_read',
            [['name', 'in', ['All Commissions', 'Pending Bills', 'Paid Bills']]],
            {'fields': ['id', 'name', 'parent_id']}
        )
        print(f"  Found {len(menus)} related menu items")
        for menu in menus:
            print(f"    - {menu['name']}")
    except Exception as e:
        print(f"  ⚠️  Error checking menus: {e}")
    
    # Generate report
    print("\n" + "="*70)
    print("DIAGNOSIS SUMMARY")
    print("="*70)
    
    if ir_module and ir_module[0]['state'] == 'uninstalled':
        print("""
🔴 ISSUE FOUND:
The module is UNINSTALLED on the server.

The error occurred because:
1. The module wasn't installed when you tried to install it
2. The XML files being loaded reference actions that don't exist yet
3. This is a chicken-and-egg problem with module loading

SOLUTION:
Since the fixed code is already in the Git repository (commit 4041254),
we need to:
1. Uninstall the broken module (if it's in a failed state)
2. Re-install with the latest code
3. Use the Odoo UI to upgrade/reinstall

The action reference fix is in:
  File: deals_management/views/deals_menu.xml
  Lines: 35-55
  Change: action="action_name" → action="deals_management.action_name"
        """)
    else:
        print("""
The module might be in an inconsistent state.
Check the Odoo logs for more details about the installation failure.
        """)
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
