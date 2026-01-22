#!/usr/bin/env python3
"""
Fuzzy Matching Script for Unlinked Invoices
============================================
Uses fuzzy string matching (90% threshold) to match invoices to sale orders
based on:
- Project name + Unit name
- Buyer name
- Booking date + Buyer name
"""
import sys
sys.path.insert(0, '/var/odoo/osusproperties/src')

import odoo
from odoo import api, SUPERUSER_ID
from odoo.tools import config
from thefuzz import fuzz
from collections import defaultdict

# Configuration
FUZZY_THRESHOLD = 90  # 90% match threshold

config.parse_config(['--config=/var/odoo/osusproperties/odoo.conf'])
db_name = 'osusproperties'
registry = odoo.modules.registry.Registry(db_name)


def normalize_string(s):
    """Normalize string for comparison - lowercase, strip, remove extra spaces"""
    if not s:
        return ''
    return ' '.join(str(s).lower().strip().split())


def fuzzy_match_score(s1, s2):
    """Calculate fuzzy match score between two strings"""
    if not s1 or not s2:
        return 0
    s1_norm = normalize_string(s1)
    s2_norm = normalize_string(s2)
    if not s1_norm or not s2_norm:
        return 0
    # Use token_sort_ratio for better matching of reordered words
    return fuzz.token_sort_ratio(s1_norm, s2_norm)


def get_best_match(invoice_value, order_values, threshold=FUZZY_THRESHOLD):
    """
    Find best fuzzy match for invoice value among order values.
    Returns (order_id, score) or (None, 0) if no match above threshold.
    """
    best_match = None
    best_score = 0

    for order_id, order_value in order_values:
        score = fuzzy_match_score(invoice_value, order_value)
        if score >= threshold and score > best_score:
            best_score = score
            best_match = order_id

    return best_match, best_score


