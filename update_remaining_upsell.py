#!/usr/bin/env python3
"""Update remaining upsell orders"""

import xmlrpc.client

URL = 'https://erposus.com'
DB = 'osusproperties'
USERNAME = 'salescompliance@osusproperties.com'
PASSWORD = '8586583'

def main():
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    # Find remaining upsell orders
    upsell_ids = models.execute_kw(DB, uid, PASSWORD,
        'sale.order', 'search',
        [[('invoice_status', '=', 'upsell')]])
    
    orders = models.execute_kw(DB, uid, PASSWORD,
        'sale.order', 'read',
        [upsell_ids],
        {'fields': ['name', 'amount_total', 'invoice_ids']})
    
    print(f'\nFound {len(orders)} remaining upsell orders')
    print('Updating automatically...\n')
    
    for order in orders:
        # Get invoice total
        if order['invoice_ids']:
            invoices = models.execute_kw(DB, uid, PASSWORD,
                'account.move', 'read',
                [order['invoice_ids']],
                {'fields': ['amount_total', 'state', 'move_type']})
            
            posted = [i for i in invoices if i['state'] == 'posted' and i['move_type'] == 'out_invoice']
            inv_total = sum(i['amount_total'] for i in posted)
            
            # Update
            models.execute_kw(DB, uid, PASSWORD,
                'sale.order', 'write',
                [[order['id']], {'invoice_status': 'invoiced'}])
            
            diff = inv_total - order['amount_total']
            order_name = order['name']
            order_amt = order['amount_total']
            print(f'Updated {order_name:15s} Order: {order_amt:10.2f} -> Invoice: {inv_total:10.2f} (diff: {diff:+10.2f})')
    
    print(f'\nAll upsell orders updated to invoiced status!')

if __name__ == '__main__':
    main()
