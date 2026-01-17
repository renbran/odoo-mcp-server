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
    
    # Check if views are registered
    views = env["ir.ui.view"].search([
        ("model", "in", ["sale.order", "account.move"]),
        ("name", "ilike", "deal")
    ])
    
    print(f"Found {len(views)} deal tracking views:")
    for view in views:
        print(f"  - {view.name} ({view.type}) - Active: {view.active} - ID: {view.id}")
    
    # Check all sale.order views
    all_sale_views = env["ir.ui.view"].search([("model", "=", "sale.order")])
    print(f"\nTotal sale.order views: {len(all_sale_views)}")
    
    # Clear all caches
    env["ir.ui.view"].clear_caches()
    env["ir.model"].clear_caches()
    env["ir.model.fields"].clear_caches()
    cr.commit()
    print("\n✅ All caches cleared and committed")
