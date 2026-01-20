#!/usr/bin/env python3
"""
Run installation commands on CloudPepper server after module upload
Completes the installation started by deploy_with_ssh_key.py
"""

import subprocess
import os
from pathlib import Path

# SSH configuration
SSH_KEY_PATH = Path(os.path.expanduser("~/.ssh/id_rsa"))
CLOUDPEPPER_HOST = "139.84.163.11"
CLOUDPEPPER_USER = "root"
CLOUDPEPPER_PORT = "22"

# Server paths
SERVER_EXTRA_ADDONS = "/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844"
SERVER_PYTHON = "/var/odoo/osusproperties/venv/bin/python3"
SERVER_ODOO_BIN = "/var/odoo/osusproperties/src/odoo-bin"
SERVER_CONFIG = "/var/odoo/osusproperties/odoo.conf"

def run_ssh_command(cmd):
    """Run command on server via SSH"""
    ssh_cmd = f'ssh -i "{SSH_KEY_PATH}" -p {CLOUDPEPPER_PORT} {CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST} "{cmd}"'
    print(f"\n>> {cmd}\n")
    return subprocess.run(ssh_cmd, shell=True)

print("\n" + "="*80)
print("CLOUDPEPPER SERVER INSTALLATION - COMPLETION STEP")
print("="*80)

print("\nStep 1: Setting permissions...")
run_ssh_command(f"cd {SERVER_EXTRA_ADDONS} && chown -R odoo:odoo invoice_status_tags && chmod -R 755 invoice_status_tags && find invoice_status_tags -type f -exec chmod 644 {{}} \\;")

print("\nStep 2: Updating module list...")
run_ssh_command(f"cd /var/odoo/osusproperties && sudo -u odoo {SERVER_PYTHON} {SERVER_ODOO_BIN} -c {SERVER_CONFIG} --no-http --stop-after-init --update-list")

print("\nStep 3: Installing module...")
run_ssh_command(f"sudo -u odoo {SERVER_PYTHON} {SERVER_ODOO_BIN} -c {SERVER_CONFIG} --no-http --stop-after-init -i invoice_status_tags -d osusproperties")

print("\nStep 4: Restarting Odoo...")
run_ssh_command("sudo systemctl restart odoo")

print("\n" + "="*80)
print("INSTALLATION COMPLETE!")
print("="*80)
print("\nNow run the local update script:")
print("  python update_all_records_after_install.py")
