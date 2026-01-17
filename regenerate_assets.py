#!/usr/bin/env python3
"""
Force regeneration of all assets and clear all UI caches
"""
import os, sys
sys.path.insert(0, "/var/odoo/scholarixv2/src")
os.chdir("/var/odoo/scholarixv2")
os.environ.setdefault("ODOO_RC", "/var/odoo/scholarixv2/odoo.conf")

import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry("commission_ax")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Clear all view caches
    print("Clearing view caches...")
    env["ir.ui.view"].clear_caches()
    
    # Clear model caches
    print("Clearing model caches...")
    env["ir.model"].clear_caches()
    env["ir.model.fields"].clear_caches()
    
    # Regenerate all assets
    print("Regenerating assets...")
    IrAttachment = env["ir.attachment"]
    assets = IrAttachment.search([
        ("name", "ilike", "assets_%"),
        ("res_model", "=", "ir.ui.view")
    ])
    if assets:
        assets.unlink()
        print(f"✅ Deleted {len(assets)} asset bundles - will regenerate on next page load")
    
    # Clear all QWeb caches
    print("Clearing QWeb template caches...")
    registry.clear_cache()
    
    # Force recomputation of views
    print("Invalidating view inheritance...")
    all_views = env["ir.ui.view"].search([])
    for view in all_views:
        view.flush_recordset()
    
    cr.commit()
    print("\n✅ All caches cleared and assets regenerated!")
    print("📋 Next steps:")
    print("   1. Clear your browser cache (Ctrl+Shift+Delete)")
    print("   2. Do a hard refresh (Ctrl+F5)")
    print("   3. Navigate to Sales > Orders")
    print("   4. The deal tracking fields should now be visible!")
