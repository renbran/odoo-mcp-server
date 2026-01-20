#!/usr/bin/env python3
"""Odoo Invoice Status Recompute - Forces Odoo to recalculate invoice_status"""

import xmlrpc.client
import sys

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
        
        print('Searching for all confirmed sales orders...')
        so_ids = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'search',
            [[('state', '=', 'sale')]], {'limit': 200})
        
        print(f'Found {len(so_ids)} confirmed sales orders\n')
        
        if not so_ids:
            print('No sales orders found')
            return
        
        print('Triggering recomputation of invoice_status field...')
        print('=' * 80)
        
        # Method 1: Call _get_invoiced() method to recompute
        try:
            result = models.execute_kw(DB, uid, PASSWORD,
                'sale.order', 'execute',
                [so_ids, '_get_invoiced'])
            print(f'\nMethod 1 (_get_invoiced): Triggered on {len(so_ids)} orders')
        except Exception as e:
            print(f'Method 1 failed: {str(e)}')
        
        # Method 2: Recompute the field
        try:
            result = models.execute_kw(DB, uid, PASSWORD,
                'sale.order', 'execute',
                [so_ids, 'recompute'])
            print(f'Method 2 (recompute): Triggered on {len(so_ids)} orders')
        except Exception as e:
            print(f'Method 2 failed: {str(e)}')
        
        # Method 3: Call modified_fields to trigger computed fields
        try:
            result = models.execute_kw(DB, uid, PASSWORD,
                'sale.order', 'execute',
                [so_ids, 'modified', [['invoice_ids']]])
            print(f'Method 3 (modified): Triggered on {len(so_ids)} orders')
        except Exception as e:
            print(f'Method 3 failed: {str(e)}')
        
        print('=' * 80)
        print('\nRecomputation complete. Verifying results...\n')
        
        # Verify the results
        orders = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'read',
            [so_ids[:10]],
            {'fields': ['name', 'invoice_status', 'invoice_ids', 'invoice_count']})
        
        print('Sample of first 10 orders after recomputation:')
        for order in orders:
            print(f"   {order['name']:15s} | Status: {order['invoice_status']:12s} | Invoices: {order['invoice_count']}")
        
        print('\nRecomputation process completed.')
        print('Run verify_invoice_status.py to check results.')
    
    except Exception as e:
        print(f'\nError: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
