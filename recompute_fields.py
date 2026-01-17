#!/usr/bin/env python3
"""
Trigger recomputation of stored fields for sale orders and account moves
"""
import os
import sys

sys.path.insert(0, "/var/odoo/scholarixv2/src")
os.chdir("/var/odoo/scholarixv2")
os.environ.setdefault("ODOO_RC", "/var/odoo/scholarixv2/odoo.conf")

import odoo
from odoo import api, SUPERUSER_ID

registry = odoo.registry("commission_ax")

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Recompute all sale orders with deal tracking fields
    print("Recomputing sale order deal tracking fields...")
    sale_orders = env["sale.order"].search([])
    for order in sale_orders:
        order._compute_buyer_name()
        order._compute_project_name()
        order._compute_unit_sale_value()
        order._compute_primary_commission_percentage()
        order._compute_deal_summary_html()
    
    # Write the computed values to database
    for order in sale_orders:
        order.write({
            'buyer_name': order.buyer_name,
            'project_name': order.project_name,
            'unit_sale_value': order.unit_sale_value,
            'primary_commission_percentage': order.primary_commission_percentage,
        })
    
    print(f"✅ Recomputed {len(sale_orders)} sale orders")
    
    # Recompute all account moves with deal tracking fields
    print("Recomputing account move deal tracking fields...")
    account_moves = env["account.move"].search([])
    for move in account_moves:
        if hasattr(move, '_compute_deal_information_summary'):
            move._compute_deal_information_summary()
    
    # Write the computed values
    for move in account_moves:
        if move.buyer_name or move.project_name or move.commission_percentage:
            move.write({
                'buyer_name': move.buyer_name,
                'project_name': move.project_name,
                'unit_sale_value': move.unit_sale_value,
                'commission_percentage': move.commission_percentage,
                'sale_order_deal_reference': move.sale_order_deal_reference,
            })
    
    print(f"✅ Recomputed {len(account_moves)} account moves")
    cr.commit()
    print("✅ Changes committed to database")
