#!/usr/bin/env python3
"""
CloudPepper Server Installation Script
---------------------------------------
Installs invoice_status_tags module to CloudPepper Odoo server
using the actual server paths.

Author: SGC TECH AI
Date: 2026-01-19
"""

import xmlrpc.client
import base64
import time
from pathlib import Path

# Server paths
SERVER_PATHS = {
    'source': '/var/odoo/osusproperties/src',
    'logs': '/var/odoo/osusproperties/logs',
    'config': '/var/odoo/osusproperties/odoo.conf',
    'python': '/var/odoo/osusproperties/venv/bin/python3',
    'extra_addons': '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/',
    'odoo_bin': '/var/odoo/osusproperties/src/odoo-bin',
}

# Odoo connection
url = 'https://erposus.com'
db = 'osusproperties'
username = 'salescompliance@osusproperties.com'
password = '8586583'

def print_upload_instructions():
    """Print file upload instructions"""
    print("=" * 100)
    print("STEP 1: UPLOAD MODULE FILES TO SERVER")
    print("=" * 100)
    
    module_path = Path(__file__).parent / 'invoice_status_tags'
    target_path = SERVER_PATHS['extra_addons'] + 'invoice_status_tags'
    
    print(f"\nLocal module: {module_path}")
    print(f"Server target: {target_path}")
    
    print("\n" + "=" * 100)
    print("OPTION A: Via SFTP/SCP (Recommended)")
    print("=" * 100)
    
    print("\n1. Upload entire folder via SFTP/SCP:")
    print(f"   scp -r {module_path} user@server:{SERVER_PATHS['extra_addons']}")
    
    print("\n2. Or use SFTP client (FileZilla, WinSCP):")
    print(f"   - Connect to CloudPepper server")
    print(f"   - Navigate to: {SERVER_PATHS['extra_addons']}")
    print(f"   - Upload folder: invoice_status_tags")
    
    print("\n" + "=" * 100)
    print("OPTION B: Via CloudPepper File Manager")
    print("=" * 100)
    
    print("\n1. Login to CloudPepper control panel")
    print("2. Go to File Manager")
    print(f"3. Navigate to: {SERVER_PATHS['extra_addons']}")
    print("4. Create folder: invoice_status_tags")
    print("5. Upload all module files maintaining structure:")
    print("   - __init__.py")
    print("   - __manifest__.py")
    print("   - models/__init__.py")
    print("   - models/sale_order.py")
    print("   - views/sale_order_views.xml")
    
    print("\n" + "=" * 100)
    print("OPTION C: Via ZIP Upload")
    print("=" * 100)
    
    zip_path = Path(__file__).parent / 'invoice_status_tags.zip'
    print(f"\n1. Upload {zip_path} to server /tmp/")
    print("2. SSH into server and run:")
    print(f"   cd {SERVER_PATHS['extra_addons']}")
    print(f"   unzip /tmp/invoice_status_tags.zip")
    print(f"   chown -R odoo:odoo invoice_status_tags")
    print(f"   chmod -R 755 invoice_status_tags")

