#!/usr/bin/env python3
"""
Verify module installation on osusproperties database
"""

import subprocess
import os
from pathlib import Path
import time

SSH_KEY_PATH = Path(os.path.expanduser("~/.ssh/id_rsa"))
CLOUDPEPPER_HOST = "139.84.163.11"
CLOUDPEPPER_USER = "root"
CLOUDPEPPER_PORT = "22"

def ssh_cmd(cmd):
    """Execute SSH command"""
    ssh_command = f'ssh -i "{SSH_KEY_PATH}" -p {CLOUDPEPPER_PORT} {CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST} "{cmd}"'
    return subprocess.run(ssh_command, shell=True, capture_output=True, text=True)

print("\n" + "="*80)
print("VERIFYING MODULE INSTALLATION ON OSUSPROPERTIES")
print("="*80)

ODOO_HOME = "/var/odoo/osusproperties"
PYTHON = f"{ODOO_HOME}/venv/bin/python3"
CONFIG = f"{ODOO_HOME}/odoo.conf"
DB = "osusproperties"
MODULE = "invoice_status_tags"

# Wait for service to fully initialize
print("\nWaiting 10 seconds for Odoo to fully initialize...")
time.sleep(10)

print("\nExecuting verification on server...")

# First, check module exists in the database using psql
print("\n1. Checking if module exists in ir_module_module table...")
result = ssh_cmd(f"sudo -u postgres psql osusproperties -c \"SELECT id, name, state, latest_version FROM ir_module_module WHERE name = 'invoice_status_tags';\"")
print(result.stdout)
if result.stderr and "FATAL" not in result.stderr:
    print("STDERR:", result.stderr)

# Check if sale.order has the new fields
print("\n2. Checking if sale.order table has new fields...")
result = ssh_cmd(f"sudo -u postgres psql osusproperties -c \"SELECT column_name FROM information_schema.columns WHERE table_name='sale_order' AND column_name IN ('invoice_type_tag', 'invoicing_percentage', 'posted_invoice_count', 'has_draft_invoice_warning', 'needs_invoice_attention') ORDER BY column_name;\"")
print(result.stdout)
if result.stderr and "FATAL" not in result.stderr:
    print("STDERR:", result.stderr)

# Direct module file check
print("\n3. Checking if module files exist on server...")
result = ssh_cmd(f"ls -lah /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/invoice_status_tags/")
print(result.stdout)

# Check service logs for module loading
print("\n4. Checking recent service logs for module initialization...")
result = ssh_cmd(f"journalctl -u odoo-osusproperties -n 30 --no-pager | grep -i 'invoice_status_tags\\|loaded\\|loading'")
print(result.stdout)

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80 + "\n")
