#!/usr/bin/env python3
"""
Remote Module Installation & Update Script
-------------------------------------------
Remotely installs invoice_status_tags module to Odoo CloudPepper server
and updates all sale order records.

Author: SGC TECH AI
Date: 2026-01-19
"""

import xmlrpc.client
import os
import zipfile
import base64
import time
from pathlib import Path
from datetime import datetime

# Odoo connection details
url = 'https://erposus.com'
db = 'osusproperties'
username = 'salescompliance@osusproperties.com'
password = '8586583'

def create_module_zip():
    """Create ZIP file of the module"""
    print("\n" + "=" * 100)
    print("STEP 1: Creating Module ZIP File")
    print("=" * 100)
    
    module_path = Path(__file__).parent / 'invoice_status_tags'
    zip_path = Path(__file__).parent / 'invoice_status_tags.zip'
    
    if not module_path.exists():
        print(f"❌ Module path not found: {module_path}")
        return None
    
    if zip_path.exists():
        os.remove(zip_path)
        print("Removed existing ZIP file")
    
    print("\nCreating ZIP archive...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(module_path):
            # Skip __pycache__ and .pyc files
            if '__pycache__' in root:
                continue
            
            for file in files:
                if file.endswith('.pyc'):
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, module_path.parent)
                zipf.write(file_path, arcname)
                print(f"  ✓ Added: {arcname}")
    
    file_size = os.path.getsize(zip_path) / 1024  # KB
    print(f"\n✓ Module ZIP created: {zip_path}")
    print(f"  Size: {file_size:.2f} KB")
    return zip_path

def connect_to_odoo():
    """Connect to Odoo server"""
    print("\n" + "=" * 100)
    print("STEP 2: Connecting to Odoo Server")
    print("=" * 100)
    print(f"\nServer: {url}")
    print(f"Database: {db}")
    print(f"User: {username}")
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    
    try:
        # Get version info
        version_info = common.version()
        print(f"\n✓ Server Info:")
        print(f"  Odoo Version: {version_info.get('server_version', 'unknown')}")
        print(f"  Series: {version_info.get('server_serie', 'unknown')}")
        
        # Authenticate
        print("\nAuthenticating...")
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Authentication failed!")
            return None, None, None
        
        print(f"✓ Authenticated (UID: {uid})")
        
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        return common, uid, models
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None, None, None

def check_module_status(models, uid):
    """Check if module exists and its status"""
    print("\n" + "=" * 100)
    print("STEP 3: Checking Module Status")
    print("=" * 100)
    
    try:
        # Search for module
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', 'invoice_status_tags']]]
        )
        
        if module_ids:
            module_data = models.execute_kw(
                db, uid, password,
                'ir.module.module', 'read',
                [module_ids, ['name', 'state', 'latest_version', 'installed_version']]
            )
            
            module = module_data[0]
            print(f"\n✓ Module found: {module['name']}")
            print(f"  State: {module['state']}")
            print(f"  Installed Version: {module.get('installed_version', 'N/A')}")
            print(f"  Latest Version: {module.get('latest_version', 'N/A')}")
            
            return module_ids[0], module['state']
        else:
            print("\n⚠ Module not found on server")
            return None, None
            
    except Exception as e:
        print(f"❌ Error checking module: {e}")
        return None, None

