#!/usr/bin/env python3
import os
import sys

# Add Odoo to path
sys.path.insert(0, "/var/odoo/scholarixv2/src")
os.chdir("/var/odoo/scholarixv2")
os.environ.setdefault("ODOO_RC", "/var/odoo/scholarixv2/odoo.conf")

import odoo
from odoo import api, SUPERUSER_ID

# Create database registry
registry = odoo.registry("commission_ax")

# Use the registry to access models
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check sale_order fields
    sale_order_model = env["sale.order"]
    print("=== SALE ORDER FIELDS ===")
    deal_fields = {k: v for k, v in sale_order_model._fields.items() 
                   if any(x in k for x in ['buyer', 'project', 'unit_sale', 'commission', 'deal'])}
    for fname, fld in deal_fields.items():
        print(f"  {fname}: {type(fld).__name__} (stored={getattr(fld, 'store', False)})")
    
    # Check account_move fields
    account_move_model = env["account.move"]
    print("\n=== ACCOUNT MOVE FIELDS ===")
    deal_fields = {k: v for k, v in account_move_model._fields.items() 
                   if any(x in k for x in ['buyer', 'project', 'unit_sale', 'commission', 'deal', 'sale_order'])}
    for fname, fld in deal_fields.items():
        print(f"  {fname}: {type(fld).__name__} (stored={getattr(fld, 'store', False)})")
