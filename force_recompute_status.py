#!/usr/bin/env python3
"""Force flush and recompute invoice_status using direct SQL access via Odoo"""

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
        
        print('Finding orders with incorrect status...')
        print('=' * 80)
        
        # Get all confirmed sales orders
        so_ids = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'search',
            [[('state', '=', 'sale')]], {'limit': 200})
        
        orders = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'read',
            [so_ids],
            {'fields': ['id', 'name', 'invoice_status', 'invoice_ids']})
        
        updates_needed = []
        
        for order in orders:
            if not order['invoice_ids']:
                continue
            
            # Get invoice states
            invoices = models.execute_kw(DB, uid, PASSWORD,
                'account.move', 'read',
                [order['invoice_ids']],
                {'fields': ['id', 'name', 'state', 'move_type']})
            
            posted = [i for i in invoices if i['state'] == 'posted']
            draft = [i for i in invoices if i['state'] == 'draft']
            current_status = order['invoice_status']
            
            # Determine what status SHOULD be
            if posted:
                expected = 'invoiced'
            elif draft:
                expected = 'to invoice'
            else:
                expected = 'no'
            
            if current_status != expected:
                updates_needed.append({
                    'id': order['id'],
                    'name': order['name'],
                    'current': current_status,
                    'expected': expected,
                    'posted': len(posted),
                    'draft': len(draft)
                })
        
        if not updates_needed:
            print('All statuses are correct!')
            return
        
        print(f'Found {len(updates_needed)} orders with incorrect status\n')
        
        # The key insight: We need to invalidate the cache and force recomputation
        # by modifying a related field that triggers the computed field
        
        print('Forcing recomputation by touching invoice_ids field...\n')
        
        fixed = 0
        failed = 0
        
        for upd in updates_needed:
            try:
                # Read current invoice_ids
                current_invoice_ids = models.execute_kw(DB, uid, PASSWORD,
                    'sale.order', 'read',
                    [[upd['id']]], {'fields': ['invoice_ids']})[0]['invoice_ids']
                
                # Write the same value back - this triggers recomputation
                models.execute_kw(DB, uid, PASSWORD,
                    'sale.order', 'write',
                    [[upd['id']], {'invoice_ids': [(6, 0, current_invoice_ids)]}])
                
                # Verify the change
                new_status = models.execute_kw(DB, uid, PASSWORD,
                    'sale.order', 'read',
                    [[upd['id']]], {'fields': ['invoice_status']})[0]['invoice_status']
                
                if new_status == upd['expected']:
                    print(f"✓ {upd['name']:15s} : {upd['current']:12s} -> {new_status}")
                    fixed += 1
                else:
                    print(f"✗ {upd['name']:15s} : Still {new_status} (expected {upd['expected']})")
                    failed += 1
                    
            except Exception as e:
                print(f"✗ {upd['name']:15s} : Error - {str(e)[:50]}")
                failed += 1
        
        print('=' * 80)
        print(f'\nResults: {fixed} fixed, {failed} failed')
        
        if failed > 0:
            print('\nNote: Some orders may require manual intervention in Odoo UI.')
            print('Try: Sales Order -> Edit -> Save (this triggers recomputation)')
    
    except Exception as e:
        print(f'\nError: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
