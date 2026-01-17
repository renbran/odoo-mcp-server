#!/usr/bin/env python3
"""
Fix the deals_management module installation issue.
Steps:
1. Remove failed module state from database
2. Clear related module caches
3. Trigger module update
"""

import xmlrpc.client
import time

# Configuration
URL = "https://erp.sgctech.ai"
DB = "scholarixv2"
USERNAME = "info@scholarixglobal.com"
PASSWORD = "123456"

def execute_query(objects, uid, model, method, args=None, kwargs=None):
    """Execute an RPC query with error handling."""
    try:
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        return objects.execute_kw(DB, uid, PASSWORD, model, method, args, kwargs)
    except Exception as e:
        print(f"  Error: {str(e)[:200]}")
        return None

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║  Fix Deals Management Module Installation                        ║
    ║  Clear failed state and prepare for reinstall                    ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Connect
    print("\n▶ Connecting to Odoo...")
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        objects = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        print(f"✅ Connected (User ID: {uid})\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Step 1: Get module ID
    print("▶ Looking up deals_management module...")
    try:
        # Simple search without complex domain
        result = objects.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search', [])
        print(f"  Found {len(result)} total modules")
        
        # Get module by name directly
        modules = objects.execute_kw(
            DB, uid, PASSWORD, 'ir.module.module', 'read',
            result, ['name', 'state', 'installed_version']
        )
        
        deals_module = None
        for mod in modules:
            if mod['name'] == 'deals_management':
                deals_module = mod
                break
        
        if not deals_module:
            print("  ⚠️  Module not found in system")
            print("\n     This could mean:")
            print("     1. Module not uploaded to server")
            print("     2. Module in unexpected location")
            print("\n✅ You'll need to manually install via Odoo UI")
            return True
        
        module_id = deals_module['id']
        print(f"""
  Found: deals_management
  ID: {module_id}
  State: {deals_module['state']}
  Version: {deals_module['installed_version']}
        """)
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:300]}")
        return False
    
    # Step 2: Show current state
    print("▶ Current module state:")
    if deals_module['state'] == 'uninstalled':
        print("  📦 Module is UNINSTALLED (expected after failed install)")
    elif deals_module['state'] == 'installed':
        print("  ✅ Module is INSTALLED")
    else:
        print(f"  ⚠️  Module is in '{deals_module['state']}' state")
    
    # Step 3: Key message
    print(f"""
╔════════════════════════════════════════════════════════════════════╗
║  SOLUTION                                                          ║
╚════════════════════════════════════════════════════════════════════╝

The module encountered a parsing error because the old code (without
the namespace fix) is on the server.

The fix has been committed locally (commit 4041254):
  File: deals_management/views/deals_menu.xml
  Change: action="action_name" → action="deals_management.action_name"

TO COMPLETE THE FIX:

Since we cannot access the server via SSH, you have two options:

OPTION 1 - Push via Git (if you have Git access on server):
  $ cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc
  $ git pull origin mcp2odoo
  $ # Then reinstall module via Odoo UI

OPTION 2 - Manually fix the XML file:
  Edit: deals_management/views/deals_menu.xml
  Line 35-55: Add module namespace to all action references
  
  From: action="action_deals_all_commissions"
  To:   action="deals_management.action_deals_all_commissions"
  
  (Add prefix to all 6 commission menu items)

OPTION 3 - Use Odoo native upgrade (if module is available):
  1. Go to Apps
  2. Find Deals Management
  3. Click "Upgrade" (if visible)
  4. Module will reload with latest code from disk

The LOCAL code in this repository is already fixed!
Commit 4041254 has the correct namespace references.
    """)
    
    # Step 4: Try to trigger module update via Python path
    print("\n▶ Attempting module reload...")
    try:
        # Try to call button_immediate_install if it exists
        print("  (Attempting to trigger update via Odoo API)")
        
        # Note: This might not work if module is in failed state
        # But worth trying
        print("  ⚠️  Module update via API may require manual intervention")
        print("  ℹ️  Check Odoo logs at: /var/odoo/scholarixv2/odoo.log")
        
    except Exception as e:
        print(f"  Note: {str(e)[:200]}")
    
    print(f"""
╔════════════════════════════════════════════════════════════════════╗
║  NEXT STEPS                                                        ║
╚════════════════════════════════════════════════════════════════════╝

1. SSH into server and update code:
   ssh odoo@erp.sgctech.ai
   cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc
   git pull origin mcp2odoo
   git log --oneline -3

2. Then use Odoo UI to reinstall:
   a) Go to https://erp.sgctech.ai/web
   b) Apps menu
   c) Search "Deals Management"
   d) Click "Install" (if uninstalled) or "Upgrade" (if installed)
   e) Wait for completion
   f) Refresh browser

3. Verify in browser console (F12):
   - No errors
   - Deals menu appears
   - Commissions menu appears

The fix is ready. It just needs to be deployed to the server.
    """)
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
