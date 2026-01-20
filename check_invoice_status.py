#!/usr/bin/env python3
"""Odoo Invoice Status Checker and Fixer"""

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
                    
                    issues.append({
                        'order': order,
                        'invoices': invoices,
                        'posted_count': len(posted_invoices),
                        'draft_count': len(draft_invoices)
                    })
        
        if not issues:
            print('No invoice status issues found\n')
            return
        
        print(f'Found {len(issues)} orders with invoice status inconsistencies:\n')
        print('=' * 80)
        
        for idx, issue in enumerate(issues, 1):
            order = issue['order']
            print(f"\n{idx}. Sales Order: {order['name']}")
            print(f"   Current Status: {order['invoice_status']}")
            print(f"   Total Invoices: {order['invoice_count']}")
            print(f"   Posted: {issue['posted_count']} | Draft: {issue['draft_count']}")
            print(f"   Invoices:")
            
            for inv in issue['invoices']:
                status_icon = 'POSTED' if inv['state'] == 'posted' else 'DRAFT'
                print(f"     - {inv['name']} ({status_icon})")
            
            if issue['posted_count'] > 0:
                print(f"   Should be: invoiced")
            elif issue['draft_count'] > 0:
                print(f"   Should be: to invoice")
        
        print('\n' + '=' * 80)
        print(f'\nSummary: {len(issues)} sales orders need status correction\n')
        
        response = input('Do you want to fix these issues? (yes/no): ').strip().lower()
        
        if response == 'yes':
            print('\nFixing invoice statuses...\n')
            fixed_count = 0
            
            for issue in issues:
                order = issue['order']
                
                if issue['posted_count'] > 0:
                    correct_status = 'invoiced'
                elif issue['draft_count'] > 0:
                    correct_status = 'to invoice'
                else:
                    correct_status = 'no'
                
                try:
                    models.execute_kw(DB, uid, PASSWORD,
                        'sale.order', 'write',
                        [[order['id']], {'invoice_status': correct_status}])
                    
                    print(f"Fixed {order['name']}: {order['invoice_status']} -> {correct_status}")
                    fixed_count += 1
                except Exception as e:
                    print(f"Failed to fix {order['name']}: {str(e)}")
            
            print(f'\nFixed {fixed_count} out of {len(issues)} orders')
        else:
            print('\nNo changes made.')
    
    except Exception as e:
        print(f'\nError: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

