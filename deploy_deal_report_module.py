#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy deal_report module to remote Odoo instance
Handles module upload and installation via RPC
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import xmlrpc.client

class OdooModuleDeployer:
    """Deploys Odoo modules to remote instance"""
    
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None
        self.common = xmlrpc.client.ServerProxy(
            f'{self.url}/xmlrpc/2/common'
        )
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def authenticate(self):
        """Authenticate and get session"""
        try:
            self.uid = self.common.authenticate(
                self.db,
                self.username,
                self.password,
                {}
            )
            if not self.uid:
                print(f'❌ Authentication failed for {self.username}')
                return False
            
            self.models = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/object'
            )
            print(f'✅ Authenticated as UID {self.uid}')
            return True
        except Exception as e:
            print(f'❌ Authentication error: {e}')
            return False
    
    def check_module_installed(self, module_name):
        """Check if module is installed"""
        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'search_read',
                [[('name', '=', module_name), ('state', '=', 'installed')]],
                {'fields': ['id', 'name', 'state'], 'limit': 1}
            )
            return len(result) > 0
        except Exception as e:
            print(f'⚠️  Error checking module: {e}')
            return False
    
    def install_module(self, module_name):
        """Install module via RPC"""
        try:
            print(f'\n📦 Installing module: {module_name}')
            
            # Check if already installed
            if self.check_module_installed(module_name):
                print(f'✅ Module {module_name} already installed')
                return True
            
            # Find module
            module_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'search',
                [[('name', '=', module_name)]],
                {'limit': 1}
            )
            
            if not module_ids:
                print(f'❌ Module {module_name} not found in repository')
                print('   Make sure the module directory is in the addons path')
                return False
            
            module_id = module_ids[0]
            print(f'   Found module ID: {module_id}')
            
            # Install module
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'button_install',
                [[module_id]]
            )
            
            print(f'✅ Module {module_name} installation initiated')
            return True
            
        except Exception as e:
            print(f'❌ Installation error: {e}')
            return False
    
    def upgrade_module(self, module_name):
        """Upgrade module"""
        try:
            print(f'\n🔄 Upgrading module: {module_name}')
            
            module_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'search',
                [[('name', '=', module_name)]],
                {'limit': 1}
            )
            
            if not module_ids:
                print(f'❌ Module {module_name} not found')
                return False
            
            module_id = module_ids[0]
            
            # Check state
            module = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'read',
                [module_id],
                {'fields': ['id', 'name', 'state']}
            )[0]
            
            print(f'   Current state: {module["state"]}')
            
            if module['state'] == 'installed':
                # Upgrade
                self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'ir.module.module', 'button_upgrade',
                    [[module_id]]
                )
                print(f'✅ Module {module_name} upgrade initiated')
                return True
            elif module['state'] == 'uninstalled':
                return self.install_module(module_name)
            else:
                print(f'⚠️  Module state: {module["state"]} (may need attention)')
                return True
                
        except Exception as e:
            print(f'❌ Upgrade error: {e}')
            return False
    
    def uninstall_module(self, module_name):
        """Uninstall module"""
        try:
            print(f'\n🗑️  Uninstalling module: {module_name}')
            
            module_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'search',
                [[('name', '=', module_name)]],
                {'limit': 1}
            )
            
            if not module_ids:
                print(f'❌ Module {module_name} not found')
                return False
            
            module_id = module_ids[0]
            
            self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'button_uninstall',
                [[module_id]]
            )
            
            print(f'✅ Module {module_name} uninstall initiated')
            return True
            
        except Exception as e:
            print(f'❌ Uninstall error: {e}')
            return False
    
    def get_module_status(self, module_name):
        """Get module installation status"""
        try:
            modules = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'search_read',
                [[('name', '=', module_name)]],
                {'fields': ['id', 'name', 'version', 'state']}
            )
            
            if modules:
                module = modules[0]
                print(f'\n📋 Module Status:')
                print(f'   Name: {module["name"]}')
                print(f'   Version: {module.get("version", "N/A")}')
                print(f'   State: {module["state"]}')
                return module['state']
            else:
                print(f'❌ Module {module_name} not found')
                return None
                
        except Exception as e:
            print(f'❌ Status check error: {e}')
            return None
    
    def list_addons_path(self):
        """Get configured addons paths"""
        try:
            config = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.config_parameter', 'search_read',
                [[('key', '=', 'base_import.ir_attachment_path')]],
                {'fields': ['value']}
            )
            print(f'\n📁 Addons path configuration:')
            if config:
                print(f'   {config[0]["value"]}')
            return True
        except:
            print(f'⚠️  Could not retrieve addons path')
            return False
    
    def deploy_full(self, module_name, action='install'):
        """Full deployment workflow"""
        print(f'\n{"="*70}')
        print(f'  ODOO MODULE DEPLOYMENT')
        print(f'{"="*70}')
        print(f'Target: {self.url}/{self.db}')
        print(f'Module: {module_name}')
        print(f'Action: {action}')
        print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Authenticate
        if not self.authenticate():
            return False
        
        # Get addons paths
        self.list_addons_path()
        
        # Check current status
        print(f'\n📊 Checking module status...')
        current_state = self.get_module_status(module_name)
        
        # Execute action
        if action == 'install':
            if current_state == 'installed':
                print(f'✅ Module already installed')
                return True
            return self.install_module(module_name)
        elif action == 'upgrade':
            return self.upgrade_module(module_name)
        elif action == 'uninstall':
            return self.uninstall_module(module_name)
        elif action == 'reinstall':
            print(f'🔄 Reinstalling module...')
            if not self.uninstall_module(module_name):
                return False
            # Wait a bit for uninstall
            import time
            time.sleep(2)
            return self.install_module(module_name)
        
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Deploy deal_report module to Odoo instance'
    )
    parser.add_argument(
        '--url',
        default='https://erp.sgctech.ai',
        help='Odoo URL (default: https://erp.sgctech.ai)'
    )
    parser.add_argument(
        '--db',
        default='scholarixv2',
        help='Database name (default: scholarixv2)'
    )
    parser.add_argument(
        '--email',
        default='info@scholarixglobal.com',
        help='User email/username'
    )
    parser.add_argument(
        '--password',
        default='123456',
        help='User password'
    )
    parser.add_argument(
        '--module',
        default='deal_report',
        help='Module name to deploy (default: deal_report)'
    )
    parser.add_argument(
        '--action',
        choices=['install', 'upgrade', 'uninstall', 'reinstall', 'status'],
        default='install',
        help='Action to perform (default: install)'
    )
    
    args = parser.parse_args()
    
    deployer = OdooModuleDeployer(
        args.url,
        args.db,
        args.email,
        args.password
    )
    
    if args.action == 'status':
        deployer.authenticate()
        deployer.get_module_status(args.module)
    else:
        success = deployer.deploy_full(args.module, args.action)
        
        print(f'\n{"="*70}')
        if success:
            print(f'✅ DEPLOYMENT SUCCESSFUL')
        else:
            print(f'❌ DEPLOYMENT FAILED')
        print(f'{"="*70}\n')
        
        return 0 if success else 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
