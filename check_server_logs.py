#!/usr/bin/env python3
"""
Check Odoo server logs
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
    return subprocess.run(ssh_cmd, shell=True)

print("\n" + "="*80)
print("CHECKING ODOO SERVER STATUS")
print("="*80)

print("\n1. Checking Odoo service status...")
run_ssh("sudo systemctl status odoo --no-pager")

print("\n\n2. Checking recent Odoo logs (last 50 lines)...")
run_ssh("tail -50 /var/odoo/osusproperties/logs/odoo.log")

print("\n\n3. Listing installed modules...")
run_ssh("ls -la /var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/")
