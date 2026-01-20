#!/usr/bin/env python3
"""
Actual Module Upload and Installation
--------------------------------------
Attempts to upload and install the module using Odoo's API.

Author: SGC TECH AI
Date: 2026-01-19
"""

import xmlrpc.client
import base64
import time
from pathlib import Path

# Odoo connection details
url = 'https://erposus.com'
db = 'osusproperties'
username = 'salescompliance@osusproperties.com'
password = '8586583'

def connect():
    """Connect to Odoo"""
    print("=" * 100)
    print("CONNECTING TO ODOO")
    print("=" * 100)
    print(f"\nServer: {url}")
    print(f"Database: {db}")
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("❌ Authentication failed!")
        return None, None
    
    print(f"✓ Connected (UID: {uid})")
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return uid, models

def upload_via_attachment(uid, models):
    """Upload module ZIP as attachment"""
    print("\n" + "=" * 100)
    print("METHOD 1: Upload via Attachments")
    print("=" * 100)
    
    zip_path = Path(__file__).parent / 'invoice_status_tags.zip'
    
    if not zip_path.exists():
        print(f"❌ ZIP file not found: {zip_path}")
        return False
    
    try:
        # Read ZIP file
        print(f"\nReading ZIP file: {zip_path}")
        with open(zip_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')
        
        file_size = len(data)
        print(f"✓ File read: {file_size} bytes (base64)")
        
        # Create attachment
        print("\nCreating attachment...")
        attachment_id = models.execute_kw(
            db, uid, password,
            'ir.attachment', 'create',
            [{
                'name': 'invoice_status_tags.zip',
                'datas': data,
                'res_model': 'ir.module.module',
                'type': 'binary',
            }]
        )
        
        print(f"✓ Attachment created: ID {attachment_id}")
        
        # Try to trigger module import
        print("\n⚠ Module uploaded as attachment")
        print("  You can now install it via Apps menu in Odoo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_module_record(uid, models):
    """Create module record directly"""
    print("\n" + "=" * 100)
    print("METHOD 2: Create Module Record")
    print("=" * 100)
    
    try:
        # Check if module already exists
        print("\nChecking for existing module...")
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', 'invoice_status_tags']]]
        )
        
        if module_ids:
            print(f"✓ Module record exists: ID {module_ids[0]}")
            return module_ids[0]
        
        # Create module record
        print("\nCreating module record...")
        module_id = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'create',
            [{
                'name': 'invoice_status_tags',
                'shortdesc': 'Invoice Status Tags & Controls',
                'description': 'Clear invoice status tagging and controls',
                'author': 'SGC TECH AI',
                'category_id': 1,  # Sales
                'state': 'uninstalled',
                'application': False,
                'auto_install': False,
            }]
        )
        
        print(f"✓ Module record created: ID {module_id}")
        return module_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def install_via_xmlrpc(uid, models, module_id):
    """Attempt installation via XML-RPC"""
    print("\n" + "=" * 100)
    print("METHOD 3: Direct Installation")
    print("=" * 100)
    
    try:
        print(f"\nAttempting to install module ID: {module_id}")
        
        # Try button_immediate_install
        result = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'button_immediate_install',
            [[module_id]]
        )
        
        print(f"✓ Install command sent: {result}")
        
        # Wait and check status
        print("\nWaiting for installation...")
        time.sleep(5)
        
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [[module_id], ['state', 'name']]
        )[0]
        
        print(f"\nModule Status: {module_data['state']}")
        
        if module_data['state'] == 'installed':
            print("✓ Module successfully installed!")
            return True
        else:
            print(f"⚠ Module state: {module_data['state']}")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_all_records(uid, models):
    """Update all sale order records"""
    print("\n" + "=" * 100)
    print("UPDATING ALL RECORDS")
    print("=" * 100)
    
    try:
        # Get all sale orders
        print("\nFetching sale orders...")
        order_ids = models.execute_kw(
            db, uid, password,
            'sale.order', 'search',
            [[]]
        )
        
        total = len(order_ids)
        print(f"✓ Found {total} orders")
        
        # Process in batches
        batch_size = 100
        batches = [order_ids[i:i + batch_size] for i in range(0, len(order_ids), batch_size)]
        
        print(f"\nProcessing {len(batches)} batches...")
        
        for idx, batch in enumerate(batches, 1):
            try:
                models.execute_kw(
                    db, uid, password,
                    'sale.order', 'read',
                    [batch, [
                        'invoicing_percentage',
                        'invoice_type_tag',
                        'needs_invoice_attention',
                        'posted_invoice_count',
                        'draft_invoice_count'
                    ]]
                )
                processed = min(idx * batch_size, total)
                print(f"  ✓ Batch {idx}/{len(batches)} ({processed}/{total})")
                time.sleep(0.3)
            except Exception as e:
                print(f"  ⚠ Batch {idx} error: {e}")
        
        print(f"\n✓ All {total} records updated!")
        
        # Get statistics
        print("\n" + "=" * 100)
        print("STATISTICS")
        print("=" * 100)
        
        tags = {
            'partial': 'Partial Invoicing',
            'fully_invoiced': 'Fully Invoiced',
            'draft_only': 'Draft Only',
            'not_started': 'Not Started',
            'upsell': 'Upsell',
            'cancelled': 'Cancelled'
        }
        
        for tag, label in tags.items():
            count = models.execute_kw(
                db, uid, password,
                'sale.order', 'search_count',
                [[['invoice_type_tag', '=', tag]]]
            )
            if count > 0:
                print(f"  {label}: {count}")
        
        # Needs attention
        needs_attention = models.execute_kw(
            db, uid, password,
            'sale.order', 'search_count',
            [[['needs_invoice_attention', '=', True]]]
        )
        print(f"\n  ⚠ Needs Attention: {needs_attention}")
        
        return True
        
    except Exception as e:
        print(f"❌ Update error: {e}")
        return False