def generate_ssh_commands():
    """Generate SSH commands for server-side installation"""
    print("\n" + "=" * 100)
    print("STEP 2: SERVER-SIDE INSTALLATION COMMANDS")
    print("=" * 100)
    
    commands = f"""
# Connect to CloudPepper server via SSH
ssh user@your-server

# Set proper ownership and permissions
cd {SERVER_PATHS['extra_addons']}
sudo chown -R odoo:odoo invoice_status_tags
sudo chmod -R 755 invoice_status_tags
sudo find invoice_status_tags -type f -exec chmod 644 {{}} \\;

# Update module list
cd /var/odoo/osusproperties
sudo -u odoo {SERVER_PATHS['python']} {SERVER_PATHS['odoo_bin']} \\
    -c {SERVER_PATHS['config']} \\
    --no-http \\
    --stop-after-init \\
    --update-list

# Install the module
sudo -u odoo {SERVER_PATHS['python']} {SERVER_PATHS['odoo_bin']} \\
    -c {SERVER_PATHS['config']} \\
    --no-http \\
    --stop-after-init \\
    -i invoice_status_tags \\
    -d {db}

# Restart Odoo service
sudo systemctl restart odoo
    """
    
    print("\nCopy and paste these commands in SSH terminal:")
    print(commands)
    
    # Save to file
    cmd_file = Path(__file__).parent / 'ssh_install_commands.sh'
    with open(cmd_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write("#!/bin/bash\n")
        f.write("# CloudPepper Module Installation Commands\n")
        f.write("# Run on server after uploading module files\n\n")
        f.write(commands)
    
    print(f"\nCommands saved to: {cmd_file}")

def connect_odoo():
    """Connect to Odoo via XML-RPC"""
    print("\n" + "=" * 100)
    print("STEP 3: VERIFYING ODOO CONNECTION")
    print("=" * 100)
    
    print(f"\nConnecting to {url}...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("Authentication failed!")
        return None, None
    
    print(f"Connected (UID: {uid})")
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return uid, models

def check_module_status(uid, models):
    """Check if module is installed"""
    print("\n" + "=" * 100)
    print("STEP 4: CHECKING MODULE STATUS")
    print("=" * 100)
    
    try:
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', 'invoice_status_tags']]]
        )
        
        if module_ids:
            module_data = models.execute_kw(
                db, uid, password,
                'ir.module.module', 'read',
                [module_ids, ['name', 'state', 'installed_version']]
            )[0]
            
            print(f"\nModule found: {module_data['name']}")
            print(f"  State: {module_data['state']}")
            print(f"  Version: {module_data.get('installed_version', 'N/A')}")
            
            return module_data['state']
        else:
            print("\nModule not found in database")
            print("  Files need to be uploaded to server first")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def update_all_records(uid, models):
    """Update all sale order records"""
    print("\n" + "=" * 100)
    print("STEP 5: UPDATING ALL SALE ORDER RECORDS")
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
        print(f"Found {total} orders")
        
        if total == 0:
            print("No orders to update")
            return True
        
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
                        'has_draft_invoice_warning',
                        'posted_invoice_count',
                        'draft_invoice_count',
                        'total_invoiced_amount',
                        'remaining_to_invoice'
                    ]]
                )
                processed = min(idx * batch_size, total)
                print(f"  Batch {idx}/{len(batches)} ({processed}/{total} orders)")
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  Warning: Batch {idx} error: {e}")
                continue
        
        print(f"\nAll {total} records updated!")
        
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
        print(f"\n  Needs Attention: {needs_attention}")
        
        # Draft warnings
        draft_warnings = models.execute_kw(
            db, uid, password,
            'sale.order', 'search_count',
            [[['has_draft_invoice_warning', '=', True]]]
        )
        print(f"  Draft Invoice Warnings: {draft_warnings}")
        
        return True
        
    except Exception as e:
        print(f"Update error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_installation_script():
    """Create a complete installation script"""
    print("\n" + "=" * 100)
    print("CREATING AUTOMATED INSTALLATION SCRIPT")
    print("=" * 100)
    
    script = f"""#!/bin/bash
# Automated Installation Script for invoice_status_tags
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

set -e  # Exit on error

echo "=================================="
echo "Invoice Status Tags Installation"
echo "=================================="

# Variables
MODULE_NAME="invoice_status_tags"
TARGET_PATH="{SERVER_PATHS['extra_addons']}$MODULE_NAME"
PYTHON="{SERVER_PATHS['python']}"
ODOO_BIN="{SERVER_PATHS['odoo_bin']}"
CONFIG="{SERVER_PATHS['config']}"
DB="{db}"

echo ""
echo "Step 1: Setting permissions..."
cd {SERVER_PATHS['extra_addons']}
sudo chown -R odoo:odoo $MODULE_NAME
sudo chmod -R 755 $MODULE_NAME
sudo find $MODULE_NAME -type f -exec chmod 644 {{}} \\;
echo "Permissions set"

echo ""
echo "Step 2: Updating module list..."
cd /var/odoo/osusproperties
sudo -u odoo $PYTHON $ODOO_BIN \\
    -c $CONFIG \\
    --no-http \\
    --stop-after-init \\
    --update-list
echo "Module list updated"

echo ""
echo "Step 3: Installing module..."
sudo -u odoo $PYTHON $ODOO_BIN \\
    -c $CONFIG \\
    --no-http \\
    --stop-after-init \\
    -i $MODULE_NAME \\
    -d $DB
echo "Module installed"

echo ""
echo "Step 4: Restarting Odoo service..."
sudo systemctl restart odoo
echo "Odoo restarted"

echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next: Run Python script to update all records"
echo "  python update_all_records_after_install.py"
"""
    
    script_file = Path(__file__).parent / 'install_on_server.sh'
    with open(script_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(script)
    
    print(f"Script created: {script_file}")
    print("\nTo use:")
    print("  1. Upload module files to server")
    print(f"  2. Upload {script_file} to server")
    print("  3. Run: bash install_on_server.sh")

def main():
    print("=" * 100)
    print("CLOUDPEPPER SERVER INSTALLATION - INVOICE STATUS TAGS")
    print("=" * 100)
    print(f"\nTarget Server: {url}")
    print(f"Database: {db}")
    print(f"Module Path: {SERVER_PATHS['extra_addons']}invoice_status_tags")
    
    # Generate instructions
    print_upload_instructions()
    generate_ssh_commands()
    create_installation_script()
    
    # Connect to Odoo
    uid, models = connect_odoo()
    if not uid:
        print("\n⚠ Could not connect to Odoo")
        return
    
    # Check module status
    state = check_module_status(uid, models)
    
    if state == 'installed':
        print("\n✓ Module is already installed!")
        print("\nUpdating records...")
        update_all_records(uid, models)
        
        print("\n" + "=" * 100)
        print("✅ COMPLETE!")
        print("=" * 100)
        print("\nModule installed and all records updated!")
        print("\nLogin to Odoo to see the new features:")
        print(f"  URL: {url}")
        print("  - Sales → Orders")
        print("  - See Invoice Type tags, Progress bars, Filters")
        
    elif state in ['to install', 'to upgrade']:
        print("\n⚠ Module is staged but not installed")
        print("\nRun the installation commands above to complete")
        
    else:
        print("\n" + "=" * 100)
        print("📋 INSTALLATION CHECKLIST")
        print("=" * 100)
        print("""
1. ☐ Upload module files to server
   Target: /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/invoice_status_tags
   
2. ☐ Run installation script on server
   bash install_on_server.sh
   
3. ☐ Update all records
   python update_all_records_after_install.py
   
4. ☐ Verify in Odoo
   Login and check Sales → Orders
        """)

if __name__ == '__main__':
    main()
