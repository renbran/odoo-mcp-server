#!/usr/bin/env python3
"""
Install hr_uae module after dependency fix
"""

import xmlrpc.client
import time

# Connection settings
url = "http://localhost:8069"
db = "odoo17_test"
username = "admin"
password = "admin"

def connect():
    """Connect to Odoo"""
    print("⏳ Waiting for Odoo...")
    time.sleep(5)
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("Authentication failed!")
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print(f"✅ Connected (UID: {uid})")
    return uid, models

def update_module_list(uid, models):
    """Update module list to reflect changes"""
    print("\n🔄 Updating module list...")
    try:
        models.execute_kw(
            db, uid, password,
            'ir.module.module', 'update_list',
            []
        )
        print("✅ Module list updated")
        return True
    except Exception as e:
        print(f"❌ Error updating module list: {e}")
        return False

def install_hr_uae(uid, models):
    """Install hr_uae module"""
    print("\n📦 Installing hr_uae...")
    try:
        # Search for module
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', 'hr_uae']]]
        )
        
        if not module_ids:
            print("❌ Module 'hr_uae' not found!")
            return False
        
        # Check current state
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [module_ids], {'fields': ['name', 'state']}
        )[0]
        
        print(f"   Current state: {module_data['state']}")
        
        if module_data['state'] == 'installed':
            print("✅ hr_uae already installed!")
            return True
        
        # Install module
        models.execute_kw(
            db, uid, password,
            'ir.module.module', 'button_immediate_install',
            [module_ids]
        )
        
        print("✅ hr_uae installed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error installing hr_uae: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main installation process"""
    print("=" * 60)
    print("🚀 Installing hr_uae Module")
    print("=" * 60)
    
    try:
        uid, models = connect()
        update_module_list(uid, models)
        install_hr_uae(uid, models)
        
        print("\n" + "=" * 60)
        print("✅ Installation complete!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
