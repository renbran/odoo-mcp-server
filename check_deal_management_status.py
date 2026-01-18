#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick status check for deal_management module."""

import xmlrpc.client
import sys

url = "https://erp.sgctech.ai"
db = "scholarixv2"
username = "info@scholarixglobal.com"
password = "123456"

try:
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    obj = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    
    uid = common.authenticate(db, username, password, {})
    print(f"[OK] Connected as UID {uid}")
    
    # Check if deal_management is installed
    print("\n=== CHECKING deal_management MODULE ===\n")
    
    try:
        # Simple search for any installed module
        result = obj.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [['name', '=', 'deal_management']]
        )
        print(f"Module found: {result}")
        
        if result:
            # Get module details
            mod_data = obj.execute_kw(
                db, uid, password,
                'ir.module.module', 'read',
                result,
                ['name', 'state', 'category_id']
            )
            print(f"Module details: {mod_data}")
    except Exception as e:
        print(f"[ERROR] {str(e)[:200]}")
    
    # Check for deal models
    print("\n=== CHECKING DEAL MODELS ===\n")
    
    try:
        models = obj.execute_kw(
            db, uid, password,
            'ir.model', 'search',
            [['model', 'like', 'deal']]
        )
        print(f"Deal models found: {len(models)} models")
        if models:
            model_data = obj.execute_kw(
                db, uid, password,
                'ir.model', 'read',
                models,
                ['model', 'name']
            )
            for m in model_data:
                print(f"  - {m['model']}: {m['name']}")
    except Exception as e:
        print(f"[ERROR] {str(e)[:200]}")
    
    # Check for deal menus
    print("\n=== CHECKING DEAL MENUS ===\n")
    
    try:
        menus = obj.execute_kw(
            db, uid, password,
            'ir.ui.menu', 'search',
            [['name', 'like', 'Deal']]
        )
        print(f"Deal menus found: {len(menus)} menus")
        if menus:
            menu_data = obj.execute_kw(
                db, uid, password,
                'ir.ui.menu', 'read',
                menus,
                ['name', 'action', 'parent_id']
            )
            for m in menu_data:
                print(f"  - {m['name']}")
    except Exception as e:
        print(f"[ERROR] {str(e)[:200]}")
    
    print("\n=== SUMMARY ===\n")
    print("[!] Check results above. If models/menus are not found,")
    print("[!] deal_management is NOT installed on the server.")
    print("[!] Code provided needs to be implemented and deployed.")
    
except Exception as e:
    print(f"[FAIL] Connection error: {e}")
