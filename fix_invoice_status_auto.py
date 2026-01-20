#!/usr/bin/env python3
"""Odoo Invoice Status Auto-Fixer - Runs without confirmation"""

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
        
        print('Searching for confirmed sales orders...')
        so_ids = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'search',
            [[('state', '=', 'sale')]], {'limit': 200})
        
        print(f'Found {len(so_ids)} confirmed sales orders\n')
        
        if not so_ids:
            print('No sales orders found')
            return
        
        orders = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'read',
            [so_ids],
            {'fields': ['name', 'invoice_status', 'invoice_ids', 'invoice_count']})
        
        issues = []
        for order in orders:
            if order['invoice_count'] > 0 and order['invoice_status'] != 'invoiced':
                if order['invoice_ids']:
                    invoices = models.execute_kw(DB, uid, PASSWORD,
                        'account.move', 'read',
                        [order['invoice_ids']],
                        {'fields': ['name', 'state', 'move_type']})
                    
                    posted_invoices = [inv for inv in invoices if inv['state'] == 'posted']
                    draft_invoices = [inv for inv in invoices if inv['state'] == 'draft']
                    cancel_invoices = [inv for inv in invoices if inv['state'] == 'cancel']
                    
                    issues.append({
                        'order': order,
                        'invoices': invoices,
                        'posted_count': len(posted_invoices),
                        'draft_count': len(draft_invoices),
                        'cancel_count': len(cancel_invoices)
                    })
        
        if not issues:
            print('No invoice status issues found\n')
            return
        
        print(f'Found {len(issues)} orders with invoice status inconsistencies')
        print('Automatically fixing all issues...\n')
        print('=' * 80)
        
        fixed_count = 0
        for idx, issue in enumerate(issues, 1):
            order = issue['order']
            
            # Determine correct status - ONLY posted invoices = 'invoiced'
            if issue['posted_count'] > 0:
                correct_status = 'invoiced'  # Has validated invoices
            elif issue['draft_count'] > 0:
                correct_status = 'to invoice'  # Has draft invoices (not validated)
            else:
                correct_status = 'no'  # Only cancelled or no valid invoices
            
            try:
                models.execute_kw(DB, uid, PASSWORD,
                    'sale.order', 'write',
                    [[order['id']], {'invoice_status': correct_status}])
                
                print(f"{idx:2d}. Fixed {order['name']:15s} : {order['invoice_status']:12s} -> {correct_status}")
                fixed_count += 1
            except Exception as e:
                print(f"{idx:2d}. FAILED {order['name']:15s} : {str(e)}")
        
        print('=' * 80)
        print(f'\n SUCCESS: Fixed {fixed_count} out of {len(issues)} orders')
        print(f'\nAll sales orders now have accurate invoice status!')
    
    except Exception as e:
        print(f'\nError: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
