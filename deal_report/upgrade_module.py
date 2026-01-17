#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Upgrade the deal_report module in Odoo.
This script will force Odoo to reload the module with the updated views.
"""

import os
import subprocess
import time
import sys

def upgrade_module():
    """Upgrade the deal_report module."""
    print("Upgrading deal_report module...")
    print("="*60)
    
    # Create a temporary database if needed
    # The module should already be installed, so we just need to upgrade it
    
    cmd = [
        "docker", "exec", "odoo17_app",
        "odoo", "-d", "odoo",
        "-u", "deal_report",
        "--without-demo=all",
        "--stop-after-init"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        print("\nReturn code:", result.returncode)
        
        if result.returncode == 0:
            print("\n" + "="*60)
            print("SUCCESS: Module upgraded successfully!")
            print("The menu and views should now be visible in Odoo.")
            return True
        else:
            print("\n" + "="*60)
            print("WARNING: Module upgrade returned non-zero exit code")
            print("The module may have upgraded partially.")
            return False
    
    except subprocess.TimeoutExpired:
        print("ERROR: Module upgrade timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def verify_module():
    """Verify the module is installed and updated."""
    print("\n" + "="*60)
    print("Verifying module installation...")
    print("="*60)
    
    cmd = [
        "docker", "exec", "odoo17_app",
        "ls", "-la", "/mnt/extra-addons/deal_report/views/"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Could not verify: {e}")

if __name__ == "__main__":
    success = upgrade_module()
    verify_module()
    
    if success:
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("1. Open Odoo in your browser: http://localhost:8069")
        print("2. Go to Apps -> Deal Report & Commissions")
        print("3. You should now see the 'Deals' menu in the Sales section")
        print("4. Check under Sales -> Deals for:")
        print("   - Deal Reports (tree view)")
        print("   - Deal Dashboard")
        print("   - Analytics (Overview, Trends, Distribution)")
        print("="*60)
    
    sys.exit(0 if success else 1)
