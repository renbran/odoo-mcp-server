#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct check for deal_management UI presence."""

import xmlrpc.client

url = "https://erp.sgctech.ai"
db = "scholarixv2"
username = "info@scholarixglobal.com"
password = "123456"

try:
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    obj = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    
    uid = common.authenticate(db, username, password, {})
    print(f"[OK] Connected as UID {uid}\n")
    
    # Simple direct check: Can we access deal.management model?
    print("=== TESTING deal.management MODEL ===")
    try:
        # Try to get count of records
        count = obj.execute_kw(
            db, uid, password,
            'deal.management', 'search_count', [[]]
        )
        print(f"[SUCCESS] deal.management exists and has {count} records")
        print("[RESULT] DEAL_MANAGEMENT IS INSTALLED")
        
        # Get some records
        deals = obj.execute_kw(
            db, uid, password,
            'deal.management', 'search', [[]], {'limit': 5}
        )
        if deals:
            data = obj.execute_kw(
                db, uid, password,
                'deal.management', 'read',
                deals,
                ['name', 'state']
            )
            print(f"\n[DATA] Sample records: {len(data)} records")
            for d in data:
                print(f"  - {d.get('name', '?')}: {d.get('state', '?')}")
    
    except Exception as e:
        error_msg = str(e)
        if "doesn't exist" in error_msg or "not found" in error_msg:
            print(f"[NOT FOUND] deal.management does NOT exist on server")
            print("[RESULT] DEAL_MANAGEMENT NOT INSTALLED - Code needs to be deployed")
        else:
            print(f"[ERROR] {error_msg[:150]}")
    
    print("\n=== CHECKING deal_stage MODEL ===")
    try:
        count = obj.execute_kw(
            db, uid, password,
            'deal.stage', 'search_count', [[]]
        )
        print(f"[SUCCESS] deal.stage exists with {count} stages")
    except Exception as e:
        if "doesn't exist" in str(e):
            print(f"[NOT FOUND] deal.stage does NOT exist")
        else:
            print(f"[ERROR] {str(e)[:100]}")
    
    print("\n=== TESTING deal_management MENU ===")
    try:
        # Check if menu exists
        menus = obj.execute_kw(
            db, uid, password,
            'ir.ui.menu', 'search',
            [['name', '=', 'Deals']], {'limit': 5}
        )
        if menus:
            print(f"[SUCCESS] 'Deals' menu found")
            for menu_id in menus:
                menu_data = obj.execute_kw(
                    db, uid, password,
                    'ir.ui.menu', 'read',
                    [menu_id],
                    ['name', 'action']
                )
                print(f"  Menu: {menu_data[0]['name']}")
        else:
            print(f"[NOT FOUND] 'Deals' menu not found")
    except Exception as e:
        print(f"[ERROR] {str(e)[:100]}")

except Exception as e:
    print(f"[FAIL] Connection error: {e}")

print("\n" + "="*60)
print("INTERPRETATION:")
print("="*60)
print("If you see [SUCCESS] messages above with deal.management,")
print("the module IS installed and working.")
print("\nIf you see [NOT FOUND] messages,")
print("the code I provided still needs to be implemented.")
print("="*60)
