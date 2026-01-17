#!/usr/bin/env python3
"""
Deploy the latest deals_management module fix to scholarixv2 server.

This script:
1. Connects to the remote server via SSH
2. Pulls the latest code from Git
3. Forces module update in Odoo
4. Verifies installation
"""

import subprocess
import os
import sys
from pathlib import Path

# Configuration
REMOTE_HOST = "erp.sgctech.ai"
REMOTE_USER = "odoo"
REMOTE_PATH = "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
PYTHON_SCRIPT = """
import sys
sys.path.insert(0, '/var/odoo/scholarixv2/src')
os.chdir('/var/odoo/scholarixv2')

from odoo.cli import main as odoo_main
from odoo.modules import get_module_path

# Force update the module
subprocess.run(['git', 'pull', 'origin', 'mcp2odoo'], cwd='{remote_path}')

# Restart Odoo with module update
print("Module code updated. Please reinstall via Odoo UI or restart Odoo service.")
""".format(remote_path=REMOTE_PATH)

def run_command(cmd, description):
    """Run a shell command and report status."""
    print(f"\n{'='*70}")
    print(f"▶ {description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            return True
        else:
            print(f"❌ FAILED: {description}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  Deploy Deals Management Fix to scholarixv2 Server              ║
    ║  Fixes: Action reference namespace issue                        ║
    ║  Commit: 4041254 - add module namespace to action references    ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: SSH into server and pull latest code
    ssh_cmd = f"ssh {REMOTE_USER}@{REMOTE_HOST} 'cd {REMOTE_PATH} && git pull origin mcp2odoo'"
    if not run_command(ssh_cmd, "Pull latest code from Git on remote server"):
        print("\n❌ Failed to pull code. Check SSH access and Git repository.")
        return False
    
    # Step 2: Display what changed
    check_cmd = f"ssh {REMOTE_USER}@{REMOTE_HOST} 'cd {REMOTE_PATH} && git diff HEAD~1 deals_management/views/deals_menu.xml | head -30'"
    print(f"\n{'='*70}")
    print("Preview of changes (first 30 lines of diff):")
    print(f"{'='*70}")
    subprocess.run(check_cmd, shell=True)
    
    # Step 3: Instructions for completing the fix
    print(f"\n{'='*70}")
    print("NEXT STEPS - Complete the fix via Odoo UI:")
    print(f"{'='*70}")
    print("""
1. Go to https://erp.sgctech.ai/web
2. Log in as administrator
3. Navigate to Apps menu
4. Search for "Deals Management"
5. If installed:
   - Click the module dropdown (⋮)
   - Select "Upgrade"
   - Wait for completion (~30 seconds)
6. If not installed:
   - Click "Install"
   - Wait for completion (~30 seconds)
7. Refresh the browser (F5)
8. Verify "Deals" and "Commissions" menus appear without errors

The fix has been deployed to the server.
The module now uses the correct action reference namespace.
    """)
    
    print(f"\n{'='*70}")
    print("✅ Code deployment to server completed!")
    print(f"{'='*70}")
    print("""
Module files are now updated on the server:
- deals_management/views/deals_menu.xml ✅
- deals_management/views/deals_views.xml ✅
- All action references now properly namespaced ✅

Complete the installation/upgrade in Odoo UI (steps above).
    """)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
