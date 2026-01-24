#!/usr/bin/env python3
"""
HR UAE Payroll Compliance Module - Installation Script
Installs the module in Odoo Docker environment (odoo17_test database)
"""

import xmlrpc.client
import sys

# Configuration
ODOO_URL = 'http://localhost:8069'
DB_NAME = 'odoo17_test'
USERNAME = 'admin'
PASSWORD = 'admin'
MODULE_NAME = 'hr_uae_payroll_compliance'

def install_module():
    """Install HR UAE Payroll Compliance module via XML-RPC"""
    
    print("=" * 70)
    print("HR UAE PAYROLL COMPLIANCE - INSTALLATION")
    print("=" * 70)
    print()
    
    try:
        # Step 1: Authenticate
        print("🔐 Authenticating...")
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
        
        if not uid:
            print("❌ Authentication failed! Check credentials.")
            return False
        
        print(f"✅ Authenticated as user ID: {uid}")
        print()
        
        # Step 2: Connect to object endpoint
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        
        # Step 3: Update module list
        print("📋 Updating module list...")
        models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'ir.module.module', 'update_list', [[]]
        )
        print("✅ Module list updated")
        print()
        
        # Step 4: Search for the module
        print(f"🔍 Searching for module '{MODULE_NAME}'...")
        module_ids = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'ir.module.module', 'search',
            [[('name', '=', MODULE_NAME)]]
        )
        
        if not module_ids:
            print(f"❌ Module '{MODULE_NAME}' not found!")
            print()
            print("📝 Troubleshooting:")
            print("   1. Ensure module is in /mnt/extra-addons/ in Docker container")
            print("   2. Restart Odoo container: docker restart odoo17")
            print("   3. Check module files exist and __manifest__.py is valid")
            return False
        
        module_id = module_ids[0]
        print(f"✅ Module found (ID: {module_id})")
        print()
        
        # Step 5: Check module state
        module_data = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'ir.module.module', 'read',
            [module_id], {'fields': ['name', 'state', 'shortdesc']}
        )[0]
        
        print(f"📦 Module: {module_data['shortdesc']}")
        print(f"📊 Current state: {module_data['state']}")
        print()
        
        if module_data['state'] == 'installed':
            print("✅ Module is already installed!")
            
            # Ask if user wants to upgrade
            upgrade = input("Do you want to upgrade the module? (y/n): ").strip().lower()
            if upgrade == 'y':
                print()
                print("⬆️  Upgrading module...")
                models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'ir.module.module', 'button_immediate_upgrade',
                    [[module_id]]
                )
                print("✅ Module upgraded successfully!")
            return True
        
        # Step 6: Install the module
        print("⚙️  Installing module...")
        print("   (This may take a minute...)")
        print()
        
        models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'ir.module.module', 'button_immediate_install',
            [[module_id]]
        )
        
        print("✅ Module installed successfully!")
        print()
        
        # Step 7: Verify installation
        print("🔍 Verifying installation...")
        module_data = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'ir.module.module', 'read',
            [module_id], {'fields': ['state']}
        )[0]
        
        if module_data['state'] == 'installed':
            print("✅ Installation verified!")
            print()
            print("=" * 70)
            print("🎉 SUCCESS - HR UAE PAYROLL COMPLIANCE INSTALLED")
            print("=" * 70)
            print()
            print("📋 Next Steps:")
            print("   1. Navigate to: HR → Employees")
            print("   2. Open any employee record")
            print("   3. Go to 'UAE Compliance' tab")
            print("   4. Fill WPS and Emirates ID fields")
            print("   5. Go to: HR → Contracts")
            print("   6. Set up UAE salary structure (Basic ≥ 50%)")
            print()
            print("📖 For detailed usage, see: test_modules/hr_uae_payroll_compliance/README.md")
            print()
            return True
        else:
            print(f"⚠️  Installation status unclear: {module_data['state']}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print("📝 Troubleshooting:")
        print("   1. Check Odoo is running: docker ps")
        print("   2. Check database name is 'odoo17_test'")
        print("   3. Verify admin credentials")
        print("   4. Check module is in extra-addons directory")
        return False

if __name__ == '__main__':
    print()
    success = install_module()
    print()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
