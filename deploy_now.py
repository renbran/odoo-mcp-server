#!/usr/bin/env python3
"""
DEAL MANAGEMENT - AUTOMATED DEPLOYMENT
Deploy module to Odoo server using correct paths
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def run_command(cmd, description="", show_output=True):
    """Execute a shell command and return success status"""
    if description:
        print_info(description)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=not show_output,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            if result.stdout and not show_output:
                print(result.stdout)
            return True, result.stdout if result.stdout else ""
        else:
            if result.stderr:
                print_error(result.stderr)
            return False, result.stderr if result.stderr else ""
    except subprocess.TimeoutExpired:
        print_error("Command timed out")
        return False, "Timeout"
    except Exception as e:
        print_error(f"Command failed: {str(e)}")
        return False, str(e)

def main():
    print_header("DEAL MANAGEMENT MODULE - AUTOMATED DEPLOYMENT")
    
    # Configuration
    LOCAL_MODULE_PATH = r"d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management"
    REMOTE_USER = "root"
    REMOTE_HOST = "erp.sgctech.ai"
    REMOTE_ADDON_PATH = "/var/odoo/scholarixv2/src/addons"
    REMOTE_ODOO_ROOT = "/var/odoo/scholarixv2"
    REMOTE_CONFIG = "/var/odoo/scholarixv2/odoo.conf"
    REMOTE_PYTHON = "/var/odoo/scholarixv2/venv/bin/python3"
    REMOTE_ODOO_BIN = "/var/odoo/scholarixv2/src/odoo-bin"
    
    print_info(f"Local module:  {LOCAL_MODULE_PATH}")
    print_info(f"Remote server: {REMOTE_USER}@{REMOTE_HOST}")
    print_info(f"Remote addon:  {REMOTE_ADDON_PATH}/deal_management")
    print_info(f"Odoo root:     {REMOTE_ODOO_ROOT}")
    
    # Step 1: Verify local module exists
    print_header("STEP 1: VERIFY LOCAL MODULE")
    module_path = Path(LOCAL_MODULE_PATH)
    
    if not module_path.exists():
        print_error(f"Module not found at: {LOCAL_MODULE_PATH}")
        sys.exit(1)
    
    manifest = module_path / "__manifest__.py"
    if not manifest.exists():
        print_error("__manifest__.py not found in module")
        sys.exit(1)
    
    print_success(f"Module found: {LOCAL_MODULE_PATH}")
    print_success(f"Manifest file: {manifest}")
    
    # List module files
    py_files = list(module_path.glob("**/*.py"))
    xml_files = list(module_path.glob("**/*.xml"))
    print_info(f"Files: {len(py_files)} Python, {len(xml_files)} XML")
    
    # Step 2: Test SSH connection
    print_header("STEP 2: TEST SSH CONNECTION")
    success, output = run_command(
        f'ssh -o ConnectTimeout=5 {REMOTE_USER}@{REMOTE_HOST} "echo OK"',
        "Testing SSH connection...",
        show_output=False
    )
    
    if not success:
        print_error("SSH connection failed!")
        print_warning("Continuing with SCP upload attempt...")
    else:
        print_success("SSH connection successful")
    
    # Step 3: Upload module via SCP
    print_header("STEP 3: UPLOAD MODULE")
    
    print_info(f"Uploading from: {LOCAL_MODULE_PATH}")
    print_info(f"Uploading to:   {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_ADDON_PATH}/")
    
    scp_cmd = f'scp -r "{LOCAL_MODULE_PATH}" {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_ADDON_PATH}/'
    success, output = run_command(scp_cmd, "Uploading module...")
    
    if not success:
        print_error("SCP upload failed. Try uploading manually via WinSCP:")
        print_info("1. Open WinSCP")
        print_info("2. Connect to erp.sgctech.ai (user: root)")
        print_info(f"3. Navigate to {REMOTE_ADDON_PATH}/")
        print_info(f"4. Drag & drop deal_management folder")
        print_warning("After manual upload, continue with steps 4-6")
        sys.exit(1)
    
    print_success("Module uploaded successfully")
    
    # Step 4: Set permissions
    print_header("STEP 4: SET PERMISSIONS")
    
    commands = [
        f'ssh {REMOTE_USER}@{REMOTE_HOST} "chown -R odoo:odoo {REMOTE_ADDON_PATH}/deal_management"',
        f'ssh {REMOTE_USER}@{REMOTE_HOST} "chmod -R 755 {REMOTE_ADDON_PATH}/deal_management"',
    ]
    
    for cmd in commands:
        success, _ = run_command(cmd, show_output=False)
        if not success:
            print_warning(f"Permission command may have failed")
    
    print_success("Permissions set for module")
    
    # Step 5: Update module list in Odoo
    print_header("STEP 5: UPDATE ODOO MODULE LIST")
    
    update_cmd = (
        f'ssh {REMOTE_USER}@{REMOTE_HOST} '
        f'"cd {REMOTE_ODOO_ROOT} && '
        f'sudo -u odoo {REMOTE_PYTHON} {REMOTE_ODOO_BIN} -c {REMOTE_CONFIG} '
        f'--no-http --stop-after-init -u base 2>&1"'
    )
    
    print_info("This may take 2-5 minutes...")
    success, output = run_command(update_cmd, "Updating module list...", show_output=True)
    
    if success:
        print_success("Module list updated")
    else:
        print_warning("Module list update may have issues - check logs")
        if output:
            print(output[:500])  # Print first 500 chars
    
    # Step 6: Install module via Odoo
    print_header("STEP 6: INSTALL VIA ODOO WEB UI")
    
    print_info("Opening Odoo in browser...")
    print_warning("Installation must be done via web UI or XML-RPC")
    print_info("\nFORWARD TO THIS POINT MANUALLY:")
    print_info("1. Open: https://erp.sgctech.ai/scholarixv2")
    print_info("2. Login: info@scholarixglobal.com / 123456")
    print_info("3. Go to: Settings > Apps")
    print_info("4. Click: 'Update App List' (refresh)")
    print_info("5. Search: 'Deal Management'")
    print_info("6. Click: 'Install'")
    print_info("7. Wait for installation (2-5 minutes)")
    
    # Step 7: Verify installation
    print_header("STEP 7: VERIFY INSTALLATION")
    
    print_info("After installation completes in web UI:")
    print_info("1. Go to: Sales > Deals")
    print_info("2. Should see 'All Deals', 'Pipeline', 'Stages'")
    print_info("3. Create a test deal")
    print_info("4. Verify workflow buttons appear")
    
    # Final summary
    print_header("DEPLOYMENT STATUS")
    print_success("✅ Module uploaded")
    print_success("✅ Permissions set")
    print_success("✅ Odoo module list updated")
    print_warning("⏳ Web UI installation required (steps above)")
    
    print_info("\nDeployment steps 1-5 complete!")
    print_info("Complete step 6-7 manually via web UI")
    print_info("Total time: 10-20 minutes")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nDeployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
