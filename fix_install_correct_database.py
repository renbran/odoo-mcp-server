#!/usr/bin/env python3
"""
Find the correct Odoo service for osusproperties and install module
"""

import subprocess
import os
import time
from pathlib import Path

SSH_KEY_PATH = Path(os.path.expanduser("~/.ssh/id_rsa"))
CLOUDPEPPER_HOST = "139.84.163.11"
CLOUDPEPPER_USER = "root"
CLOUDPEPPER_PORT = "22"

def ssh_cmd(cmd):
    """Execute SSH command"""
    ssh_command = f'ssh -i "{SSH_KEY_PATH}" -p {CLOUDPEPPER_PORT} {CLOUDPEPPER_USER}@{CLOUDPEPPER_HOST} "{cmd}"'
    print(f"\n>>> {cmd}\n")
    return subprocess.run(ssh_command, shell=True)

print("\n" + "="*80)
print("FINDING CORRECT ODOO SERVICE FOR OSUSPROPERTIES")
print("="*80)

# Step 1: List all Odoo services
print("\nStep 1: Checking all systemd services...")
ssh_cmd("systemctl list-units --type=service | grep -i odoo")

# Step 2: Check which service runs osusproperties
print("\n" + "="*80)
print("Step 2: Identifying osusproperties service...")
ssh_cmd("grep -r 'osusproperties' /etc/systemd/system/*.service 2>/dev/null | head -5")

# Step 3: Check the odoo.service configuration
print("\n" + "="*80)
print("Step 3: Checking main odoo.service configuration...")
ssh_cmd("cat /etc/systemd/system/odoo.service | head -30")

# Step 4: List all Odoo instances in /var/odoo
print("\n" + "="*80)
print("Step 4: Listing all Odoo instances...")
ssh_cmd("ls -d /var/odoo/*/ 2>/dev/null | head -20")

# Step 5: Check if there's a dedicated osusproperties systemd service
print("\n" + "="*80)
print("Step 5: Looking for osusproperties-specific service...")
ssh_cmd("find /etc/systemd/system -name '*osusproperties*' -o -name '*osus*' 2>/dev/null")

# Step 6: Manual installation on osusproperties
print("\n" + "="*80)
print("Step 6: Installing module directly on osusproperties instance...")

ODOO_HOME = "/var/odoo/osusproperties"
ODOO_BIN = f"{ODOO_HOME}/src/odoo-bin"
CONFIG = f"{ODOO_HOME}/odoo.conf"
PYTHON = f"{ODOO_HOME}/venv/bin/python3"
DB = "osusproperties"
MODULE = "invoice_status_tags"

print(f"\nTarget Instance:")
print(f"  Home: {ODOO_HOME}")
print(f"  Database: {DB}")
print(f"  Module: {MODULE}")

# Check if the config exists
print("\nVerifying osusproperties config exists...")
ssh_cmd(f"cat {CONFIG} | head -10")

# Stop any running instance for this database
print("\n" + "="*80)
print("Step 7: Stopping services...")
ssh_cmd("sudo systemctl stop odoo")
time.sleep(5)

# Install on osusproperties
print("\n" + "="*80)
print("Step 8: Installing module on osusproperties...")
print(f"\nCommand:")
print(f"  cd {ODOO_HOME}")
print(f"  sudo -u odoo {PYTHON} {ODOO_BIN} -c {CONFIG} -i {MODULE} -d {DB} --no-http --stop-after-init")

ssh_cmd(f"cd {ODOO_HOME} && sudo -u odoo {PYTHON} {ODOO_BIN} -c {CONFIG} -i {MODULE} -d {DB} --no-http --stop-after-init")

# Restart service
print("\n" + "="*80)
print("Step 9: Restarting Odoo service...")
ssh_cmd("sudo systemctl restart odoo")
time.sleep(5)

# Verify
print("\n" + "="*80)
print("Step 10: Verifying installation...")
ssh_cmd("sudo systemctl status odoo --no-pager | head -15")

print("\n" + "="*80)
print("INSTALLATION ON OSUSPROPERTIES DATABASE COMPLETE")
print("="*80 + "\n")
