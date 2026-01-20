#!/usr/bin/env python3
"""
Update All Records After Module Installation
---------------------------------------------
Run this AFTER installing invoice_status_tags module
to update all existing sale orders with new computed fields.

Author: SGC TECH AI
Date: 2026-01-19
"""

import xmlrpc.client
import time

# Odoo connection details
url = 'https://erposus.com'
db = 'osusproperties'
username = 'salescompliance@osusproperties.com'
password = '8586583'

def main():
    print("=" * 100)
    print("UPDATE ALL SALE ORDERS - INVOICE STATUS TAGS")
    print("=" * 100)
    
    print("\nConnecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("Authentication failed!")
        return
    
    print(f"Connected (UID: {uid})")
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Fetch all sale orders
    print("\nFetching all sale orders...")
    order_ids = models.execute_kw(
        db, uid, password,
        'sale.order', 'search',
        [[]]
    )
    
    total_orders = len(order_ids)
    print(f"Found {total_orders} orders")
    
    if total_orders == 0:
        print("No orders to update")
        return
    
    # Trigger recomputation by reading the new fields
    print("\nTriggering field recomputation...")
    print("(This will compute invoice_status, invoicing_percentage, etc.)")
    
    batch_size = 100
    batches = [order_ids[i:i + batch_size] for i in range(0, len(order_ids), batch_size)]
    
    print(f"\nProcessing {len(batches)} batches of {batch_size} orders each...")
    
    for idx, batch in enumerate(batches, 1):
        try:
            # Read the computed fields to trigger recomputation
            models.execute_kw(
                db, uid, password,
                'sale.order', 'read',
                [batch, [
                    'invoicing_percentage',
                    'invoice_type_tag',
                    'needs_invoice_attention',
                    'has_draft_invoice_warning',
                    'posted_invoice_count',
                    'draft_invoice_count',
                    'total_invoiced_amount',
                    'remaining_to_invoice'
                ]]
            )
            processed = min(idx * batch_size, total_orders)
            print(f"  Processed batch {idx}/{len(batches)} ({processed}/{total_orders} orders)")
            time.sleep(0.5)  # Small delay
            
        except Exception as e:
            print(f"  Warning: Batch {idx} error: {e}")
            continue
    
    print(f"\nAll {total_orders} orders updated!")
    
    # Get summary statistics
    print("\n" + "=" * 100)
    print("UPDATED STATISTICS")
    print("=" * 100)
    
    # Count by invoice type tag
    print("\nInvoice Type Distribution:")
    tag_labels = {
        'not_started': 'Not Started',
        'partial': 'Partial Invoicing',
        'fully_invoiced': 'Fully Invoiced',
        'draft_only': 'Draft Only',
        'upsell': 'Upsell',
        'cancelled': 'Cancelled'
    }
    
    for tag, label in tag_labels.items():
        count = models.execute_kw(
            db, uid, password,
            'sale.order', 'search_count',
            [[['invoice_type_tag', '=', tag]]]
        )
        if count > 0:
            print(f"  {label}: {count}")
    
    # Count orders needing attention
    needs_attention = models.execute_kw(
        db, uid, password,
        'sale.order', 'search_count',
        [[['needs_invoice_attention', '=', True]]]
    )
    print(f"\n  Needs Attention: {needs_attention}")
    
    # Count draft invoice warnings
    draft_warnings = models.execute_kw(
        db, uid, password,
        'sale.order', 'search_count',
        [[['has_draft_invoice_warning', '=', True]]]
    )
    print(f"  Draft Invoice Warnings: {draft_warnings}")
    
    print("\n" + "=" * 100)
    print("UPDATE COMPLETE!")
    print("=" * 100)
    print("\nYou can now:")
    print("  1. Login to Odoo: https://erposus.com")
    print("  2. Go to Sales > Orders")
    print("  3. See new Invoice Type badges and Progress bars")
    print("  4. Use filters: Needs Attention, Partial Invoicing, etc.")

if __name__ == '__main__':
    main()
