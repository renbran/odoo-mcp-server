#!/usr/bin/env python3
"""Odoo Invoice Status Verification - Validates all statuses are correct"""

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
        
        print('Verifying all confirmed sales orders...')
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
        
        print('Analyzing invoice statuses...\n')
        print('=' * 100)
        
        correct_count = 0
        incorrect_count = 0
        categories = {
            'fully_invoiced': [],
            'has_draft': [],
            'not_invoiced': [],
            'incorrect_status': []
        }
        
        for order in orders:
            order_name = order['name']
            current_status = order['invoice_status']
            invoice_count = order['invoice_count']
            
            # Get invoice details if any
            if invoice_count > 0 and order['invoice_ids']:
                invoices = models.execute_kw(DB, uid, PASSWORD,
                    'account.move', 'read',
                    [order['invoice_ids']],
                    {'fields': ['name', 'state', 'move_type']})
                
                posted_invoices = [inv for inv in invoices if inv['state'] == 'posted']
                draft_invoices = [inv for inv in invoices if inv['state'] == 'draft']
                posted_count = len(posted_invoices)
                draft_count = len(draft_invoices)
                
                # Determine expected status
                if posted_count > 0:
                    expected_status = 'invoiced'
                    category = 'fully_invoiced'
                elif draft_count > 0:
                    expected_status = 'to invoice'
                    category = 'has_draft'
                else:
                    expected_status = 'no'
                    category = 'not_invoiced'
                
                # Check if status is correct
                if current_status == expected_status:
                    correct_count += 1
                    categories[category].append({
                        'name': order_name,
                        'status': current_status,
                        'posted': posted_count,
                        'draft': draft_count,
                        'invoices': invoices
                    })
                else:
                    incorrect_count += 1
                    categories['incorrect_status'].append({
                        'name': order_name,
                        'current': current_status,
                        'expected': expected_status,
                        'posted': posted_count,
                        'draft': draft_count,
                        'invoices': invoices
                    })
            else:
                # No invoices
                expected_status = 'no' if invoice_count == 0 else 'to invoice'
                if current_status == expected_status:
                    correct_count += 1
                    categories['not_invoiced'].append({
                        'name': order_name,
                        'status': current_status,
                        'posted': 0,
                        'draft': 0,
                        'invoices': []
                    })
                else:
                    incorrect_count += 1
                    categories['incorrect_status'].append({
                        'name': order_name,
                        'current': current_status,
                        'expected': expected_status,
                        'posted': 0,
                        'draft': 0,
                        'invoices': []
                    })
        
        # Display results by category
        print('\n1. FULLY INVOICED ORDERS (Posted Invoices)')
        print('-' * 100)
        if categories['fully_invoiced']:
            print(f'   Found {len(categories["fully_invoiced"])} orders with status = "invoiced" (CORRECT)\n')
            for idx, order in enumerate(categories['fully_invoiced'][:10], 1):
                inv_names = ', '.join([inv['name'] for inv in order['invoices'] if inv['state'] == 'posted'])
                print(f'   {idx:2d}. {order["name"]:15s} | Status: invoiced | Posted: {order["posted"]} | {inv_names[:50]}')
            if len(categories['fully_invoiced']) > 10:
                print(f'   ... and {len(categories["fully_invoiced"]) - 10} more orders')
        else:
            print('   No fully invoiced orders found')
        
        print('\n2. ORDERS WITH DRAFT INVOICES')
        print('-' * 100)
        if categories['has_draft']:
            print(f'   Found {len(categories["has_draft"])} orders with status = "to invoice" (CORRECT)\n')
            for idx, order in enumerate(categories['has_draft'][:10], 1):
                inv_names = ', '.join([f"{inv['name']} ({inv['state']})" for inv in order['invoices']])
                print(f'   {idx:2d}. {order["name"]:15s} | Status: to invoice | Draft: {order["draft"]} | {inv_names[:50]}')
            if len(categories['has_draft']) > 10:
                print(f'   ... and {len(categories["has_draft"]) - 10} more orders')
        else:
            print('   No orders with draft invoices found')
        
        print('\n3. ORDERS WITHOUT INVOICES')
        print('-' * 100)
        if categories['not_invoiced']:
            print(f'   Found {len(categories["not_invoiced"])} orders with status = "no" or "to invoice" (CORRECT)\n')
            for idx, order in enumerate(categories['not_invoiced'][:5], 1):
                print(f'   {idx:2d}. {order["name"]:15s} | Status: {order["status"]} | No invoices')
            if len(categories['not_invoiced']) > 5:
                print(f'   ... and {len(categories["not_invoiced"]) - 5} more orders')
        else:
            print('   All orders have invoices')
        
        print('\n4. INCORRECT STATUSES (ISSUES FOUND)')
        print('-' * 100)
        if categories['incorrect_status']:
            print(f'   ALERT: Found {len(categories["incorrect_status"])} orders with INCORRECT status!\n')
            for idx, order in enumerate(categories['incorrect_status'], 1):
                print(f'   {idx:2d}. {order["name"]:15s} | Current: {order["current"]:12s} | Expected: {order["expected"]:12s}')
                print(f'       Posted: {order["posted"]} | Draft: {order["draft"]}')
                if order['invoices']:
                    for inv in order['invoices']:
                        print(f'       - {inv["name"]} ({inv["state"]})')
        else:
            print('   SUCCESS: No incorrect statuses found!')
        
        # Summary
        print('\n' + '=' * 100)
        print('\nVERIFICATION SUMMARY:')
        print(f'   Total Orders Checked:  {len(orders)}')
        print(f'   Correct Statuses:      {correct_count} ({correct_count*100//len(orders)}%)')
        print(f'   Incorrect Statuses:    {incorrect_count}')
        print(f'\n   Fully Invoiced:        {len(categories["fully_invoiced"])} orders (with POSTED invoices)')
        print(f'   With Draft Invoices:   {len(categories["has_draft"])} orders (still "to invoice")')
        print(f'   Not Invoiced:          {len(categories["not_invoiced"])} orders')
        
        if incorrect_count == 0:
            print('\n   STATUS: ALL INVOICE STATUSES ARE ACCURATE!')
        else:
            print(f'\n   WARNING: {incorrect_count} orders need correction!')
        
        print('=' * 100)
    
    except Exception as e:
        print(f'\nError: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
