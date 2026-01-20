#!/usr/bin/env python3
"""
Fix Cancelled Invoices Status
------------------------------
Updates 12 orders that have only cancelled invoices but show "to invoice"
These should be "no" status (no valid invoices).

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
    print("FIX: Cancelled Invoices with Wrong Status")
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
    
    # List of 12 orders with cancelled invoices
    order_names = [
        'S01953',
        'SS/10/214',
        'ES/10/7664',
        'PS/10/4517',
        'PS/10/4516',
        '6879',
        '197',
        '6843',
        '6890',
        '7012',
        '6856',
        '6855'
    ]
    
    print(f"\nSearching for {len(order_names)} orders with cancelled invoice issues...")
    
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
        [order_ids, ['name', 'invoice_status', 'invoice_ids']]
    )
    
    # Prepare audit log
    audit_log = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'database': db,
        'user': username,
        'operation': 'Fix Cancelled Invoices Status',
        'orders_processed': []
    }
    
    print("\n" + "=" * 100)
    print("ORDERS TO FIX - CANCELLED INVOICES SHOWING AS 'TO INVOICE'")
    print("=" * 100)
    
    orders_to_fix = []
    
    for order in orders:
        # Get invoice details
        if order['invoice_ids']:
            invoices = models.execute_kw(
                db, uid, password,
                'account.move', 'read',
                [order['invoice_ids'], ['name', 'state', 'move_type']]
            )
            
            # Check if has only cancelled invoices
            cancelled_invoices = [inv for inv in invoices if inv['state'] == 'cancel']
            posted_invoices = [inv for inv in invoices if inv['state'] == 'posted']
            draft_invoices = [inv for inv in invoices if inv['state'] == 'draft']
            
            if cancelled_invoices and not posted_invoices and not draft_invoices and order['invoice_status'] != 'no':
                orders_to_fix.append(order)
                
                print(f"\n{len(orders_to_fix)}. Order: {order['name']}")
                print(f"   Current Status: {order['invoice_status']} (WRONG)")
                print(f"   Cancelled Invoices: {len(cancelled_invoices)}")
                for inv in cancelled_invoices:
                    print(f"   - {inv['name']} ({inv['state']})")
                print(f"   → Should be: no")
                
                # Add to audit log
                audit_log['orders_processed'].append({
                    'order_id': order['id'],
                    'order_name': order['name'],
                    'current_status': order['invoice_status'],
                    'new_status': 'no',
                    'reason': 'Has only cancelled invoices',
                    'cancelled_invoices': [{'name': inv['name'], 'state': inv['state']} for inv in cancelled_invoices]
                })
    
    if not orders_to_fix:
        print("\nNo orders found with this specific issue!")
        return
    
    print(f"\n" + "=" * 100)
    print(f"SUMMARY: Found {len(orders_to_fix)} orders to fix")
    print("=" * 100)
    
    # Ask for confirmation
    print("\nThese orders will be updated to 'no' status (no valid invoices)")
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
                [[order['id']], {'invoice_status': 'no'}]
            )
            
            if result:
                updated_count += 1
                print(f"✓ Updated {order['name']}: {order['invoice_status']} → no")
                
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
    log_filename = f"fix_cancelled_status_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        status_icon = "✓" if order['invoice_status'] == 'no' else "✗"
        print(f"{status_icon} {order['name']}: {order['invoice_status']}")

if __name__ == '__main__':
    main()