with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    AccountMove = env['account.move']
    SaleOrder = env['sale.order']

    print('=' * 60)
    print('FUZZY MATCHING INVOICES TO SALE ORDERS')
    print(f'Threshold: {FUZZY_THRESHOLD}%')
    print('=' * 60)

    # Get all unmatched invoices (not linked via lines and not already matched)
    all_posted = AccountMove.search([
        ('state', '=', 'posted'),
        ('move_type', 'in', ['out_invoice', 'out_refund']),
    ])

    unmatched = all_posted.filtered(
        lambda m: not m.line_ids.sale_line_ids.order_id and not m.matched_sale_order_id
    )

    print(f'\nUnmatched invoices to process: {len(unmatched)}')

    # Get all sale orders for matching
    orders = SaleOrder.search([('state', 'in', ['draft', 'sale', 'done'])])
    print(f'Sale orders available for matching: {len(orders)}')

    # Build lookup structures for orders
    print('\nBuilding order lookup tables...')

    # Project + Unit combinations
    order_project_unit = []  # [(order_id, "project_name unit_name")]
    for o in orders:
        if o.project_id and o.unit_id:
            combo = f"{o.project_id.name or ''} {o.unit_id.name or ''}".strip()
            if combo:
                order_project_unit.append((o.id, combo))

    # Buyer names
    order_buyers = []  # [(order_id, buyer_name)]
    for o in orders:
        if o.buyer_id:
            order_buyers.append((o.id, o.buyer_id.name or ''))

    # Booking date + buyer combinations
    order_date_buyer = defaultdict(list)  # {booking_date: [(order_id, buyer_name)]}
    for o in orders:
        if o.booking_date and o.buyer_id:
            order_date_buyer[o.booking_date].append((o.id, o.buyer_id.name or ''))

    print(f'  - Project+Unit combinations: {len(order_project_unit)}')
    print(f'  - Buyer names: {len(order_buyers)}')
    print(f'  - Date+Buyer combinations: {sum(len(v) for v in order_date_buyer.values())}')

    # Process unmatched invoices
    print('\nProcessing unmatched invoices...')

    matched_count = 0
    match_details = []
    match_by_method = defaultdict(int)

    for idx, inv in enumerate(unmatched):
        if idx % 20 == 0:
            print(f'  Processing {idx + 1}/{len(unmatched)}...')

        matched_order_id = None
        match_method = None
        match_score = 0

        # Get invoice deal info
        inv_project = getattr(inv, 'project_id', None)
        inv_unit = getattr(inv, 'unit_id', None)
        inv_buyer = getattr(inv, 'buyer_id', None)
        inv_booking_date = getattr(inv, 'booking_date', None)

        # Method 1: Fuzzy match on Project + Unit
        if inv_project and inv_unit and not matched_order_id:
            inv_combo = f"{inv_project.name or ''} {inv_unit.name or ''}".strip()
            if inv_combo:
                order_id, score = get_best_match(inv_combo, order_project_unit)
                if order_id:
                    matched_order_id = order_id
                    match_method = f'project+unit (fuzzy {score}%)'
                    match_score = score

        # Method 2: Fuzzy match on Buyer name (only if project+unit didn't match)
        if inv_buyer and not matched_order_id:
            inv_buyer_name = inv_buyer.name or ''
            if inv_buyer_name:
                order_id, score = get_best_match(inv_buyer_name, order_buyers)
                if order_id:
                    matched_order_id = order_id
                    match_method = f'buyer (fuzzy {score}%)'
                    match_score = score

        # Method 3: Exact date + Fuzzy buyer match
        if inv_booking_date and inv_buyer and not matched_order_id:
            if inv_booking_date in order_date_buyer:
                inv_buyer_name = inv_buyer.name or ''
                candidates = order_date_buyer[inv_booking_date]
                order_id, score = get_best_match(inv_buyer_name, candidates)
                if order_id:
                    matched_order_id = order_id
                    match_method = f'date+buyer (fuzzy {score}%)'
                    match_score = score

        # Update invoice if matched
        if matched_order_id:
            inv.write({
                'matched_sale_order_id': matched_order_id,
                'is_manually_matched': True,  # Mark as fuzzy matched
            })
            matched_count += 1

            matched_order = SaleOrder.browse(matched_order_id)
            match_details.append({
                'invoice': inv.name,
                'order': matched_order.name,
                'method': match_method,
                'score': match_score,
            })

            # Track by method type
            method_type = match_method.split(' ')[0]
            match_by_method[method_type] += 1

    cr.commit()

    # Results
    print('\n' + '=' * 60)
    print('FUZZY MATCHING RESULTS')
    print('=' * 60)
    print(f'\nTotal processed: {len(unmatched)}')
    print(f'Successfully matched: {matched_count}')
    print(f'Still unmatched: {len(unmatched) - matched_count}')

    print(f'\nMatches by method:')
    for method, count in sorted(match_by_method.items()):
        print(f'  - {method}: {count}')

    print(f'\nSample matches (first 20):')
    print('-' * 80)
    for detail in match_details[:20]:
        print(f"{detail['invoice']:20} -> {detail['order']:15} via {detail['method']}")

    # Final verification
    print('\n' + '=' * 60)
    print('FINAL STATUS')
    print('=' * 60)

    still_unmatched = all_posted.filtered(
        lambda m: not m.line_ids.sale_line_ids.order_id and not m.matched_sale_order_id
    )

    total_linked = all_posted.filtered(lambda m: m.effective_sale_order_id)

    print(f'Total posted invoices: {len(all_posted)}')
    print(f'Invoices with effective link: {len(total_linked)}')
    print(f'Remaining unmatched: {len(still_unmatched)}')

    # Show some unmatched invoices for analysis
    print(f'\nSample unmatched invoices (first 10):')
    print('-' * 80)
    for inv in still_unmatched[:10]:
        inv_project = getattr(inv, 'project_id', None)
        inv_unit = getattr(inv, 'unit_id', None)
        inv_buyer = getattr(inv, 'buyer_id', None)
        print(f"{inv.name}: Project={inv_project.name if inv_project else 'N/A'}, "
              f"Unit={inv_unit.name if inv_unit else 'N/A'}, "
              f"Buyer={inv_buyer.name if inv_buyer else 'N/A'}")
