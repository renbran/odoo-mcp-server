#!/usr/bin/env python3
import os, sys
sys.path.insert(0, "/var/odoo/scholarixv2/src")
os.chdir("/var/odoo/scholarixv2")
os.environ.setdefault("ODOO_RC", "/var/odoo/scholarixv2/odoo.conf")

import odoo
from odoo import api, SUPERUSER_ID

# Use scholarixv2 database
registry = odoo.registry("scholarixv2")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    print("🔍 Checking deal tracking fields on scholarixv2 database...")
    
    # Check if commission_ax module is installed
    module = env["ir.module.module"].search([("name", "=", "commission_ax")])
    if module:
        print(f"   Module state: {module.state}")
        if module.state != "installed":
            print("   ❌ Module not installed! Installing now...")
            module.button_immediate_install()
    
    # Check fields
    sale_order = env["sale.order"].search([], limit=1)
    if sale_order:
        print(f"\n✅ Sample sale order ID: {sale_order.id}")
        print(f"   Buyer Name: {sale_order.buyer_name}")
        print(f"   Project Name: {sale_order.project_name}")
        print(f"   Unit Sale Value: {sale_order.unit_sale_value}")
    
    # Clear caches
    print("\n🔄 Clearing all caches...")
    env["ir.ui.view"].clear_caches()
    env["ir.model"].clear_caches()
    env["ir.model.fields"].clear_caches()
    
    # Delete assets
    print("🗑️  Deleting cached assets...")
    IrAttachment = env["ir.attachment"]
    assets = IrAttachment.search([
        ("name", "ilike", "assets_%"),
        ("res_model", "=", "ir.ui.view")
    ])
    if assets:
        assets.unlink()
        print(f"   ✅ Deleted {len(assets)} asset bundles")
    
    registry.clear_cache()
    cr.commit()
    print("\n✅ scholarixv2 database ready!")
    print("📋 Clear your browser cache and refresh!")
