#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Upgrade the deal_report module via Odoo RPC API.
This requires the Odoo instance to be running and accessible.
"""

import json
import time
import urllib.request
import urllib.error
import base64

ODOO_URL = "http://localhost:8069"
DB_NAME = "odoo"
ADMIN_USER = "admin"
ADMIN_PASS = "admin"

def make_rpc_call(method, params):
    """Make an RPC call to Odoo."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        req = urllib.request.Request(
            f"{ODOO_URL}/jsonrpc",
            data=json.dumps(payload).encode('utf-8'),
            headers=headers
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.URLError as e:
        print(f"Network error: {e}")
        return {"error": {"message": str(e)}}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": {"message": str(e)}}

def authenticate():
    """Authenticate with Odoo and get session."""
    print("Authenticating with Odoo...")
    
    result = make_rpc_call("call", {
        "service": "common",
        "method": "authenticate",
        "args": [DB_NAME, ADMIN_USER, ADMIN_PASS, {}]
    })
    
    if "result" in result:
        print(f"Successfully authenticated as user ID: {result['result']}")
        return result["result"]
    else:
        print(f"Authentication failed: {result.get('error', 'Unknown error')}")
        return None

def upgrade_module(user_id):
    """Upgrade the deal_report module."""
    print(f"\nUpgrading deal_report module for user {user_id}...")
    
    # First, find the module record
    result = make_rpc_call("call", {
        "service": "object",
        "method": "execute",
        "args": [DB_NAME, user_id, ADMIN_PASS, "ir.module.module", "search", 
                 [["name", "=", "deal_report"]]]
    })
    
    if "error" in result:
        print(f"Error searching for module: {result['error']}")
        return False
    
    module_ids = result.get("result", [])
    if not module_ids:
        print("ERROR: deal_report module not found!")
        return False
    
    module_id = module_ids[0]
    print(f"Found module with ID: {module_id}")
    
    # Upgrade the module
    print("Calling button_upgrade...")
    result = make_rpc_call("call", {
        "service": "object",
        "method": "execute",
        "args": [DB_NAME, user_id, ADMIN_PASS, "ir.module.module", 
                 "button_upgrade", [module_id]]
    })
    
    if "error" in result:
        error_msg = result["error"].get("message", "Unknown error")
        print(f"Upgrade returned error: {error_msg}")
        # Check if it's just a message about already being in upgrade state
        if "already" in error_msg.lower() or "state" in error_msg.lower():
            print("Module may already be in upgrade state. Waiting a moment...")
            time.sleep(2)
            return True
        return False
    
    print("Module upgrade initiated successfully!")
    return True

def main():
    """Main function."""
    print("="*60)
    print("Deal Report Module Upgrade via RPC")
    print("="*60)
    
    # Check if Odoo is accessible
    try:
        req = urllib.request.Request(f"{ODOO_URL}/web")
        with urllib.request.urlopen(req, timeout=5) as response:
            print("✓ Odoo is accessible\n")
    except Exception as e:
        print(f"✗ Could not connect to Odoo: {e}")
        print(f"  Please ensure Odoo is running at {ODOO_URL}")
        return False
    
    # Authenticate
    user_id = authenticate()
    if not user_id:
        return False
    
    # Upgrade module
    success = upgrade_module(user_id)
    
    if success:
        print("\n" + "="*60)
        print("SUCCESS: Module upgrade initiated!")
        print("="*60)
        print("\nNEXT STEPS:")
        print("1. Wait a few seconds for the upgrade to complete")
        print("2. Open Odoo in your browser: http://localhost:8069")
        print("3. Go to Sales menu")
        print("4. You should now see the 'Deals' submenu with:")
        print("   - Deal Reports")
        print("   - Deal Dashboard")
        print("   - Analytics (with Overview, Trends, Distribution)")
        print("\nIf menus still don't appear:")
        print("- Clear your browser cache (Ctrl+Shift+Del)")
        print("- Refresh the page (Ctrl+F5)")
        print("- Log out and log back in")
        return True
    else:
        print("\n" + "="*60)
        print("WARNING: Module upgrade may have failed")
        print("="*60)
        print("\nTroubleshooting:")
        print("1. Check Odoo logs for errors")
        print("2. Ensure deal_report is not in an error state")
        print("3. Try upgrading via the web interface manually")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
