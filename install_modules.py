#!/usr/bin/env python3
"""
Odoo Module Installation Script
Installs commission_ax and hr_uae modules with all dependencies
"""

import xmlrpc.client
import time

# Connection settings
url = "http://localhost:8069"
db = "odoo17_test"
username = "admin"
password = "admin"

def wait_for_odoo():
    """Wait for Odoo to be ready"""
    print("⏳ Waiting for Odoo to be ready...")
    max_attempts = 30
    for i in range(max_attempts):
        try:
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            version = common.version()
            print(f"✅ Odoo is ready! Version: {version.get('server_version', 'unknown')}")
            return True
        except Exception as e:
            if i < max_attempts - 1:
                print(f"   Attempt {i+1}/{max_attempts}: Not ready yet, waiting...")
                time.sleep(2)
            else:
                print(f"❌ Odoo not ready after {max_attempts} attempts")
                return False
    return False

def check_database_exists():
    """Check if database exists"""
    try:
        db_list = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/db')
        databases = db_list.list()
        exists = db in databases
        print(f"📊 Database '{db}' exists: {exists}")
        print(f"   Available databases: {databases}")
        return exists
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def create_database():
    """Create Odoo database"""
    try:
        print(f"\n🔨 Creating database '{db}'...")
        db_api = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/db')
        
        # Create database with demo data
        db_api.create_database(
            'admin',  # master password
            db,       # database name
            True,     # demo data
            'en_US',  # language
            username, # admin login
            password, # admin password
            'AE'      # country code (UAE)
        )
        
        print(f"✅ Database '{db}' created successfully!")
        print("⏳ Waiting for database initialization (30 seconds)...")
        time.sleep(30)
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def authenticate():
    """Authenticate with Odoo"""
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"✅ Authenticated successfully! UID: {uid}")
            return uid
        else:
            print("❌ Authentication failed")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def install_module(uid, module_name, description=""):
    """Install a single module"""
    try:
        print(f"\n📦 Installing {description or module_name}...")
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Search for module
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', module_name]]]
        )
        
        if not module_ids:
            print(f"❌ Module '{module_name}' not found!")
            return False
        
        # Check current state
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [module_ids], {'fields': ['name', 'state']}
        )
        
        current_state = module_data[0]['state']
        print(f"   Current state: {current_state}")
        
        if current_state == 'installed':
            print(f"✅ {module_name} already installed!")
            return True
        
        # Install module
        models.execute_kw(
            db, uid, password,
            'ir.module.module', 'button_immediate_install',
            [module_ids]
        )
        
        print(f"⏳ Installing {module_name}... (this may take a moment)")
        time.sleep(5)
        
        # Verify installation
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [module_ids], {'fields': ['state']}
        )
        
        if module_data[0]['state'] == 'installed':
            print(f"✅ {module_name} installed successfully!")
            return True
        else:
            print(f"⚠️  {module_name} state: {module_data[0]['state']}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing {module_name}: {e}")
        return False

def main():
    """Main installation process"""
    print("=" * 60)
    print("🚀 Odoo Module Installation Script")
    print("=" * 60)
    
    # Step 1: Wait for Odoo
    if not wait_for_odoo():
        return False
    
    # Step 2: Check/Create database
    if not check_database_exists():
        if not create_database():
            return False
    
    # Step 3: Authenticate
    uid = authenticate()
    if not uid:
        return False
    
    # Step 4: Install modules in order
    modules_to_install = [
        # Core dependencies
        ('hr', 'Human Resources'),
        ('hr_holidays', 'Time Off'),
        ('hr_payroll_community', 'Payroll Community'),
        ('sale_management', 'Sales Management'),
        ('crm', 'CRM'),
        ('purchase', 'Purchase'),
        ('account', 'Accounting'),
        
        # Custom modules
        ('le_sale_type', 'Sale Type Extension'),
        ('commission_ax', 'Advanced Commission Management'),
        ('hr_uae', 'UAE HR Extended'),
    ]
    
    print(f"\n📋 Installing {len(modules_to_install)} modules...")
    print("=" * 60)
    
    installed_count = 0
    failed_modules = []
    
    for module_name, description in modules_to_install:
        if install_module(uid, module_name, description):
            installed_count += 1
        else:
            failed_modules.append(module_name)
        time.sleep(2)  # Small delay between installations
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INSTALLATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully installed: {installed_count}/{len(modules_to_install)}")
    
    if failed_modules:
        print(f"❌ Failed modules: {', '.join(failed_modules)}")
    else:
        print("🎉 All modules installed successfully!")
    
    print("=" * 60)
    print("\n🌐 Access Odoo at: http://localhost:8069")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Database: {db}")
    print("=" * 60)
    
    return len(failed_modules) == 0

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
