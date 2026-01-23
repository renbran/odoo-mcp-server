#!/usr/bin/env python3
"""
OSUS Properties - Contact Duplicate Cleanup Script
Automatically fixes the 4 critical duplicate issues identified
"""

import xmlrpc.client
import json
from datetime import datetime

# Server configuration
PROD_URL = "http://localhost:8070"
PROD_DB = "osusproperties"
PROD_USER = "salescompliance@osusproperties.com"
PROD_PASS = "8586583"

def cleanup_duplicates(dry_run=True):
    """
    Clean up identified duplicate contacts
    
    Args:
        dry_run: If True, only preview changes without applying
    """
    print("=" * 80)
    print("OSUS PROPERTIES - CONTACT DUPLICATE CLEANUP")
    print("=" * 80)
    print(f"Mode: {'DRY RUN (Preview Only)' if dry_run else 'LIVE EXECUTION'}")
    print()
    
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f"{PROD_URL}/xmlrpc/2/common")
    uid = common.authenticate(PROD_DB, PROD_USER, PROD_PASS, {})
    
    if not uid:
        print("❌ Authentication failed!")
        return
    
    print(f"✓ Connected to {PROD_DB} (UID: {uid})")
    print()
    
    models = xmlrpc.client.ServerProxy(f"{PROD_URL}/xmlrpc/2/object")
    
    cleanup_actions = []
    
    # =========================================================================
    # ACTION 1: Delete TESTRENBRAN (ID: 34567) - Test account duplicate
    # =========================================================================
    print("🗑️  ACTION 1: Delete Test Account - TESTRENBRAN")
    try:
        test_account = models.execute_kw(
            PROD_DB, uid, PROD_PASS,
            'res.partner', 'read',
            [[34567], ['name', 'email', 'active']]
        )
        
        if test_account:
            account = test_account[0]
            print(f"   Found: {account.get('name')} (ID: {account['id']})")
            print(f"   Email: {account.get('email', 'N/A')}")
            print(f"   Status: {'Active' if account.get('active') else 'Inactive'}")
            
            if not dry_run:
                models.execute_kw(
                    PROD_DB, uid, PROD_PASS,
                    'res.partner', 'unlink',
                    [[34567]]
                )
                print("   ✅ DELETED")
                cleanup_actions.append({
                    'action': 'delete',
                    'id': 34567,
                    'name': account.get('name'),
                    'status': 'success'
                })
            else:
                print("   🔍 WILL BE DELETED (dry run)")
                cleanup_actions.append({
                    'action': 'delete',
                    'id': 34567,
                    'name': account.get('name'),
                    'status': 'pending'
                })
        else:
            print("   ℹ️  Account not found (may have been deleted already)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        cleanup_actions.append({
            'action': 'delete',
            'id': 34567,
            'status': 'error',
            'error': str(e)
        })
    
    print()
    
    # =========================================================================
    # ACTION 2: Delete AHMED GABER (COPY) (ID: 34539) - Copy duplicate
    # =========================================================================
    print("🗑️  ACTION 2: Delete Copy Account - AHMED GABER (COPY)")
    try:
        copy_account = models.execute_kw(
            PROD_DB, uid, PROD_PASS,
            'res.partner', 'read',
            [[34539], ['name', 'email', 'mobile', 'active']]
        )
        
        if copy_account:
            account = copy_account[0]
            print(f"   Found: {account.get('name')} (ID: {account['id']})")
            print(f"   Email: {account.get('email', 'N/A')}")
            print(f"   Mobile: {account.get('mobile', 'N/A')}")
            
            if not dry_run:
                models.execute_kw(
                    PROD_DB, uid, PROD_PASS,
                    'res.partner', 'unlink',
                    [[34539]]
                )
                print("   ✅ DELETED")
                cleanup_actions.append({
                    'action': 'delete',
                    'id': 34539,
                    'name': account.get('name'),
                    'status': 'success'
                })
            else:
                print("   🔍 WILL BE DELETED (dry run)")
                cleanup_actions.append({
                    'action': 'delete',
                    'id': 34539,
                    'name': account.get('name'),
                    'status': 'pending'
                })
        else:
            print("   ℹ️  Account not found (may have been deleted already)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        cleanup_actions.append({
            'action': 'delete',
            'id': 34539,
            'status': 'error',
            'error': str(e)
        })
    
    print()
    
    # =========================================================================
    # ACTION 3: Update TRIPTI SHETDD email (ID: 20980)
    # =========================================================================
    print("⚠️  ACTION 3: Flag Incorrect Email - TRIPTI SHETDD")
    try:
        tripti = models.execute_kw(
            PROD_DB, uid, PROD_PASS,
            'res.partner', 'read',
            [[20980], ['name', 'email', 'phone', 'mobile']]
        )
        
        if tripti:
            account = tripti[0]
            print(f"   Found: {account.get('name')} (ID: {account['id']})")
            print(f"   Current Email: {account.get('email', 'N/A')}")
            print(f"   ⚠️  ISSUE: Email 'wsimon@lmduae.com' belongs to WESSAM SIMON")
            print(f"   📋 ACTION REQUIRED: Manual email update needed")
            print(f"      Contact TRIPTI SHETDD to get correct email address")
            print(f"      Then update via: Contacts → ID 20980 → Edit → Email")
            
            cleanup_actions.append({
                'action': 'manual_update_required',
                'id': 20980,
                'name': account.get('name'),
                'current_email': account.get('email'),
                'issue': 'Wrong email assigned',
                'status': 'needs_manual_action'
            })
        else:
            print("   ℹ️  Account not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # =========================================================================
    # ACTION 4: Flag RAHUL email conflict (IDs: 20976, 24482)
    # =========================================================================
    print("⚠️  ACTION 4: Review RAHUL Email Conflict")
    try:
        rahul_accounts = models.execute_kw(
            PROD_DB, uid, PROD_PASS,
            'res.partner', 'read',
            [[20976, 24482], ['name', 'email', 'supplier_rank', 'customer_rank']]
        )
        
        if rahul_accounts:
            print(f"   Found {len(rahul_accounts)} accounts sharing rahul@osusproperties.com:")
            for acc in rahul_accounts:
                role = []
                if acc.get('customer_rank', 0) > 0:
                    role.append('Customer')
                if acc.get('supplier_rank', 0) > 0:
                    role.append('Supplier')
                role_str = '/'.join(role) if role else 'No role'
                
                print(f"   • ID {acc['id']}: {acc.get('name')} | {role_str}")
            
            print()
            print(f"   📋 DECISION REQUIRED:")
            print(f"      Option A: If same person → Merge into ID 24482 (has Supplier role)")
            print(f"      Option B: If different people → Update ID 20976 to different email")
            
            cleanup_actions.append({
                'action': 'manual_review_required',
                'ids': [20976, 24482],
                'issue': 'Email conflict - same email on 2 accounts',
                'status': 'needs_decision'
            })
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 80)
    
    # Summary
    if dry_run:
        print("🔍 DRY RUN COMPLETE - No changes made")
        print()
        print("📋 SUMMARY:")
        print(f"   ✅ Will delete: 2 accounts (TESTRENBRAN, AHMED GABER COPY)")
        print(f"   ⚠️  Manual action needed: 2 items (TRIPTI email, RAHUL conflict)")
        print()
        print("💡 To apply deletions, run:")
        print("   python3 cleanup_contact_duplicates.py --live")
    else:
        print("✅ CLEANUP COMPLETE")
        print()
        print("📋 SUMMARY:")
        deleted = sum(1 for a in cleanup_actions if a.get('action') == 'delete' and a.get('status') == 'success')
        print(f"   ✅ Deleted: {deleted} accounts")
        print(f"   ⚠️  Manual action still needed: 2 items")
        print()
        print("📋 NEXT STEPS:")
        print("   1. Update TRIPTI SHETDD email (ID: 20980)")
        print("   2. Resolve RAHUL email conflict (IDs: 20976, 24482)")
    
    print("=" * 80)
    print()
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'dry_run' if dry_run else 'live',
        'actions': cleanup_actions,
        'summary': {
            'deleted': sum(1 for a in cleanup_actions if a.get('action') == 'delete' and a.get('status') == 'success'),
            'pending_delete': sum(1 for a in cleanup_actions if a.get('action') == 'delete' and a.get('status') == 'pending'),
            'manual_action_needed': sum(1 for a in cleanup_actions if 'manual' in a.get('action', ''))
        }
    }
    
    report_file = f"duplicate_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Report saved: {report_file}")
    print()
    
    return report

if __name__ == "__main__":
    import sys
    
    # Default to dry run for safety
    dry_run = True
    
    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        confirm = input("⚠️  This will DELETE 2 contact records. Type 'CLEANUP' to confirm: ")
        if confirm == 'CLEANUP':
            dry_run = False
        else:
            print("❌ Cleanup cancelled")
            sys.exit(1)
    
    cleanup_duplicates(dry_run=dry_run)
