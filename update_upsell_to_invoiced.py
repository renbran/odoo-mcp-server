#!/usr/bin/env python3
"""
Update Upsell Orders to Invoiced Status
Logs all details before making changes
"""

import xmlrpc.client
import sys
from datetime import datetime
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
        
        print('Searching for orders with "upsell" status...')
        upsell_ids = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'search',
            [[('state', '=', 'sale'), ('invoice_status', '=', 'upsell')]])
        
        print(f'Found {len(upsell_ids)} orders with upsell status\n')
        
        if not upsell_ids:
            print('No upsell orders found')
            return
        
        # Read order details
        orders = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'read',
            [upsell_ids],
            {'fields': ['name', 'invoice_status', 'invoice_ids', 'amount_total', 'amount_untaxed']})
        
        # Prepare log data
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'database': DB,
            'user': USERNAME,
            'total_orders': len(orders),
            'orders': []
        }
        
        print('=' * 100)
        print('UPSELL ORDERS ANALYSIS - BEFORE UPDATE')
        print('=' * 100)
        print(f'\n{"Order":<15} {"Status":<12} {"Order Value":<15} {"Invoice Value":<15} {"Difference":<15} {"Posted Invs"}')
        print('-' * 100)
        
        for order in orders:
            order_total = order['amount_total']
            
            # Get invoice totals
            if order['invoice_ids']:
                invoices = models.execute_kw(DB, uid, PASSWORD,
                    'account.move', 'read',
                    [order['invoice_ids']],
                    {'fields': ['name', 'state', 'amount_total', 'move_type']})
                
                posted_invoices = [inv for inv in invoices if inv['state'] == 'posted']
                invoice_total = sum(inv['amount_total'] for inv in posted_invoices if inv['move_type'] == 'out_invoice')
                refund_total = sum(inv['amount_total'] for inv in posted_invoices if inv['move_type'] == 'out_refund')
                net_invoice_total = invoice_total - refund_total
                
                difference = net_invoice_total - order_total
                
                # Log entry
                log_entry = {
                    'order_id': order['id'],
                    'order_name': order['name'],
                    'current_status': order['invoice_status'],
                    'order_value': order_total,
                    'invoice_value': net_invoice_total,
                    'difference': difference,
                    'posted_invoice_count': len(posted_invoices),
                    'invoices': [
                        {
                            'name': inv['name'],
                            'state': inv['state'],
                            'type': inv['move_type'],
                            'amount': inv['amount_total']
                        } for inv in invoices
                    ]
                }
                log_data['orders'].append(log_entry)
                
                # Display
                print(f'{order["name"]:<15} {order["invoice_status"]:<12} {order_total:>13.2f} {net_invoice_total:>13.2f} {difference:>13.2f} {len(posted_invoices):>12}')
        
        print('-' * 100)
        print(f'Total: {len(orders)} orders\n')
        
        # Save log file
        log_filename = f'upsell_update_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(log_filename, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f'Log saved to: {log_filename}')
        
        # Confirmation
        print('\n' + '=' * 100)
        print('EXPLANATION:')
        print('=' * 100)
        print('These orders have "upsell" status because:')
        print('  - They have been fully invoiced (invoice posted)')
        print('  - The invoiced amount may exceed the original order value')
        print('  - This represents additional sales/upselling that occurred')
        print('\nThese orders SHOULD be marked as "invoiced" because:')
        print('  - They ARE fully invoiced (invoices are posted)')
        print('  - "upsell" is not a standard invoice status')
        print('  - The correct status for posted invoices is "invoiced"')
        print('=' * 100)
        
        response = input('\nDo you want to update these orders to "invoiced" status? (yes/no): ').strip().lower()
        
        if response == 'yes':
            print('\nUpdating orders...\n')
            print('=' * 100)
            
            updated = 0
            failed = 0
            
            for order in orders:
                try:
                    # Update to invoiced status
                    models.execute_kw(DB, uid, PASSWORD,
                        'sale.order', 'write',
                        [[order['id']], {'invoice_status': 'invoiced'}])
                    
                    print(f"✓ Updated {order['name']:15s} : upsell -> invoiced")
                    updated += 1
                except Exception as e:
                    print(f"✗ Failed {order['name']:15s} : {str(e)[:50]}")
                    failed += 1
            
            print('=' * 100)
            print(f'\nResults: {updated} updated, {failed} failed')
            print(f'Log file: {log_filename}')
            
            # Save update results to log
            log_data['update_results'] = {
                'updated': updated,
                'failed': failed,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(log_filename, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            print(f'\nFinal log saved to: {log_filename}')
        else:
            print('\nNo changes made.')
            print(f'Log file saved: {log_filename}')
    
    except Exception as e:
        print(f'\nError: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
