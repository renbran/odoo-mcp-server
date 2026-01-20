#!/usr/bin/env python3
"""
Fix Posted Invoices with Wrong Status
--------------------------------------
Updates 14 orders that have posted (validated) invoices but show wrong status
These should all be "invoiced" status.

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
    print("FIX: Posted Invoices with Wrong Status")
    print("=" * 100)
    
    # Connect to Odoo
    print("\nConnecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("Authentication failed!")
        return
    
    print(f"Connected (UID: {uid})")
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # List of 14 orders with posted invoices but wrong status
    order_names = [
        'PS/07/4343',  # to invoice (has 2 posted)
        'PS/01/4554',  # to invoice (has 1 posted)
        'S01973',      # to invoice (has 1 posted)
        'PS/11/4541',  # to invoice (has 1 posted)
        'ES/11/7678',  # to invoice (has 1 posted)
        'S01883',      # upsell (has 1 posted)
        'S01880',      # to invoice (has 1 posted)
        'PS/07/4353',  # upsell (has 1 posted)
        'PS/10/4524',  # to invoice (has 2 posted)
        'ES/10/7661',  # upsell (has 1 posted)
        'ES/10/7660',  # upsell (has 1 posted)
        'PS/10/4522',  # to invoice (has 1 posted)
        'PS/10/4519',  # to invoice (has 1 posted)
        'PS/10/4520',  # to invoice (has 1 posted)
    ]
    
    print(f"\nSearching for {len(order_names)} orders with posted invoice status issues...")
    
    # Search for these orders
    order_ids = models.execute_kw(
        db, uid, password,
        'sale.order', 'search',
        [[['name', 'in', order_names]]]
    )
    
    if not order_ids:
        print("No orders found!")
        return
    
    print(f"Found {len(order_ids)} orders")
    
    # Get order details
    orders = models.execute_kw(
        db, uid, password,
        'sale.order', 'read',
        [order_ids, ['name', 'invoice_status', 'invoice_ids', 'amount_total']]
    )
    
    # Prepare audit log
    audit_log = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'database': db,
        'user': username,
        'operation': 'Fix Posted Invoices Wrong Status',
        'orders_processed': []
    }
    
    print("\n" + "=" * 100)
    print("ORDERS TO FIX - POSTED INVOICES WITH WRONG STATUS")
    print("=" * 100)
    
    orders_to_fix = []
    
    for order in orders:
        # Get invoice details
        if order['invoice_ids']:
            invoices = models.execute_kw(
                db, uid, password,
                'account.move', 'read',
                [order['invoice_ids'], ['name', 'state', 'move_type', 'amount_total']]
            )
            
            # Check if has posted invoices
            posted_invoices = [inv for inv in invoices if inv['state'] == 'posted' and inv['move_type'] == 'out_invoice']
            draft_invoices = [inv for inv in invoices if inv['state'] == 'draft']
            
            # Calculate total invoiced amount
            total_invoiced = sum(inv['amount_total'] for inv in posted_invoices)
            
            if posted_invoices and order['invoice_status'] != 'invoiced':
                orders_to_fix.append(order)
                
                print(f"\n{len(orders_to_fix)}. Order: {order['name']}")
                print(f"   Current Status: {order['invoice_status']} (WRONG)")
                print(f"   Order Amount: {order['amount_total']:.2f} AED")
                print(f"   Invoiced Amount: {total_invoiced:.2f} AED")
                print(f"   Posted Invoices: {len(posted_invoices)}")
                for inv in posted_invoices:
                    print(f"   - {inv['name']} ({inv['state']}) - {inv['amount_total']:.2f} AED")
                if draft_invoices:
                    print(f"   Draft Invoices: {len(draft_invoices)}")
                print(f"   → Should be: invoiced")
                
                # Add to audit log
                audit_log['orders_processed'].append({
                    'order_id': order['id'],
                    'order_name': order['name'],
                    'current_status': order['invoice_status'],
                    'new_status': 'invoiced',
                    'order_amount': order['amount_total'],
                    'invoiced_amount': total_invoiced,
                    'reason': f'Has {len(posted_invoices)} posted invoice(s)',
                    'posted_invoices': [{'name': inv['name'], 'amount': inv['amount_total']} for inv in posted_invoices]
                })
    
    if not orders_to_fix:
        print("\nNo orders found with this specific issue!")
        return
    
    print(f"\n" + "=" * 100)
    print(f"SUMMARY: Found {len(orders_to_fix)} orders to fix")
    print("=" * 100)
    
    # Ask for confirmation
    print("\nThese orders will be updated to 'invoiced' status")
    response = input("\nProceed with update? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Update cancelled by user")
        return
    
    # Update orders
    print("\nUpdating orders...")
    updated_count = 0
    failed_count = 0
    
    for order in orders_to_fix:
        try:
            result = models.execute_kw(
                db, uid, password,
                'sale.order', 'write',
                [[order['id']], {'invoice_status': 'invoiced'}]
            )
            
            if result:
                updated_count += 1
                print(f"✓ Updated {order['name']}: {order['invoice_status']} → invoiced")
                
                # Update audit log
                for log_entry in audit_log['orders_processed']:
                    if log_entry['order_id'] == order['id']:
                        log_entry['update_result'] = 'success'
            else:
                failed_count += 1
                print(f"✗ Failed to update {order['name']}")
                for log_entry in audit_log['orders_processed']:
                    if log_entry['order_id'] == order['id']:
                        log_entry['update_result'] = 'failed'
        except Exception as e:
            failed_count += 1
            print(f"✗ Error updating {order['name']}: {str(e)}")
            for log_entry in audit_log['orders_processed']:
                if log_entry['order_id'] == order['id']:
                    log_entry['update_result'] = f'error: {str(e)}'
    
    # Save audit log
    log_filename = f"fix_posted_status_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_filename, 'w') as f:
        json.dump(audit_log, f, indent=2)
    
    print("\n" + "=" * 100)
    print("UPDATE COMPLETE")
    print("=" * 100)
    print(f"Updated: {updated_count}")
    print(f"Failed: {failed_count}")
    print(f"Audit log saved: {log_filename}")
    
    # Verify updates
    print("\nVerifying updates...")
    updated_orders = models.execute_kw(
        db, uid, password,
        'sale.order', 'read',
        [[order['id'] for order in orders_to_fix], ['name', 'invoice_status']]
    )
    
    print("\nFinal Status:")
    for order in updated_orders:
        status_icon = "✓" if order['invoice_status'] == 'invoiced' else "✗"
        print(f"{status_icon} {order['name']}: {order['invoice_status']}")

if __name__ == '__main__':
    main()
