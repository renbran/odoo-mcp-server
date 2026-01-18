#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for deal_management module conflicts and verify database state
"""

import xmlrpc.client
import json
import subprocess
import sys

# Server credentials
URL = "https://erp.sgctech.ai"
DB = "scholarixv2"
USER = "info@scholarixglobal.com"
PASSWORD = "123456"

print("=" * 60)
print("DEAL MANAGEMENT - CONFLICT CHECK & DEPLOYMENT PREP")
print("=" * 60)
print()

# Connect to Odoo
try:
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    print(f"✅ Connected to Odoo as UID {uid}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# Get model connection
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

print()
print("1. CHECKING INSTALLED MODULES")
print("-" * 60)

try:
    # Check if deal_management is installed
    installed = models.execute_kw(
        DB, uid, PASSWORD, 'ir.module.module', 'search',
        [('name', '=', 'deal_management'), ('state', '=', 'installed')]
    )
    
    if installed:
        print(f"⚠️  FOUND: deal_management is INSTALLED (id: {installed[0]})")
        
        # Get details
        module = models.execute_kw(
            DB, uid, PASSWORD, 'ir.module.module', 'read',
            installed, ['name', 'version', 'state', 'installed_version']
        )[0]
        print(f"   Name: {module['name']}")
        print(f"   Version: {module.get('installed_version', 'unknown')}")
        print(f"   State: {module['state']}")
        print()
        
        # Check for conflicts in addons path
        print("2. CHECKING REMOTE ADDON PATHS")
        print("-" * 60)
        
        ssh_cmd = (
            "ssh root@erp.sgctech.ai "
            "'find /var/lib/odoo/addons /var/odoo/scholarixv2/extra-addons -name deal_management -type d 2>/dev/null'"
        )
        
        try:
            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=10)
            paths = [p.strip() for p in result.stdout.strip().split('\n') if p.strip()]
            
            if paths:
                print(f"⚠️  FOUND {len(paths)} deal_management location(s):")
                for path in paths:
                    print(f"   - {path}")
                print()
                
                if len(paths) > 1:
                    print("❌ MULTIPLE VERSIONS DETECTED - Need to clean up!")
                else:
                    print("✅ Single location - OK")
            else:
                print("✅ No conflicting paths found")
        except subprocess.TimeoutExpired:
            print("⚠️  SSH command timed out")
        except Exception as e:
            print(f"⚠️  Could not check paths: {e}")
        
    else:
        print("✅ deal_management NOT currently installed")
        
        # Check if it exists but not installed
        all_modules = models.execute_kw(
            DB, uid, PASSWORD, 'ir.module.module', 'search',
            [('name', '=', 'deal_management')]
        )
        if all_modules:
            print(f"⚠️  But it EXISTS in database (not installed): {all_modules}")
        else:
            print("✅ Module not in database at all")
    
except Exception as e:
    print(f"❌ Error checking modules: {e}")
    sys.exit(1)

print()
print("3. CHECKING DATABASE MODELS")
print("-" * 60)

# Check if deal.management model exists
try:
    models_found = models.execute_kw(
        DB, uid, PASSWORD, 'ir.model', 'search',
        [('model', '=', 'deal.management')]
    )
    
    if models_found:
        print(f"⚠️  FOUND: deal.management model exists in database")
        model_info = models.execute_kw(
            DB, uid, PASSWORD, 'ir.model', 'read',
            models_found, ['model', 'name', 'module']
        )[0]
        print(f"   Name: {model_info['name']}")
        print(f"   Module: {model_info.get('module', 'unknown')}")
    else:
        print("✅ deal.management model NOT in database")
        
except Exception as e:
    print(f"⚠️  Error checking models: {e}")

print()
print("=" * 60)
print("DEPLOYMENT READINESS SUMMARY")
print("=" * 60)

# Summary
print()
print("NEXT STEPS:")
print("1. ✅ This script has identified the current state")
print("2. ⏳ Will now proceed with uninstall/reinstall")
print("3. ⏳ Will upload fresh module")
print("4. ⏳ Will install with monitoring")
print()