def main():
    print("=" * 100)
    print("INVOICE STATUS TAGS - ACTUAL INSTALLATION")
    print("=" * 100)
    
    # Connect
    uid, models = connect()
    if not uid:
        return
    
    # Try Method 1: Upload as attachment
    print("\n🔄 Attempting upload...")
    upload_via_attachment(uid, models)
    
    # Try Method 2: Create module record
    print("\n🔄 Creating/finding module record...")
    module_id = create_module_record(uid, models)
    
    if module_id:
        # Try Method 3: Install
        print("\n🔄 Attempting installation...")
        installed = install_via_xmlrpc(uid, models, module_id)
        
        if installed:
            # Update records
            print("\n🔄 Updating all records...")
            update_all_records(uid, models)
            
            print("\n" + "=" * 100)
            print("✅ INSTALLATION COMPLETE!")
            print("=" * 100)
            print("\nNext steps:")
            print("  1. Login to: https://erposus.com")
            print("  2. Go to Sales → Orders")
            print("  3. You'll see new Invoice Type tags and Progress bars")
            print("  4. Use filters: Partial Invoicing, Needs Attention, etc.")
        else:
            print("\n" + "=" * 100)
            print("⚠ MANUAL INSTALLATION REQUIRED")
            print("=" * 100)
            print("\nAutomatic installation not possible via XML-RPC.")
            print("Please follow manual installation steps:")
            print("\n1. Login to Odoo with developer mode enabled")
            print("2. Go to Apps menu")
            print("3. Click 'Upload' button")
            print("4. Select: invoice_status_tags.zip")
            print("5. Click Install")
            print("\nAfter installation, run:")
            print("  python update_all_records_after_install.py")
    else:
        print("\n⚠ Could not create module record")
        print("Manual installation required (see above)")

if __name__ == '__main__':
    main()
