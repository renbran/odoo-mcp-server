#!/usr/bin/env python3
"""
Alternative: Install via Odoo Web Interface
-------------------------------------------
This script provides step-by-step instructions for manual installation
via Odoo's web interface, which works with CloudPepper.

Author: SGC TECH AI
Date: 2026-01-19
"""

import webbrowser
from pathlib import Path
import json

print("=" * 100)
print("MANUAL INSTALLATION GUIDE - INVOICE STATUS TAGS MODULE")
print("=" * 100)

# Module details
module_path = Path(__file__).parent / 'invoice_status_tags'
zip_path = Path(__file__).parent / 'invoice_status_tags.zip'

print(f"\n✓ Module ZIP created: {zip_path}")
print(f"  Size: {zip_path.stat().st_size / 1024:.2f} KB")

print("\n" + "=" * 100)
print("INSTALLATION STEPS")
print("=" * 100)

print("\n📋 METHOD 1: Via Odoo Apps Menu (Recommended)")
print("-" * 100)
print("""
1. Login to Odoo:
   URL: https://erposus.com
   User: salescompliance@osusproperties.com
   
2. Enable Developer Mode:
   - Click your username (top right)
   - Settings → Activate the developer mode
   - Or add ?debug=1 to URL: https://erposus.com/web?debug=1

3. Go to Apps:
   - Click "Apps" in main menu
   
4. Upload Module:
   - Remove any search filters (click X on search bar)
   - Click "Upload" button (top right, may need to scroll)
   - Select file: invoice_status_tags.zip
   - Click "Upload"
   
5. Install Module:
   - Search for "Invoice Status Tags"
   - Click "Install" button
   - Wait for installation to complete
   
6. Refresh the page
""")

print("\n📋 METHOD 2: Via CloudPepper Control Panel")
print("-" * 100)
print("""
1. Login to CloudPepper control panel

2. Access File Manager:
   - Navigate to your Odoo installation directory
   - Usually: /opt/odoo/custom/addons/ or /opt/odoo/addons/

3. Upload Module:
   - Create folder: invoice_status_tags
   - Upload all files from the module folder, maintaining structure:
     ✓ __init__.py
     ✓ __manifest__.py
     ✓ models/__init__.py
     ✓ models/sale_order.py
     ✓ views/sale_order_views.xml

4. Set Permissions:
   - Set folder permissions: 755
   - Set file permissions: 644

5. Restart Odoo:
   - Use CloudPepper's restart button
   - Or via SSH: sudo systemctl restart odoo

6. Update Apps List:
   - Login to Odoo
   - Enable developer mode
   - Apps → Update Apps List

7. Install Module:
   - Search "Invoice Status Tags"
   - Click Install
""")

print("\n📋 METHOD 3: Contact CloudPepper Support")
print("-" * 100)
print("""
Send this to CloudPepper support:

Subject: Please Install Custom Module - invoice_status_tags

Dear CloudPepper Support,

Please install the attached custom module on our Odoo instance:

Database: osusproperties
Module: invoice_status_tags.zip (attached)

Installation Steps:
1. Extract to custom addons directory
2. Update apps list
3. Install the module

The module adds invoice status tracking features to sales orders.

Thank you!
""")

print("\n" + "=" * 100)
print("WHAT TO EXPECT AFTER INSTALLATION")
print("=" * 100)

print("""
Once installed, you'll see:

✨ In Sales Order List View:
   - New column: "Invoice Type" with colored badges
   - New column: "Invoicing Progress" with progress bars
   - New column: "Needs Attention" toggle

✨ In Sales Order Form View:
   - Red ribbon "DRAFT INVOICE WARNING" (if applicable)
   - Yellow ribbon "NEEDS ATTENTION" (if applicable)
   - Blue ribbon "UPSELL" (if applicable)
   - New section "Invoice Progress" with:
     * Invoice Type badge
     * Progress bar
     * Invoice breakdown (X Posted | Y Draft | Z Cancelled)
   - Amount details:
     * Total Invoiced (Posted)
     * Remaining to Invoice
     * Upsell Amount

✨ New Filters:
   - Needs Attention
   - Has Draft Invoices
   - Partial Invoicing
   - Upsell Orders
   - Draft Only

✨ New Menu Items (under Sales → Orders):
   - Needs Attention
   - Partial Invoicing
""")

print("\n" + "=" * 100)
print("AFTER INSTALLATION - UPDATE ALL RECORDS")
print("=" * 100)

print("""
Run this Python script to update all existing sales orders:
""")

print("\nPython command:")
print("  python update_all_records_after_install.py")

# Create the update script
update_script = """#!/usr/bin/env python3
import xmlrpc.client

url = 'https://erposus.com'
db = 'osusproperties'
username = 'salescompliance@osusproperties.com'
password = '8586583'

print("Connecting to Odoo...")
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("Authentication failed!")
    exit(1)

print(f"Connected (UID: {uid})")
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("Fetching all sale orders...")
order_ids = models.execute_kw(db, uid, password, 'sale.order', 'search', [[]])
print(f"Found {len(order_ids)} orders")

print("Triggering recomputation...")
batch_size = 100
for i in range(0, len(order_ids), batch_size):
    batch = order_ids[i:i + batch_size]
    models.execute_kw(db, uid, password, 'sale.order', 'read',
        [batch, ['invoicing_percentage', 'invoice_type_tag']])
    print(f"  Processed {min(i + batch_size, len(order_ids))}/{len(order_ids)}")

print("✓ All records updated!")
"""

update_script_path = Path(__file__).parent / 'update_all_records_after_install.py'
with open(update_script_path, 'w') as f:
    f.write(update_script)

print(f"\n✓ Update script created: {update_script_path}")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

summary = {
    'module_name': 'invoice_status_tags',
    'version': '17.0.1.0.0',
    'zip_file': str(zip_path),
    'module_folder': str(module_path),
    'installation_methods': [
        'Via Odoo Apps Upload (Recommended)',
        'Via CloudPepper File Manager',
        'Via CloudPepper Support'
    ],
    'post_installation': 'Run update_all_records_after_install.py',
    'documentation': str(module_path / 'README.md')
}

print(json.dumps(summary, indent=2))

print("\n✅ Ready for Installation!")
print(f"   Module ZIP: {zip_path}")
print(f"   Choose installation method above")
print(f"   After install, run: python update_all_records_after_install.py")

# Optionally open browser
print("\n" + "=" * 100)
response = input("Open Odoo login page in browser? (y/n): ").strip().lower()
if response == 'y':
    webbrowser.open('https://erposus.com/web/login')
    print("✓ Browser opened")
