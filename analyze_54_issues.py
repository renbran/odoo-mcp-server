#!/usr/bin/env python3
"""Detailed analysis of the 54 orders with incorrect status"""

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
        
        # Get all confirmed sales orders
        so_ids = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'search',
            [[('state', '=', 'sale')]], {'limit': 200})
        
        orders = models.execute_kw(DB, uid, PASSWORD,
            'sale.order', 'read',
            [so_ids],
            {'fields': ['id', 'name', 'invoice_status', 'invoice_ids', 'invoice_count']})
        
        print('Analyzing all orders for status issues...\n')
        
        issues_by_type = {
            'posted_but_wrong_status': [],
            'draft_marked_as_invoiced': [],
            'cancelled_marked_as_to_invoice': [],
            'no_invoices_but_has_status': [],
            'other_issues': []
        }
        
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
            cancel = [i for i in invoices if i['state'] == 'cancel']
            current_status = order['invoice_status']
            
            # Categorize the issue
            if posted and current_status != 'invoiced':
                issues_by_type['posted_but_wrong_status'].append({
                    'order': order['name'],
                    'current_status': current_status,
                    'expected': 'invoiced',
                    'posted': len(posted),
                    'draft': len(draft),
                    'cancel': len(cancel),
                    'invoices': [f"{i['name']} ({i['state']})" for i in invoices]
                })
            elif not posted and not draft and current_status == 'invoiced':
                issues_by_type['cancelled_marked_as_to_invoice'].append({
                    'order': order['name'],
                    'current_status': current_status,
                    'expected': 'no',
                    'posted': 0,
                    'draft': 0,
                    'cancel': len(cancel),
                    'invoices': [f"{i['name']} ({i['state']})" for i in invoices]
                })
            elif draft and not posted and current_status == 'invoiced':
                issues_by_type['draft_marked_as_invoiced'].append({
                    'order': order['name'],
                    'current_status': current_status,
                    'expected': 'to invoice',
                    'posted': 0,
                    'draft': len(draft),
                    'cancel': len(cancel),
                    'invoices': [f"{i['name']} ({i['state']})" for i in invoices]
                })
            elif not posted and not draft and current_status == 'to invoice':
                issues_by_type['no_invoices_but_has_status'].append({
                    'order': order['name'],
                    'current_status': current_status,
                    'expected': 'no',
                    'posted': 0,
                    'draft': 0,
                    'cancel': len(cancel),
                    'invoices': [f"{i['name']} ({i['state']})" for i in invoices]
                })
        
        # Display categorized issues
        print('=' * 100)
        print('ISSUE BREAKDOWN - 54 ORDERS WITH INCORRECT STATUS')
        print('=' * 100)
        
        # Issue Type 1: Has POSTED invoices but wrong status
        if issues_by_type['posted_but_wrong_status']:
            print(f"\n1. ORDERS WITH POSTED INVOICES - SHOULD BE 'invoiced'")
            print(f"   Count: {len(issues_by_type['posted_but_wrong_status'])}")
            print('-' * 100)
            for idx, issue in enumerate(issues_by_type['posted_but_wrong_status'][:10], 1):
                print(f"   {idx:2d}. {issue['order']:15s} | Current: {issue['current_status']:12s} | Posted: {issue['posted']} | Draft: {issue['draft']}")
                for inv in issue['invoices'][:2]:
                    print(f"       - {inv}")
            if len(issues_by_type['posted_but_wrong_status']) > 10:
                print(f"       ... and {len(issues_by_type['posted_but_wrong_status']) - 10} more orders")
        
        # Issue Type 2: Has ONLY DRAFT invoices but marked as 'invoiced'
        if issues_by_type['draft_marked_as_invoiced']:
            print(f"\n2. DRAFT INVOICES MARKED AS 'invoiced' - CRITICAL ERROR!")
            print(f"   Count: {len(issues_by_type['draft_marked_as_invoiced'])}")
            print('-' * 100)
            print("   These should be 'to invoice' (drafts are NOT validated)")
            for idx, issue in enumerate(issues_by_type['draft_marked_as_invoiced'], 1):
                print(f"   {idx:2d}. {issue['order']:15s} | Current: {issue['current_status']:12s} | Draft: {issue['draft']}")
                for inv in issue['invoices']:
                    print(f"       - {inv}")
        
        # Issue Type 3: Has ONLY CANCELLED invoices but marked as 'to invoice'
        if issues_by_type['no_invoices_but_has_status']:
            print(f"\n3. CANCELLED/NO INVOICES MARKED AS 'to invoice'")
            print(f"   Count: {len(issues_by_type['no_invoices_but_has_status'])}")
            print('-' * 100)
            print("   These should be 'no' (no valid invoices)")
            for idx, issue in enumerate(issues_by_type['no_invoices_but_has_status'][:10], 1):
                print(f"   {idx:2d}. {issue['order']:15s} | Current: {issue['current_status']:12s} | Cancelled: {issue['cancel']}")
            if len(issues_by_type['no_invoices_but_has_status']) > 10:
                print(f"       ... and {len(issues_by_type['no_invoices_but_has_status']) - 10} more orders")
        
        # Issue Type 4: Other status issues
        if issues_by_type['cancelled_marked_as_to_invoice']:
            print(f"\n4. OTHER STATUS ISSUES")
            print(f"   Count: {len(issues_by_type['cancelled_marked_as_to_invoice'])}")
            print('-' * 100)
            for idx, issue in enumerate(issues_by_type['cancelled_marked_as_to_invoice'], 1):
                print(f"   {idx:2d}. {issue['order']:15s} | Current: {issue['current_status']:12s} | Expected: {issue['expected']}")
        
        # Summary
        total_issues = sum(len(v) for v in issues_by_type.values())
        print('\n' + '=' * 100)
        print('SUMMARY BY ISSUE TYPE:')
        print('=' * 100)
        print(f"  Posted invoices (wrong status):        {len(issues_by_type['posted_but_wrong_status']):3d} orders")
        print(f"  Draft invoices marked as 'invoiced':   {len(issues_by_type['draft_marked_as_invoiced']):3d} orders (CRITICAL!)")
        print(f"  Cancelled invoices need status update: {len(issues_by_type['no_invoices_but_has_status']):3d} orders")
        print(f"  Other issues:                           {len(issues_by_type['cancelled_marked_as_to_invoice']):3d} orders")
        print('-' * 100)
        print(f"  TOTAL ISSUES:                           {total_issues:3d} orders")
        print('=' * 100)
        
        # Root cause analysis
        print('\nROOT CAUSES:')
        print('  1. Odoo is auto-computing invoice_status based on order lines')
        print('  2. Some orders have additional order lines not yet invoiced')
        print('  3. Draft invoices incorrectly showing as "invoiced"')
        print('  4. Cancelled invoices not updating parent order status')
        
        print('\nRECOMMENDED ACTIONS:')
        print('  1. Fix CRITICAL issue: Draft invoices showing as "invoiced"')
        print('  2. Update orders with posted invoices to "invoiced"')
        print('  3. Update orders with only cancelled invoices to "no"')
        print('  4. Review order lines to ensure quantities match')
        
    except Exception as e:
        print(f'\nError: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
