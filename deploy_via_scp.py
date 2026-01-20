#!/usr/bin/env python3
"""
Direct SCP Deployment for invoice_status_tags Module
Copies module files directly to CloudPepper server and performs installation
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Configuration
CLOUDPEPPER_HOST = input("Enter CloudPepper server hostname/IP (e.g., 139.84.163.11): ").strip()

# SSH Key configuration - check if available
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")
use_ssh_key = False
if os.path.exists(SSH_KEY_PATH):
    use_ssh_key = True
    CLOUDPEPPER_USER = "root"
    print(f"\nSSH key found: {SSH_KEY_PATH}")
    print(f"Will use SSH key authentication as 'root'")
else:
    # Check alternative key names
    for key_name in ["id_ed25519", "id_ecdsa", "id_dsa"]:
        alt_path = os.path.expanduser(f"~/.ssh/{key_name}")
        if os.path.exists(alt_path):
            SSH_KEY_PATH = alt_path
            use_ssh_key = True
            CLOUDPEPPER_USER = "root"
            print(f"\nSSH key found: {SSH_KEY_PATH}")
            print(f"Will use SSH key authentication as 'root'")
            break

if not use_ssh_key:
    # Use password authentication with osusproperties credentials
    CLOUDPEPPER_USER = "salescompliance@osusproperties.com"
    CLOUDPEPPER_PASSWORD = "8586583"
    print(f"\nNo SSH key found - will use password authentication")
    print(f"User: {CLOUDPEPPER_USER}")

CLOUDPEPPER_PORT = input("Enter SSH port (default 22): ").strip() or "22"

print(f"Host: {CLOUDPEPPER_HOST}:{CLOUDPEPPER_PORT}")
print(f"User: {CLOUDPEPPER_USER}\n")

# Server paths
SERVER_EXTRA_ADDONS = "/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844"
SERVER_PYTHON = "/var/odoo/osusproperties/venv/bin/python3"
SERVER_ODOO_BIN = "/var/odoo/osusproperties/src/odoo-bin"
SERVER_CONFIG = "/var/odoo/osusproperties/odoo.conf"

# Local paths
LOCAL_MODULE = Path(__file__).parent / "invoice_status_tags"
LOCAL_UPDATE_SCRIPT = Path(__file__).parent / "update_all_records_after_install.py"

def build_ssh_cmd(cmd):
    """Build SSH command with proper key or password authentication"""
    if use_ssh_key and os.path.exists(SSH_KEY_PATH):
        return f'ssh -i "{SSH_KEY_PATH}" -p {CLOUDPEPPER_PORT} {CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST} "{cmd}"'
    else:
        return f'ssh -p {CLOUDPEPPER_PORT} {CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST} "{cmd}"'

def build_scp_cmd(src, dst):
    """Build SCP command with proper authentication"""
    if use_ssh_key and os.path.exists(SSH_KEY_PATH):
        return f'scp -i "{SSH_KEY_PATH}" -r -P {CLOUDPEPPER_PORT} "{src}" "{CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST}:{dst}"'
    else:
        return f'scp -r -P {CLOUDPEPPER_PORT} "{src}" "{CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST}:{dst}"'

def run_command(cmd, description=""):
    """Run shell command and return success status"""
    print(f"\n{'='*80}")
    if description:
        print(f">> {description}")
    print(f">> {cmd[:100]}..." if len(cmd) > 100 else f">> {cmd}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"[SUCCESS] {description or cmd}")
            return True
        else:
            print(f"[FAILED] {description or cmd} (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def verify_local_module():
    """Verify module files exist locally"""
    print("\nVerifying local module files...")
    
    required_files = [
        LOCAL_MODULE / "__init__.py",
        LOCAL_MODULE / "__manifest__.py",
        LOCAL_MODULE / "models" / "__init__.py",
        LOCAL_MODULE / "models" / "sale_order.py",
        LOCAL_MODULE / "views" / "sale_order_views.xml",
    ]
    
    for f in required_files:
        if not f.exists():
            print(f"[ERROR] Missing: {f}")
            return False
        print(f"[OK] {f.name}")
    
    return True

def copy_module_via_scp():
    """Copy module to server via SCP"""
    print("\n" + "="*80)
    print("STEP 1: COPYING MODULE FILES VIA SCP")
    print("="*80)
    
    # SCP command to copy entire module folder
    src = str(LOCAL_MODULE).replace("\\", "/")
    dst = SERVER_EXTRA_ADDONS
    
    cmd = build_scp_cmd(src, dst)
    
    print(f"\nSource: {src}")
    print(f"Destination: {CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST}:{dst}")
    print(f"Authentication: {'SSH Key' if use_ssh_key else 'Password'}\n")
    
    if not run_command(cmd, "Copying module files to CloudPepper server"):
        print("\n[FAILED] Could not copy files. Check credentials and connectivity.")
        return False
    
    return True

def install_module_on_server():
    """SSH into server and run installation commands"""
    print("\n" + "="*80)
    print("STEP 2: RUNNING INSTALLATION ON SERVER")
    print("="*80)
    
    # Installation commands to run on server
    install_commands = f"""
