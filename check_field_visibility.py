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
    
    # Get a sale order and check if fields are accessible
    order = env["sale.order"].search([], limit=1)
    if order:
        print("✅ Sample Sale Order Data:")
        print(f"   ID: {order.id}")
        print(f"   Name: {order.name}")
        print(f"   Partner: {order.partner_id.name}")
        print(f"   Buyer Name: {order.buyer_name}")
        print(f"   Project ID: {order.project_id}")
        print(f"   Project Name: {order.project_name}")
        print(f"   Unit Sale Value: {order.unit_sale_value}")
        print(f"   Primary Commission %: {order.primary_commission_percentage}")
        
        # Check field definitions
        print("\n📋 Field Metadata:")
        for fname in ['buyer_name', 'project_id', 'project_name', 'unit_sale_value', 'primary_commission_percentage']:
            field = order._fields.get(fname)
            if field:
                print(f"   {fname}: type={type(field).__name__}, store={field.store}, readonly={field.readonly}")
        
        # Check if fields are in the form view's fields_get
        print("\n🔍 Checking fields_get (what UI sees):")
        fields_info = env["sale.order"].fields_get(['buyer_name', 'project_name', 'unit_sale_value', 'primary_commission_percentage'])
        for fname, finfo in fields_info.items():
            print(f"   {fname}: {finfo.get('type')} - {finfo.get('string')}")
