#!/usr/bin/env python3
"""
Install module on the CORRECT osusproperties service
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
    result = subprocess.run(ssh_command, shell=True)
    return result

print("\n" + "="*80)
print("INSTALLING MODULE ON CORRECT OSUSPROPERTIES SERVICE")
print("="*80)

ODOO_HOME = "/var/odoo/osusproperties"
ODOO_BIN = f"{ODOO_HOME}/src/odoo-bin"
CONFIG = f"{ODOO_HOME}/odoo.conf"
PYTHON = f"{ODOO_HOME}/venv/bin/python3"
DB = "osusproperties"
MODULE = "invoice_status_tags"
SERVICE = "odoo-osusproperties"

print(f"\n✓ Target Service: {SERVICE}")
print(f"✓ Database: {DB}")
print(f"✓ Module: {MODULE}")
print(f"✓ Home: {ODOO_HOME}")

# Step 1: Stop the CORRECT service
print("\n" + "="*80)
print("STEP 1: Stop the osusproperties service")
ssh_cmd(f"sudo systemctl stop {SERVICE}")
time.sleep(3)

# Step 2: Clear cache
print("\n" + "="*80)
print("STEP 2: Clear session cache")
ssh_cmd(f"sudo -u odoo rm -rf {ODOO_HOME}/sessions/*")

# Step 3: Install module
print("\n" + "="*80)
print("STEP 3: Install module on CORRECT service")
print(f"\nRunning Odoo installer...")
ssh_cmd(f"cd {ODOO_HOME} && sudo -u odoo {PYTHON} {ODOO_BIN} -c {CONFIG} -i {MODULE} -d {DB} --no-http --stop-after-init")

# Step 4: Start the CORRECT service
print("\n" + "="*80)
print("STEP 4: Start the osusproperties service")
ssh_cmd(f"sudo systemctl start {SERVICE}")
time.sleep(5)

# Step 5: Check status
print("\n" + "="*80)
print("STEP 5: Verify service is running")
ssh_cmd(f"sudo systemctl status {SERVICE} --no-pager | head -20")

# Step 6: Verify installation in database
print("\n" + "="*80)
print("STEP 6: Verify module installation in database")
print("\nChecking ir.module.module table...")

# Let's write a quick verification script
verify_script = f'''
import sys
sys.path.insert(0, '{ODOO_HOME}/src')
import odoo
odoo.tools.config.parse_config(['-c', '{CONFIG}'])
from odoo.api import Environment
from odoo.sql_db import db_connect

try:
    cr = db_connect('{DB}').cursor()
    env = Environment(cr, 2, {{}})
    module = env['ir.module.module'].search([('name', '=', '{MODULE}')])
    if module:
        print(f"✓ Module Found!")
        print(f"  Name: {{module.name}}")
        print(f"  State: {{module.state}}")
        print(f"  Version: {{module.latest_version}}")
    else:
        print(f"✗ Module NOT found in database")
    cr.commit()
    cr.close()
except Exception as e:
    print(f"✗ Error: {{e}}")
'''

# Write verification script to server and run it
ssh_cmd(f'''cat > {ODOO_HOME}/verify_module.py << 'EOF'
{verify_script}
EOF
''')

print("\nRunning verification script...")
ssh_cmd(f"cd {ODOO_HOME} && sudo -u odoo {PYTHON} verify_module.py")

print("\n" + "="*80)
print("INSTALLATION ON CORRECT OSUSPROPERTIES SERVICE COMPLETE!")
print("="*80 + "\n")
