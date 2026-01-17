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
    
    # Check sale orders
    sale_orders = env["sale.order"].search([], limit=3)
    print("\n=== SALE ORDER DEAL TRACKING DATA ===")
    for order in sale_orders:
        print(f"Order {order.id}:")
        print(f"  Buyer: {order.buyer_name}")
        print(f"  Project: {order.project_name}")
        print(f"  Unit Sale Value: {order.unit_sale_value}")
        print(f"  Commission %: {order.primary_commission_percentage}")
    
    # Check account moves
    account_moves = env["account.move"].search([], limit=3)
    print("\n=== ACCOUNT MOVE DEAL TRACKING DATA ===")
    for move in account_moves:
        print(f"Move {move.id}:")
        print(f"  Buyer: {move.buyer_name}")
        print(f"  Project: {move.project_name}")
        print(f"  Commission %: {move.commission_percentage}")
        print(f"  Sale Order Ref: {move.sale_order_deal_reference}")
