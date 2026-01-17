#!/usr/bin/env python3
import os, sys
sys.path.insert(0, "/var/odoo/scholarixv2/src")
os.chdir("/var/odoo/scholarixv2")
os.environ.setdefault("ODOO_RC", "/var/odoo/scholarixv2/odoo.conf")

import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry("commission_ax")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Get the FINAL compiled form view (what browser sees)
    view = env["sale.order"].get_view(view_type='form')
    
    # Check if deal tracking fields are in the arch
    arch_str = str(view.get('arch', ''))
    
    print("🔍 Checking final compiled FORM view for deal tracking fields:")
    fields_to_check = ['buyer_name', 'project_name', 'unit_sale_value', 'primary_commission_percentage', 'BROKERAGE DEAL']
    
    for field_name in fields_to_check:
        if field_name in arch_str:
            print(f"   ✅ FOUND: {field_name}")
        else:
            print(f"   ❌ MISSING: {field_name}")
    
    # Get the tree view
    tree_view = env["sale.order"].get_view(view_type='tree')
    tree_arch = str(tree_view.get('arch', ''))
    
    print("\n🔍 Checking final compiled TREE view for deal tracking fields:")
    for field_name in ['buyer_name', 'project_name', 'unit_sale_value', 'primary_commission_percentage']:
        if field_name in tree_arch:
            print(f"   ✅ FOUND: {field_name}")
        else:
            print(f"   ❌ MISSING: {field_name}")
    
    # Show a snippet of the arch around buyer_name
    if 'buyer_name' in arch_str:
        idx = arch_str.find('buyer_name')
        snippet = arch_str[max(0, idx-200):min(len(arch_str), idx+200)]
        print(f"\n📋 Snippet around 'buyer_name':")
        print(snippet)