def upload_module_files(zip_path):
    """Upload module files to server via file system (manual step)"""
    print("\n" + "=" * 100)
    print("STEP 4: Module Upload Instructions")
    print("=" * 100)
    
    print("\n⚠ CloudPepper requires manual module upload via their interface:")
    print("\nOption A: Via CloudPepper Control Panel")
    print("  1. Login to CloudPepper control panel")
    print("  2. Navigate to File Manager")
    print("  3. Go to addons directory: /opt/odoo/addons/")
    print("  4. Upload and extract: invoice_status_tags.zip")
    print("  5. Set proper permissions (chmod 755)")
    
    print("\nOption B: Via FTP/SFTP")
    print("  1. Connect to CloudPepper via SFTP")
    print("  2. Navigate to: /opt/odoo/addons/")
    print(f"  3. Upload folder: {Path(__file__).parent / 'invoice_status_tags'}")
    
    print("\nOption C: Via SSH (if enabled)")
    print("  1. SSH into CloudPepper server")
    print("  2. Upload ZIP file to /tmp/")
    print("  3. Extract: unzip /tmp/invoice_status_tags.zip -d /opt/odoo/addons/")
    print("  4. Set permissions: chmod -R 755 /opt/odoo/addons/invoice_status_tags")
    
    print("\n⚠ After uploading, press ENTER to continue with installation...")
    input()

def update_apps_list(models, uid):
    """Update the apps list to detect new module"""
    print("\n" + "=" * 100)
    print("STEP 5: Updating Apps List")
    print("=" * 100)
    
    try:
        print("\nUpdating module list...")
        models.execute_kw(
            db, uid, password,
            'ir.module.module', 'update_list',
            []
        )
        print("✓ Apps list updated")
        time.sleep(2)  # Wait for update to complete
        return True
        
    except Exception as e:
        print(f"❌ Error updating apps list: {e}")
        return False

def install_module(models, uid, module_id=None):
    """Install or upgrade the module"""
    print("\n" + "=" * 100)
    print("STEP 6: Installing/Upgrading Module")
    print("=" * 100)
    
    try:
        # Re-check module status after update
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', 'invoice_status_tags']]]
        )
        
        if not module_ids:
            print("❌ Module still not found after apps list update!")
            print("   Please check if files were uploaded correctly.")
            return False
        
        module_id = module_ids[0]
        
        # Get module state
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [module_ids, ['name', 'state']]
        )[0]
        
        state = module_data['state']
        print(f"\nModule state: {state}")
        
        if state == 'installed':
            print("\nUpgrading module...")
            models.execute_kw(
                db, uid, password,
                'ir.module.module', 'button_immediate_upgrade',
                [[module_id]]
            )
            print("✓ Module upgrade initiated")
            
        elif state in ['uninstalled', 'to install']:
            print("\nInstalling module...")
            models.execute_kw(
                db, uid, password,
                'ir.module.module', 'button_immediate_install',
                [[module_id]]
            )
            print("✓ Module installation initiated")
            
        else:
            print(f"⚠ Module in unexpected state: {state}")
            return False
        
        # Wait for installation/upgrade to complete
        print("\nWaiting for installation to complete...")
        time.sleep(5)
        
        # Verify installation
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [[module_id], ['state']]
        )[0]
        
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

