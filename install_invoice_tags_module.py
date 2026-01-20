#!/usr/bin/env python3
"""
Install Invoice Status Tags Module to Odoo
-------------------------------------------
Installs the custom invoice_status_tags module to osusproperties database.

Author: SGC TECH AI
Date: 2026-01-19
"""

import xmlrpc.client
import os
import zipfile
import base64
from pathlib import Path

# Odoo connection details
url = 'https://erposus.com'
db = 'osusproperties'
username = 'salescompliance@osusproperties.com'
password = '8586583'

def create_module_zip():
    """Create ZIP file of the module"""
    print("Creating module ZIP file...")
    module_path = Path(__file__).parent / 'invoice_status_tags'
    zip_path = Path(__file__).parent / 'invoice_status_tags.zip'
    
    if zip_path.exists():
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(module_path):
            # Skip __pycache__
            if '__pycache__' in root:
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, module_path.parent)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")
    
    print(f"✓ Module ZIP created: {zip_path}")
    return zip_path

def install_module():
    """Install module to Odoo via XML-RPC"""
    print("\n" + "=" * 100)
    print("INSTALLING INVOICE STATUS TAGS MODULE")
    print("=" * 100)
    
    # Connect to Odoo
    print("\nConnecting to Odoo...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("❌ Authentication failed!")
        return False
    
    print(f"✓ Connected (UID: {uid})")
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Check if module already exists
    print("\nChecking for existing module...")
    module_ids = models.execute_kw(
        db, uid, password,
        'ir.module.module', 'search',
        [[['name', '=', 'invoice_status_tags']]]
    )
    
    if module_ids:
        print("Module already exists. Upgrading...")
        
        # Upgrade module
        models.execute_kw(
            db, uid, password,
            'ir.module.module', 'button_immediate_upgrade',
            [module_ids]
        )
        print("✓ Module upgraded successfully!")
    else:
        print("Module not found. Manual installation required.")
        print("\n" + "=" * 100)
        print("MANUAL INSTALLATION STEPS")
        print("=" * 100)
        print("\n1. Copy module to Odoo addons directory:")
        print(f"   Source: {Path(__file__).parent / 'invoice_status_tags'}")
        print(f"   Destination: /path/to/odoo/addons/invoice_status_tags")
        print("\n2. Restart Odoo server:")
        print("   sudo systemctl restart odoo")
        print("\n3. Update Apps List:")
        print("   Apps → Update Apps List")
        print("\n4. Install Module:")
        print("   Apps → Search 'Invoice Status Tags' → Install")
        
        # Create ZIP for upload
        zip_path = create_module_zip()
        print(f"\n5. Alternative: Upload ZIP file")
        print(f"   File ready: {zip_path}")
        print(f"   Upload via: Apps → Upload Module")
    
    return True

def main():
    try:
        install_module()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
