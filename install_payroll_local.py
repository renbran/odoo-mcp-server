#!/usr/bin/env python3
"""
Install Payroll Modules on Local Docker Odoo Instance
Automated installation and verification
"""

import xmlrpc.client
import time
import json
from datetime import datetime

# Local Docker Instance Configuration
LOCAL_CONFIG = {
    'url': 'http://localhost:8069',
    'db': 'odoo17_test',
    'username': 'admin',
    'password': 'admin'
}

MODULES_TO_INSTALL = [
    'hr_payroll_community',
    'hr_payroll_account_community'
]

def connect_odoo(config):
    """Connect to Odoo instance"""
    print(f"Connecting to {config['url']}...")
    common = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/common")
    uid = common.authenticate(config['db'], config['username'], config['password'], {})
    
    if not uid:
        raise Exception("Authentication failed")
    
    models = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/object")
    print(f"✓ Connected (UID: {uid})\n")
    return uid, models, config

def update_module_list(uid, models, config):
    """Update module list (equivalent to 'Update Apps List')"""
    print("Updating module list...")
    try:
        models.execute_kw(
            config['db'], uid, config['password'],
            'ir.module.module', 'update_list', [[]]
        )
        print("✓ Module list updated\n")
        time.sleep(2)  # Wait for update to complete
        return True
    except Exception as e:
        print(f"✗ Error updating module list: {str(e)}\n")
        return False

def check_module_exists(uid, models, config, module_name):
    """Check if module exists and get its state"""
    module_ids = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.module.module', 'search',
        [[('name', '=', module_name)]]
    )
    
    if not module_ids:
        return None
    
    module = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.module.module', 'read',
        [module_ids, ['name', 'state', 'shortdesc', 'installed_version']]
    )[0]
    
    return module

def install_module(uid, models, config, module_name):
    """Install a module"""
    print(f"Installing {module_name}...")
    
    module_ids = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.module.module', 'search',
        [[('name', '=', module_name)]]
    )
    
    if not module_ids:
        print(f"✗ Module {module_name} not found")
        return False
    
    try:
        # Trigger installation
        models.execute_kw(
            config['db'], uid, config['password'],
            'ir.module.module', 'button_immediate_install',
            [module_ids]
        )
        
        print(f"✓ Installation initiated for {module_name}")
        print(f"  Waiting for installation to complete...")
        
        # Wait and verify
        time.sleep(5)
        
        # Check installation status
        module = check_module_exists(uid, models, config, module_name)
        if module and module['state'] == 'installed':
            print(f"✓ {module_name} installed successfully!")
            return True
        else:
            print(f"⚠ Installation may require server restart")
            return True
            
    except Exception as e:
        print(f"✗ Installation failed: {str(e)}")
        return False

def verify_installation(uid, models, config):
    """Verify all modules are installed"""
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80 + "\n")
    
    all_installed = True
    
    for module_name in MODULES_TO_INSTALL:
        module = check_module_exists(uid, models, config, module_name)
        if module:
            status = "✓ INSTALLED" if module['state'] == 'installed' else f"✗ {module['state'].upper()}"
            print(f"{status}: {module_name}")
            print(f"  Description: {module['shortdesc']}")
            if module.get('installed_version'):
                print(f"  Version: {module['installed_version']}")
            print()
            
            if module['state'] != 'installed':
                all_installed = False
        else:
            print(f"✗ NOT FOUND: {module_name}\n")
            all_installed = False
    
    return all_installed

def main():
    """Main installation process"""
    print("="*80)
    print("PAYROLL MODULE INSTALLATION - LOCAL DOCKER INSTANCE")
    print("="*80)
    print(f"Target: {LOCAL_CONFIG['url']}")
    print(f"Database: {LOCAL_CONFIG['db']}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Connect
        uid, models, config = connect_odoo(LOCAL_CONFIG)
        
        # Update module list first
        update_module_list(uid, models, config)
        
        # Check current state
        print("Checking current module state...")
        for module_name in MODULES_TO_INSTALL:
            module = check_module_exists(uid, models, config, module_name)
            if module:
                print(f"  {module_name}: {module['state']}")
            else:
                print(f"  {module_name}: NOT FOUND")
        print()
        
        # Install modules
        print("="*80)
        print("INSTALLATION")
        print("="*80 + "\n")
        
        for module_name in MODULES_TO_INSTALL:
            module = check_module_exists(uid, models, config, module_name)
            
            if not module:
                print(f"✗ Cannot install {module_name} - module not found")
                print(f"  Please ensure module files are in Odoo addons path\n")
                continue
            
            if module['state'] == 'installed':
                print(f"✓ {module_name} already installed\n")
                continue
            
            install_module(uid, models, config, module_name)
            time.sleep(2)
        
        # Verify installation
        all_installed = verify_installation(uid, models, config)
        
        # Summary
        print("="*80)
        print("INSTALLATION SUMMARY")
        print("="*80)
        
        if all_installed:
            print("\n✓ All modules installed successfully!")
            print("\nYou can now proceed with Phase 1 of UAE Payroll Compliance implementation")
        else:
            print("\n⚠ Some modules may require manual installation or Odoo restart")
            print("\nTroubleshooting steps:")
            print("1. Check Odoo logs: docker logs <container_name>")
            print("2. Verify modules are in addons path")
            print("3. Restart Odoo: docker restart <container_name>")
            print("4. Try manual installation via web interface")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nPlease verify:")
        print("- Docker container is running")
        print("- Odoo is accessible at http://localhost:8069")
        print("- Database credentials are correct")

if __name__ == '__main__':
    main()