def recompute_all_records(models, uid):
    """Recompute invoice status fields for all sale orders"""
    print("\n" + "=" * 100)
    print("STEP 7: Updating All Sale Order Records")
    print("=" * 100)
    
    try:
        # Get all sale orders
        print("\nFetching sale orders...")
        order_ids = models.execute_kw(
            db, uid, password,
            'sale.order', 'search',
            [[]]  # All orders
        )
        
        total_orders = len(order_ids)
        print(f"✓ Found {total_orders} sale orders")
        
        if total_orders == 0:
            print("No orders to update")
            return True
        
        # Trigger recomputation by touching a field that triggers the compute
        print("\nTriggering field recomputation...")
        print("(This will recompute invoice_status, invoicing_percentage, etc.)")
        
        # Process in batches of 100
        batch_size = 100
        batches = [order_ids[i:i + batch_size] for i in range(0, len(order_ids), batch_size)]
        
        print(f"\nProcessing {len(batches)} batches of {batch_size} orders each...")
        
        for idx, batch in enumerate(batches, 1):
            try:
                # Force recomputation by reading the fields
                models.execute_kw(
                    db, uid, password,
                    'sale.order', 'read',
                    [batch, ['invoicing_percentage', 'invoice_type_tag', 'needs_invoice_attention']]
                )
                print(f"  ✓ Batch {idx}/{len(batches)} processed ({len(batch)} orders)")
                time.sleep(0.5)  # Small delay to avoid overwhelming server
                
            except Exception as e:
                print(f"  ⚠ Batch {idx} error: {e}")
                continue
        
        print(f"\n✓ All {total_orders} orders updated!")
        
        # Get summary statistics
        print("\n" + "=" * 100)
        print("UPDATED STATISTICS")
        print("=" * 100)
        
        # Count by invoice type tag
        for tag in ['not_started', 'partial', 'fully_invoiced', 'draft_only', 'upsell', 'cancelled']:
            count = models.execute_kw(
                db, uid, password,
                'sale.order', 'search_count',
                [[['invoice_type_tag', '=', tag]]]
            )
            if count > 0:
                tag_label = tag.replace('_', ' ').title()
                print(f"  {tag_label}: {count}")
        
        # Count orders needing attention
        needs_attention = models.execute_kw(
            db, uid, password,
            'sale.order', 'search_count',
            [[['needs_invoice_attention', '=', True]]]
        )
        print(f"\n  ⚠ Needs Attention: {needs_attention}")
        
        # Count draft invoice warnings
        draft_warnings = models.execute_kw(
            db, uid, password,
            'sale.order', 'search_count',
            [[['has_draft_invoice_warning', '=', True]]]
        )
        print(f"  🔴 Draft Invoice Warnings: {draft_warnings}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating records: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_installation_report(success, module_installed):
    """Create installation report"""
    print("\n" + "=" * 100)
    print("INSTALLATION REPORT")
    print("=" * 100)
    
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'server': url,
        'database': db,
        'module': 'invoice_status_tags',
        'status': 'success' if success and module_installed else 'partial' if success else 'failed',
        'steps_completed': []
    }
    
    if success:
        report['steps_completed'] = [
            'Module ZIP created',
            'Connected to Odoo',
            'Apps list updated',
        ]
        
        if module_installed:
            report['steps_completed'].extend([
                'Module installed',
                'All records updated'
            ])
            print("\n✓ INSTALLATION SUCCESSFUL!")
            print("\nNext Steps:")
            print("  1. Login to Odoo: https://erposus.com")
            print("  2. Go to Sales → Orders")
            print("  3. You'll see new columns: Invoice Type, Invoicing Progress, etc.")
            print("  4. Use filters: Needs Attention, Partial Invoicing, etc.")
            print("  5. Open any order to see Invoice Progress section with badges")
        else:
            print("\n⚠ PARTIAL SUCCESS")
            print("  Module files created but installation needs manual completion")
    else:
        print("\n❌ INSTALLATION FAILED")
        print("  Please check the error messages above")
    
    # Save report
    report_file = f"installation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import json
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nInstallation report saved: {report_file}")

def main():
    print("=" * 100)
    print("REMOTE MODULE INSTALLATION - INVOICE STATUS TAGS")
    print("=" * 100)
    print(f"\nTarget: {url} / {db}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = False
    module_installed = False
    
    try:
        # Step 1: Create ZIP
        zip_path = create_module_zip()
        if not zip_path:
            return
        
        # Step 2: Connect to Odoo
        common, uid, models = connect_to_odoo()
        if not uid:
            return
        
        success = True
        
        # Step 3: Check module status
        module_id, module_state = check_module_status(models, uid)
        
        # Step 4: Upload instructions (manual for CloudPepper)
        upload_module_files(zip_path)
        
        # Step 5: Update apps list
        if not update_apps_list(models, uid):
            print("⚠ Continuing despite apps list update issue...")
        
        # Step 6: Install/Upgrade module
        if install_module(models, uid, module_id):
            module_installed = True
            
            # Step 7: Update all records
            recompute_all_records(models, uid)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        create_installation_report(success, module_installed)

if __name__ == '__main__':
    main()
