#!/usr/bin/env python3
"""
Identify Partial Invoicing Scenarios
-------------------------------------
Analyzes order lines to identify orders where some lines are invoiced but not all.
Note: Odoo doesn't have a "partially invoiced" status - these show as "to invoice"
This script helps identify which orders are partially vs fully invoiced.

Author: SGC TECH AI
Date: 2026-01-19
"""

import xmlrpc.client
import json
from datetime import datetime

# Odoo connection details
url = 'https://erposus.com'
db = 'osusproperties'
username = 'salescompliance@osusproperties.com'
password = '8586583'

def main():
    print("=" * 100)
    print("IDENTIFY PARTIAL INVOICING SCENARIOS")
    print("=" * 100)
    print("\nNote: Odoo standard only has these statuses:")
    print("  - 'no' = Nothing to invoice")
    print("  - 'to invoice' = Needs invoicing (includes PARTIAL)")
    print("  - 'invoiced' = Fully invoiced")
    print("  - 'upsell' = Over-invoiced")
    print("\nThis script identifies which 'to invoice' orders are PARTIAL vs NOT STARTED")
    
    # Connect to Odoo
    print("\nConnecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("Authentication failed!")
        return
    
    print(f"Connected (UID: {uid})")
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Get all confirmed sales orders with "to invoice" status
    print("\nSearching for confirmed orders with 'to invoice' status...")
    order_ids = models.execute_kw(
        db, uid, password,
        'sale.order', 'search',
        [[['state', 'in', ['sale', 'done']], ['invoice_status', '=', 'to invoice']]],
        {'limit': 100}
    )
    
    print(f"Found {len(order_ids)} orders to analyze")
    
    # Get order details
    orders = models.execute_kw(
        db, uid, password,
        'sale.order', 'read',
        [order_ids, ['name', 'invoice_status', 'order_line', 'invoice_ids', 'amount_total']]
    )
    
    partial_invoicing = []
    not_invoiced = []
    
    print("\nAnalyzing order lines...")
    
    for order in orders:
        if not order['order_line']:
            continue
        
        # Get order line details
        order_lines = models.execute_kw(
            db, uid, password,
            'sale.order.line', 'read',
            [order['order_line'], ['product_id', 'product_uom_qty', 'qty_delivered', 'qty_invoiced', 'price_subtotal']]
        )
        
        # Calculate totals
        total_ordered_qty = sum(line['product_uom_qty'] for line in order_lines)
        total_invoiced_qty = sum(line['qty_invoiced'] for line in order_lines)
        total_delivered_qty = sum(line['qty_delivered'] for line in order_lines)
        
        # Get invoice details
        posted_invoices = []
        draft_invoices = []
        if order['invoice_ids']:
            invoices = models.execute_kw(
                db, uid, password,
                'account.move', 'read',
                [order['invoice_ids'], ['name', 'state', 'move_type', 'amount_total']]
            )
            posted_invoices = [inv for inv in invoices if inv['state'] == 'posted' and inv['move_type'] == 'out_invoice']
            draft_invoices = [inv for inv in invoices if inv['state'] == 'draft']
        
        # Determine if partial or not invoiced
        if total_invoiced_qty > 0 and total_invoiced_qty < total_ordered_qty:
            # PARTIAL INVOICING
            partial_invoicing.append({
                'order': order,
                'order_lines': order_lines,
                'total_ordered_qty': total_ordered_qty,
                'total_invoiced_qty': total_invoiced_qty,
                'total_delivered_qty': total_delivered_qty,
                'posted_invoices': posted_invoices,
                'draft_invoices': draft_invoices,
                'invoicing_percentage': (total_invoiced_qty / total_ordered_qty * 100) if total_ordered_qty > 0 else 0
            })
        elif total_invoiced_qty == 0:
            # NOT INVOICED YET
            not_invoiced.append({
                'order': order,
                'order_lines': order_lines,
                'total_ordered_qty': total_ordered_qty,
                'total_delivered_qty': total_delivered_qty,
                'draft_invoices': draft_invoices
            })
    
    # Display results
    print("\n" + "=" * 100)
    print(f"PARTIAL INVOICING - {len(partial_invoicing)} ORDERS")
    print("=" * 100)
    print("These orders have SOME lines invoiced but not ALL (should remain 'to invoice')")
    
    if partial_invoicing:
        for idx, item in enumerate(partial_invoicing[:20], 1):  # Show top 20
            order = item['order']
            print(f"\n{idx}. Order: {order['name']}")
            print(f"   Status: {order['invoice_status']} (CORRECT - partial invoicing in progress)")
            print(f"   Order Amount: {order['amount_total']:.2f} AED")
            print(f"   Total Ordered Qty: {item['total_ordered_qty']:.2f}")
            print(f"   Total Invoiced Qty: {item['total_invoiced_qty']:.2f}")
            print(f"   Invoicing Progress: {item['invoicing_percentage']:.1f}%")
            
            if item['posted_invoices']:
                total_invoiced = sum(inv['amount_total'] for inv in item['posted_invoices'])
                print(f"   Posted Invoices: {len(item['posted_invoices'])} ({total_invoiced:.2f} AED)")
            
            if item['draft_invoices']:
                print(f"   Draft Invoices: {len(item['draft_invoices'])}")
            
            # Show line details
            print(f"   Order Lines:")
            for line in item['order_lines']:
                product_name = line['product_id'][1] if line['product_id'] else 'No Product'
                invoiced_pct = (line['qty_invoiced'] / line['product_uom_qty'] * 100) if line['product_uom_qty'] > 0 else 0
                print(f"     - {product_name}: Ordered={line['product_uom_qty']:.0f}, Invoiced={line['qty_invoiced']:.0f} ({invoiced_pct:.0f}%)")
        
        if len(partial_invoicing) > 20:
            print(f"\n   ... and {len(partial_invoicing) - 20} more partial invoicing orders")
    else:
        print("\nNo partial invoicing found!")
    
    print("\n" + "=" * 100)
    print(f"NOT YET INVOICED - {len(not_invoiced)} ORDERS")
    print("=" * 100)
    print("These orders have NO invoiced quantities yet (correctly 'to invoice')")
    
    if not_invoiced:
        for idx, item in enumerate(not_invoiced[:10], 1):  # Show top 10
            order = item['order']
            print(f"\n{idx}. Order: {order['name']}")
            print(f"   Status: {order['invoice_status']} (CORRECT - not yet invoiced)")
            print(f"   Order Amount: {order['amount_total']:.2f} AED")
            print(f"   Total Ordered Qty: {item['total_ordered_qty']:.2f}")
            print(f"   Total Delivered Qty: {item['total_delivered_qty']:.2f}")
            
            if item['draft_invoices']:
                print(f"   Draft Invoices: {len(item['draft_invoices'])} (not validated yet)")
        
        if len(not_invoiced) > 10:
            print(f"\n   ... and {len(not_invoiced) - 10} more uninvoiced orders")
    else:
        print("\nNo uninvoiced orders found!")
    
    # Save detailed report
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'database': db,
        'summary': {
            'total_to_invoice_orders': len(orders),
            'partial_invoicing': len(partial_invoicing),
            'not_invoiced': len(not_invoiced)
        },
        'partial_invoicing_orders': [
            {
                'order_name': item['order']['name'],
                'order_amount': item['order']['amount_total'],
                'ordered_qty': item['total_ordered_qty'],
                'invoiced_qty': item['total_invoiced_qty'],
                'invoicing_percentage': item['invoicing_percentage'],
                'posted_invoices': len(item['posted_invoices']),
                'draft_invoices': len(item['draft_invoices'])
            }
            for item in partial_invoicing
        ],
        'not_invoiced_orders': [
            {
                'order_name': item['order']['name'],
                'order_amount': item['order']['amount_total'],
                'ordered_qty': item['total_ordered_qty'],
                'delivered_qty': item['total_delivered_qty'],
                'draft_invoices': len(item['draft_invoices'])
            }
            for item in not_invoiced
        ]
    }
    
    report_filename = f"partial_invoicing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Total 'to invoice' orders analyzed: {len(orders)}")
    print(f"Partial invoicing (some lines done): {len(partial_invoicing)}")
    print(f"Not invoiced yet (no lines done): {len(not_invoiced)}")
    print(f"\nDetailed report saved: {report_filename}")
    
    print("\n" + "=" * 100)
    print("IMPORTANT NOTE")
    print("=" * 100)
    print("Odoo doesn't have a 'partially invoiced' status by default.")
    print("Both partial and not-yet-invoiced show as 'to invoice'.")
    print("\nIf you need to distinguish these in the UI, you would need to:")
    print("1. Add a custom field to track invoicing percentage")
    print("2. Add a custom status or label in the form view")
    print("3. Create a custom filter/view for partial invoicing")

if __name__ == '__main__':
    main()
