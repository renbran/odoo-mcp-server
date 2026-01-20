#!/usr/bin/env python3
"""
Verify module installation in Odoo database
"""

import xmlrpc.client as xmlrpc
import time

print("\n" + "="*80)
print("VERIFYING MODULE INSTALLATION IN ODOO")
print("="*80)

# Wait a moment for Odoo to stabilize
print("\nWaiting 15 seconds for Odoo to fully stabilize...")
time.sleep(15)

# Connect to Odoo
url = 'https://erposus.com'
db = 'osusproperties'
username = 'salescompliance@osusproperties.com'
password = '8586583'

try:
    print("\nConnecting to Odoo...")
    common = xmlrpc.ServerProxy(f'{url}/xmlrpc/2/common')
    models = xmlrpc.ServerProxy(f'{url}/xmlrpc/2/object')
    
    uid = common.authenticate(db, username, password, {})
    print(f"✓ Connected (UID: {uid})")
    
    # Search for the module
    print("\nSearching for invoice_status_tags module...")
    modules = models.execute_kw(
        db, uid, password,
        'ir.module.module', 'search',
        [['name', '=', 'invoice_status_tags']]
    )
    
    if modules:
        print(f"✓ Module found (ID: {modules[0]})")
        
        # Read module details
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [modules[0], ['name', 'state', 'installed_version', 'latest_version']]
        )
        
        module = module_data[0]
        print(f"\nModule Details:")
        print(f"  Name: {module['name']}")
        print(f"  State: {module['state']}")
        print(f"  Installed Version: {module.get('installed_version', 'N/A')}")
        print(f"  Latest Version: {module.get('latest_version', 'N/A')}")
        
        # Check installation status
        print(f"\n{'='*80}")
        if module['state'] == 'installed':
            print("✓ SUCCESS: Module is installed!")
            print(f"{'='*80}")
            
            # List new fields added
            print("\nNew fields available on sale.order:")
            try:
                fields = models.execute_kw(
                    db, uid, password,
                    'sale.order', 'fields_get',
                    [['invoicing_percentage', 'invoice_type_tag', 'needs_invoice_attention']]
                )
                
                for field_name, field_info in fields.items():
                    print(f"  - {field_name}: {field_info.get('string', 'N/A')}")
                
            except Exception as e:
                print(f"  (Could not list fields: {str(e)[:100]})")
        else:
            print(f"⚠ Module state: {module['state']}")
            print(f"{'='*80}")
            
            if module['state'] == 'to install':
                print("\n⚠ Module is staged but not yet installed")
                print("Try one of the following:")
                print("  1. Restart Odoo: sudo systemctl restart odoo")
                print("  2. Click 'Install' in Apps menu")
                print("  3. Run: python3 odoo-bin -i invoice_status_tags -d osusproperties --no-http --stop-after-init")
    else:
        print("✗ Module not found in database")
        print("\nModule may need to be re-deployed. Try:")
        print("  1. Upload module files again")
        print("  2. Run: python3 install_module_complete.py")
    
    print("\n" + "="*80 + "\n")
    
except Exception as e:
    print(f"\n✗ Error: {str(e)[:200]}")
    print("\nTroubleshooting:")
    print("  1. Check if Odoo is running: systemctl status odoo")
    print("  2. Check Odoo logs: tail -50 /var/odoo/osusproperties/logs/odoo.log")
    print("  3. Try restarting Odoo: sudo systemctl restart odoo")
