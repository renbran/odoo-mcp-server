#!/usr/bin/env python3
"""
Verify module installation and check if folder exists
"""

import subprocess
import os
from pathlib import Path

SSH_KEY_PATH = Path(os.path.expanduser("~/.ssh/id_rsa"))
CLOUDPEPPER_HOST = "139.84.163.11"
CLOUDPEPPER_USER = "root"
CLOUDPEPPER_PORT = "22"

def run_ssh(cmd):
    ssh_cmd = f'ssh -i "{SSH_KEY_PATH}" -p {CLOUDPEPPER_PORT} {CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST} "{cmd}"'
    print(f"\n>> Running: {cmd}")
    subprocess.run(ssh_cmd, shell=True)

print("="*80)
print("VERIFYING MODULE INSTALLATION")
print("="*80)

print("\n1. Checking if invoice_status_tags folder exists...")
run_ssh("ls -la /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/ | grep invoice_status_tags")

print("\n2. Listing all files in invoice_status_tags folder...")
run_ssh("find /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/invoice_status_tags -type f")

print("\n3. Checking module permissions...")
run_ssh("ls -la /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/invoice_status_tags/")

print("\n4. Checking if __manifest__.py is readable...")
run_ssh("cat /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/invoice_status_tags/__manifest__.py")

print("\n" + "="*80)
print("Module verification complete!")
print("="*80)
print("\nNext steps:")
print("  1. Login to Odoo: https://erposus.com")
print("  2. Go to Settings > Apps > Apps")
print("  3. Click 'Update Apps List' (if available)")
print("  4. Search for 'Invoice Status Tags'")
print("  5. Click 'Install' button")
print("\nOr restart Odoo and check if module is auto-detected:")
print("  ssh -i ~/.ssh/id_rsa root@139.84.163.11 'sudo systemctl restart odoo'")
