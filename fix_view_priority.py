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
    
    # Update view priorities to ensure they load
    print("Updating view priorities...")
    
    deal_form_view = env["ir.ui.view"].search([
        ("name", "=", "sale.order.form.deal.tracking")
    ])
    if deal_form_view:
        deal_form_view.write({'priority': 1})
        print(f"✅ Form view priority set to 1 (was {deal_form_view.priority})")
    
    deal_tree_view = env["ir.ui.view"].search([
        ("name", "=", "sale.order.tree.deal.tracking")
    ])
    if deal_tree_view:
        deal_tree_view.write({'priority': 1})
        print(f"✅ Tree view priority set to 1")
    
    # Check for any disabled views
    print("\n🔍 Checking for inactive/disabled deal tracking views:")
    all_deal_views = env["ir.ui.view"].search([
        ("model", "in", ["sale.order", "account.move"]),
        ("name", "ilike", "deal")
    ])
    for view in all_deal_views:
        status = "✅ ACTIVE" if view.active else "❌ INACTIVE"
        print(f"   {status}: {view.name} (priority={view.priority})")
    
    # Get the actual view used for sale.order form
    print("\n📋 Sale Order Form View Inheritance Chain:")
    base_view = env.ref("sale.view_order_form")
    print(f"   Base: {base_view.name} (ID: {base_view.id})")
    
    # Find all views that inherit from it
    inheriting_views = env["ir.ui.view"].search([
        ("inherit_id", "=", base_view.id),
        ("model", "=", "sale.order")
    ])
    print(f"\n   Found {len(inheriting_views)} inheriting views:")
    for view in inheriting_views:
        active_mark = "✅" if view.active else "❌"
        print(f"   {active_mark} {view.name} (priority={view.priority}, module={view.xml_id.split('.')[0] if view.xml_id else 'N/A'})")
    
    cr.commit()
    print("\n✅ View priorities updated!")
