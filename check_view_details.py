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
    
    # Get the deal tracking form view
    form_view = env["ir.ui.view"].search([
        ("name", "=", "sale.order.form.deal.tracking"),
        ("model", "=", "sale.order")
    ], limit=1)
    
    if form_view:
        print("✅ SALE ORDER FORM VIEW FOUND:")
        print(f"   ID: {form_view.id}")
        print(f"   Active: {form_view.active}")
        print(f"   Mode: {form_view.mode}")
        print(f"   Priority: {form_view.priority}")
        print(f"   Inherit ID: {form_view.inherit_id.name if form_view.inherit_id else 'None'}")
        print("\n📋 ARCH (structure):")
        print(form_view.arch[:500] if form_view.arch else "No arch")
    
    # Get the tree view
    tree_view = env["ir.ui.view"].search([
        ("name", "=", "sale.order.tree.deal.tracking"),
        ("model", "=", "sale.order")
    ], limit=1)
    
    if tree_view:
        print("\n\n✅ SALE ORDER TREE VIEW FOUND:")
        print(f"   ID: {tree_view.id}")
        print(f"   Active: {tree_view.active}")
        print(f"   Inherit ID: {tree_view.inherit_id.name if tree_view.inherit_id else 'None'}")
        print("\n📋 ARCH (structure):")
        print(tree_view.arch[:500] if tree_view.arch else "No arch")
