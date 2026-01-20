#!/usr/bin/env python3
"""Deep dive into one sales order to understand Odoo's invoice_status logic"""

import xmlrpc.client
import sys
import json

URL = 'https://erposus.com'
DB = 'osusproperties'
USERNAME = 'salescompliance@osusproperties.com'
PASSWORD = '8586583'

def main():
    try:
        print("Connecting to Odoo...")
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        
        if not uid:
            print('Authentication failed')
            sys.exit(1)
        
        print(f'Connected (UID: {uid})\n')
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Analyze PS/01/4552 - your specific order
        target_order = 'PS/01/4552'
        
        print(f'Analyzing order: {target_order}')
        print('=' * 100)
        
        # Get full order details
        order_ids = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'search',
            [[('name', '=', target_order)]])
        
        if not order_ids:
            print(f'Order {target_order} not found')
            return
        
        order = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'read',
            [order_ids],
            {'fields': [
                'name', 'state', 'invoice_status', 'invoice_ids', 'invoice_count',
                'order_line', 'amount_total', 'amount_untaxed', 'amount_tax'
            ]})[0]
        
        print(f'\nORDER DETAILS:')
        print(f'  Name: {order["name"]}')
        print(f'  State: {order["state"]}')
        print(f'  Invoice Status: {order["invoice_status"]}')
        print(f'  Invoice Count: {order["invoice_count"]}')
        print(f'  Total Amount: {order["amount_total"]}')
        
        # Get order lines
        if order['order_line']:
            lines = models.execute_kw(DB, uid, PASSWORD,
                'sale.order.line', 'read',
                [order['order_line']],
                {'fields': ['name', 'product_uom_qty', 'qty_delivered', 'qty_invoiced', 'price_unit', 'price_subtotal']})
            
            print(f'\nORDER LINES ({len(lines)} lines):')
            for idx, line in enumerate(lines, 1):
                print(f'  {idx}. {line["name"][:40]}')
                print(f'     Qty Ordered: {line["product_uom_qty"]} | Delivered: {line["qty_delivered"]} | Invoiced: {line["qty_invoiced"]}')
                print(f'     Unit Price: {line["price_unit"]} | Subtotal: {line["price_subtotal"]}')
        
        # Get invoices
        if order['invoice_ids']:
            invoices = models.execute_kw(DB, uid, PASSWORD,
                'account.move', 'read',
                [order['invoice_ids']],
                {'fields': ['name', 'state', 'move_type', 'amount_total', 'amount_untaxed', 'invoice_line_ids']})
            
            print(f'\nINVOICES ({len(invoices)} invoices):')
            for idx, inv in enumerate(invoices, 1):
                print(f'  {idx}. {inv["name"]}')
                print(f'     State: {inv["state"]} | Type: {inv["move_type"]}')
                print(f'     Amount: {inv["amount_total"]}')
                
                # Get invoice lines
                if inv['invoice_line_ids']:
                    inv_lines = models.execute_kw(DB, uid, PASSWORD,
                        'account.move.line', 'read',
                        [inv['invoice_line_ids']],
                        {'fields': ['name', 'quantity', 'price_unit', 'price_subtotal']})
                    
                    print(f'     Invoice Lines ({len(inv_lines)} lines):')
                    for il in inv_lines:
                        if il['name']:  # Skip account lines
                            print(f'       - {il["name"][:35]} | Qty: {il["quantity"]} | Total: {il["price_subtotal"]}')
        
        # Determine what status SHOULD be
        print(f'\n' + '=' * 100)
        print('ANALYSIS:')
        
        if invoices:
            posted_invs = [i for i in invoices if i['state'] == 'posted']
            draft_invs = [i for i in invoices if i['state'] == 'draft']
            cancel_invs = [i for i in invoices if i['state'] == 'cancel']
            
            print(f'  Posted Invoices: {len(posted_invs)}')
            print(f'  Draft Invoices: {len(draft_invs)}')
            print(f'  Cancelled Invoices: {len(cancel_invs)}')
            
            # Check if fully invoiced
            if lines:
                total_ordered = sum(l['product_uom_qty'] for l in lines)
                total_invoiced = sum(l['qty_invoiced'] for l in lines)
                print(f'\n  Total Qty Ordered: {total_ordered}')
                print(f'  Total Qty Invoiced: {total_invoiced}')
                print(f'  Invoicing Progress: {(total_invoiced/total_ordered*100) if total_ordered > 0 else 0:.1f}%')
                
                if total_invoiced >= total_ordered and posted_invs:
                    print(f'\n  EXPECTED STATUS: "invoiced" (100% invoiced with posted invoices)')
                elif posted_invs:
                    print(f'\n  EXPECTED STATUS: "invoiced" (partial, but has posted invoices)')
                elif draft_invs:
                    print(f'\n  EXPECTED STATUS: "to invoice" (has draft invoices only)')
                else:
                    print(f'\n  EXPECTED STATUS: "to invoice" (needs invoicing)')
            
            if order['invoice_status'] == 'upsell':
                print(f'\n  CURRENT STATUS: "upsell" - This means:')
                print(f'    - Order has been fully invoiced')
                print(f'    - BUT there are additional order lines that havent been invoiced')
                print(f'    - This suggests opportunity for additional sales (upselling)')
        
        print('=' * 100)
    
    except Exception as e:
        print(f'\nError: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
