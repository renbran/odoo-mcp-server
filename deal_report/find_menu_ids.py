#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find the correct Sales menu ID for parent reference.
Run this against the running Odoo instance via RPC.
"""

import requests
import json

ODOO_URL = "http://localhost:8069"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def call_odoo(method, model, args=None, kwargs=None):
    """Make an RPC call to Odoo."""
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": method,
            "args": [model] + args,
            "kwargs": kwargs
        },
        "id": 1
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{ODOO_URL}/jsonrpc",
        json=payload,
        headers=headers
    )
    
    return response.json()

def find_sale_menu_ids():
    """Find menu IDs in the Sales module."""
    print("Searching for Sales menu items in Odoo...\n")
    
    try:
        # Get all menu items
        result = call_odoo(
            "search_read",
            "ir.ui.menu",
            [[]],
            {"fields": ["id", "name", "xml_id"]}
        )
        
        if "result" in result:
            menus = result["result"]
            print("Menu items containing 'sale' or 'root':")
            print("-" * 60)
            
            for menu in menus:
                name = menu.get("name", "").lower()
                xml_id = menu.get("xml_id", "")
                
                if "sale" in name or "root" in name or "sales" in name:
                    print(f"ID: {menu.get('id'):4d} | Name: {menu.get('name'):40s} | XML ID: {xml_id}")
            
            print("\n" + "="*60)
            print("Look for the root Sales menu and use its xml_id as parent")
            print("Example: parent=\"sale.menu_root_sale\"")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Error connecting to Odoo: {e}")
        print("\nTrying alternative approach...")
        print("Looking at Odoo 17 standard menu structure:")
        print("-" * 60)
        print("For Sales module, the typical parent menu ID is:")
        print("  parent=\"sale.menu_root_sale\"")
        print("\nIf that doesn't work, try:")
        print("  parent=\"sale.menu_sales\"")
        print("  parent=\"crm.menu_crm_root\"")
        print("  parent=\"base.menu_sales\"")

if __name__ == "__main__":
    find_sale_menu_ids()