# Set permissions
cd {SERVER_EXTRA_ADDONS}
sudo chown -R odoo:odoo invoice_status_tags
sudo chmod -R 755 invoice_status_tags
sudo find invoice_status_tags -type f -exec chmod 644 {{}} \\;

# Update module list
cd /var/odoo/osusproperties
echo "Updating module list..."
sudo -u odoo {SERVER_PYTHON} {SERVER_ODOO_BIN} \\
    -c {SERVER_CONFIG} \\
    --no-http \\
    --stop-after-init \\
    --update-list
echo "Module list updated"

# Install module
echo "Installing module..."
sudo -u odoo {SERVER_PYTHON} {SERVER_ODOO_BIN} \\
    -c {SERVER_CONFIG} \\
    --no-http \\
    --stop-after-init \\
    -i invoice_status_tags \\
    -d osusproperties
echo "Module installed"

# Restart Odoo
echo "Restarting Odoo..."
sudo systemctl restart odoo
echo "Odoo restarted"

echo "Installation complete!"
"""
    
    # Run via SSH
    ssh_cmd = build_ssh_cmd(f"bash -s << 'EOFSCRIPT'{install_commands}EOFSCRIPT")
    
    if not run_command(ssh_cmd, "Running installation commands on server"):
        print("\n[FAILED] Installation failed. Check SSH credentials and server logs.")
        return False
    
    return True

def verify_installation_on_server():
    """Verify module is installed on server"""
    print("\n" + "="*80)
    print("STEP 3: VERIFYING INSTALLATION")
    print("="*80)
    
    verify_cmd = build_ssh_cmd(f"ls -la {SERVER_EXTRA_ADDONS}/invoice_status_tags/__manifest__.py")
    
    return run_command(verify_cmd, "Verifying module folder on server")

def update_records_locally():
    """Update all records locally via XML-RPC"""
    print("\n" + "="*80)
    print("STEP 4: UPDATING ALL SALE ORDER RECORDS")
    print("="*80)
    
    if not LOCAL_UPDATE_SCRIPT.exists():
        print(f"[WARNING] Update script not found: {LOCAL_UPDATE_SCRIPT}")
        print("You can run it manually later:")
        print(f"  python {LOCAL_UPDATE_SCRIPT.name}")
        return True
    
    cmd = f'python "{LOCAL_UPDATE_SCRIPT}"'
    return run_command(cmd, "Updating all sale order records")

def main():
    """Main deployment flow"""
    print("\n" + "="*80)
    print("CLOUDPEPPER DIRECT SCP DEPLOYMENT")
    print("Invoice Status Tags Module Installation")
    print("="*80)
    
    # Step 0: Verify local files
    if not verify_local_module():
        print("\n[FATAL] Local module verification failed")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("DEPLOYMENT PLAN")
    print("="*80)
    print(f"Server: {CLOUDPEPPER_HOST} (user: {CLOUDPEPPER_USER}, port: {CLOUDPEPPER_PORT})")
    print(f"Target path: {SERVER_EXTRA_ADDONS}/invoice_status_tags")
    print(f"Module: {LOCAL_MODULE}")
    print("\nSteps:")
    print("  1. Copy module files via SCP")
    print("  2. SSH into server and run installation")
    print("  3. Verify installation")
    print("  4. Update all sale order records")
    
    confirm = input("\nProceed with deployment? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Deployment cancelled")
        sys.exit(0)
    
    # Step 1: Copy via SCP
    if not copy_module_via_scp():
        sys.exit(1)
    
    print("\nWaiting 3 seconds before installation...")
    time.sleep(3)
    
    # Step 2: Install on server
    if not install_module_on_server():
        sys.exit(1)
    
    print("\nWaiting 10 seconds for Odoo to restart...")
    time.sleep(10)
    
    # Step 3: Verify
    if not verify_installation_on_server():
        print("\n[WARNING] Could not verify installation, but it may have succeeded")
    
    # Step 4: Update records
    print("\nNow updating all sale order records locally...")
    time.sleep(2)
    if not update_records_locally():
        print("\n[WARNING] Record update failed, but module may be installed")
        print("You can run the update script manually:")
        print(f"  python {LOCAL_UPDATE_SCRIPT.name}")
    
    # Summary
    print("\n" + "="*80)
    print("DEPLOYMENT SUMMARY")
    print("="*80)
    print("Module: invoice_status_tags")
    print(f"Server: {CLOUDPEPPER_HOST}")
    print(f"Location: {SERVER_EXTRA_ADDONS}/invoice_status_tags")
    print("\nNext steps:")
    print("  1. Login to Odoo: https://erposus.com")
    print("  2. Go to Apps > Installed > invoice_status_tags")
    print("  3. Go to Sales > Orders")
    print("  4. View new columns: Invoice Type, Invoicing Progress, Needs Attention")
    print("  5. Check new menu items under Sales > Orders")
    print("\nFilters now available:")
    print("  - Needs Attention")
    print("  - Partial Invoicing")
    print("  - Has Draft Invoices")
    print("  - Upsell Orders")
    print("  - Draft Only")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
