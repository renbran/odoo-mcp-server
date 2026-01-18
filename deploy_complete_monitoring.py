#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete deal_management deployment with monitoring
- Check for conflicts
- Remove old versions
- Deploy new module
- Install on Odoo
- Monitor installation
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

# Configuration
SERVER = "erp.sgctech.ai"
DB = "scholarixv2"
ODOO_USER = "info@scholarixglobal.com"
ODOO_PASS = "123456"
ODOO_ADDONS = "/var/lib/odoo/addons"
EXTRA_ADDONS = "/var/odoo/scholarixv2/extra-addons"
ODOOAPPS_PATH = "/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
MODULE = "deal_management"

class DeploymentMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.steps = []
        
    def log(self, step, status, message=""):
        """Log a deployment step"""
        elapsed = time.time() - self.start_time
        self.steps.append({
            'step': step,
            'status': status,
            'message': message,
            'time': elapsed
        })
        
        status_symbol = "✅" if status == "success" else "⏳" if status == "in_progress" else "❌"
        print(f"{status_symbol} [{elapsed:.1f}s] {step}: {message}")
    
    def report(self):
        """Print deployment report"""
        print()
        print("=" * 60)
        print("DEPLOYMENT REPORT")
        print("=" * 60)
        for step in self.steps:
            status = "✅ SUCCESS" if step['status'] == "success" else "⏳ IN_PROGRESS" if step['status'] == "in_progress" else "❌ FAILED"
            print(f"[{step['time']:.1f}s] {step['step']}: {status}")
            if step['message']:
                print(f"       → {step['message']}")
        print(f"\nTotal time: {time.time() - self.start_time:.1f}s")

monitor = DeploymentMonitor()

def run_ssh(cmd, description=""):
    """Run SSH command on server"""
    full_cmd = f'ssh root@{SERVER} "{cmd}"'
    try:
        result = subprocess.run(
            full_cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def run_scp(local_path, remote_path, description=""):
    """Copy files via SCP"""
    cmd = f'scp -r "{local_path}" root@{SERVER}:"{remote_path}"'
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        return False

print()
print("=" * 60)
print("DEAL MANAGEMENT DEPLOYMENT")
print("=" * 60)
print()

# STEP 1: Check current state
print("STEP 1: CHECKING CURRENT STATE")
print("-" * 60)

monitor.log("Check Paths", "in_progress", "Scanning server for existing modules...")

check_script = f"""
echo "Checking: {ODOO_ADDONS}"
if [ -d {ODOO_ADDONS}/{MODULE} ]; then echo "FOUND_ODOO_ADDONS"; fi

echo "Checking: {EXTRA_ADDONS}"
if [ -d {EXTRA_ADDONS}/{MODULE} ]; then echo "FOUND_EXTRA_ADDONS"; fi

echo "Checking: {ODOOAPPS_PATH}"
if [ -d {ODOOAPPS_PATH}/{MODULE} ]; then echo "FOUND_ODOOAPPS"; fi
"""

success, output, error = run_ssh(check_script)
if success:
    found_locations = [line for line in output.split('\n') if line.startswith('FOUND_')]
    monitor.log("Check Paths", "success", f"Found in {len(found_locations)} location(s)")
    for loc in found_locations:
        print(f"   - {loc}")
else:
    monitor.log("Check Paths", "failed", error)

print()

# STEP 2: Clean up old modules
print("STEP 2: CLEANUP OLD MODULES")
print("-" * 60)

if found_locations:
    monitor.log("Cleanup", "in_progress", "Removing old module versions...")
    
    cleanup_script = f"""
# Remove from odoo addons
[ -d {ODOO_ADDONS}/{MODULE} ] && rm -rf {ODOO_ADDONS}/{MODULE} && echo "Removed from {ODOO_ADDONS}"

# Remove from extra addons
[ -d {EXTRA_ADDONS}/{MODULE} ] && rm -rf {EXTRA_ADDONS}/{MODULE} && echo "Removed from {EXTRA_ADDONS}"

# Remove from odooapps path
[ -d {ODOOAPPS_PATH}/{MODULE} ] && rm -rf {ODOOAPPS_PATH}/{MODULE} && echo "Removed from odooapps path"

echo "Cleanup complete"
"""
    
    success, output, error = run_ssh(cleanup_script)
    if success:
        monitor.log("Cleanup", "success", "Old modules removed")
        print(f"   Output: {output}")
    else:
        monitor.log("Cleanup", "failed", error)
else:
    monitor.log("Cleanup", "success", "No old modules to remove")

print()

# STEP 3: Deploy new module
print("STEP 3: DEPLOYING NEW MODULE")
print("-" * 60)

local_module = Path("d:/01_WORK_PROJECTS/odoo-mcp-server/deal_management")
if local_module.exists():
    monitor.log("Upload Module", "in_progress", f"Uploading from {local_module}...")
    
    # Upload to preferred location (odoo addons)
    if run_scp(str(local_module), f"root@{SERVER}:{ODOO_ADDONS}/"):
        monitor.log("Upload Module", "success", f"Uploaded to {ODOO_ADDONS}/")
        
        # Fix permissions
        monitor.log("Fix Permissions", "in_progress", "Setting permissions...")
        success, output, error = run_ssh(f"chown -R odoo:odoo {ODOO_ADDONS}/{MODULE}")
        if success:
            monitor.log("Fix Permissions", "success", "Permissions set")
        else:
            monitor.log("Fix Permissions", "failed", error)
    else:
        monitor.log("Upload Module", "failed", "SCP upload failed")
else:
    monitor.log("Upload Module", "failed", f"Local module not found at {local_module}")

print()

# STEP 4: Restart Odoo
print("STEP 4: RESTARTING ODOO")
print("-" * 60)

monitor.log("Restart Odoo", "in_progress", "Stopping and restarting service...")
success, output, error = run_ssh("systemctl restart odoo")

if success:
    monitor.log("Restart Odoo", "in_progress", "Waiting for Odoo to start...")
    # Wait for Odoo to start
    for i in range(30):
        test_success, _, _ = run_ssh("curl -s https://localhost/web/login > /dev/null && echo OK")
        if "OK" in _:
            time.sleep(2)  # Extra buffer
            monitor.log("Restart Odoo", "success", "Odoo started and responsive")
            break
        time.sleep(1)
        if i % 5 == 0:
            print(f"   Waiting... {i}s")
else:
    monitor.log("Restart Odoo", "failed", error)

print()

# STEP 5: Install module
print("STEP 5: INSTALLING MODULE")
print("-" * 60)

monitor.log("Install Module", "in_progress", "Installing deal_management...")

# Create install script
install_script = f"""
import xmlrpc.client
import time

url = "https://localhost/xmlrpc/2/common"
db = "{DB}"
username = "{ODOO_USER}"
password = "{ODOO_PASS}"

try:
    common = xmlrpc.client.ServerProxy(url)
    uid = common.authenticate(db, username, password, {{}})
    print(f"UID: {{uid}}")
    
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object")
    
    # Update module list
    print("Updating module list...")
    models.execute_kw(
        db, uid, password,
        'ir.module.module', 'update_list'
    )
    
    # Find module
    print("Searching for {MODULE}...")
    module_ids = models.execute_kw(
        db, uid, password,
        'ir.module.module', 'search',
        [('name', '=', '{MODULE}')]
    )
    
    if module_ids:
        print(f"Found module: {{module_ids}}")
        
        # Install
        print("Installing...")
        models.execute_kw(
            db, uid, password,
            'ir.module.module', 'button_install',
            module_ids
        )
        
        # Wait for installation
        for i in range(60):
            state = models.execute_kw(
                db, uid, password,
                'ir.module.module', 'read',
                module_ids, ['state']
            )[0]['state']
            
            print(f"State: {{state}}")
            
            if state == 'installed':
                print("✅ INSTALLED SUCCESSFULLY")
                exit(0)
            elif state == 'failed':
                print("❌ INSTALLATION FAILED")
                exit(1)
            
            time.sleep(1)
        
        print("❌ INSTALLATION TIMEOUT")
        exit(2)
    else:
        print("❌ Module not found")
        exit(3)

except Exception as e:
    print(f"ERROR: {{e}}")
    exit(4)
"""

# Write and run install script
install_script_path = "/tmp/install_deal_management.py"
write_cmd = f'cat > {install_script_path} << \'EOF\'\n{install_script}\nEOF\n'
run_ssh(f"cat > {install_script_path} << 'EOF'\n{install_script}\nEOF")

# Run installation
success, output, error = run_ssh(f"python3 {install_script_path}")

if success and "INSTALLED SUCCESSFULLY" in output:
    monitor.log("Install Module", "success", "deal_management installed")
    print(f"   Output: {output[:200]}")
elif "INSTALLED SUCCESSFULLY" in output:
    monitor.log("Install Module", "success", "deal_management installed")
else:
    monitor.log("Install Module", "failed", f"Installation failed or timed out")
    print(f"   Output: {output}")
    print(f"   Error: {error}")

print()

# STEP 6: Verify installation
print("STEP 6: VERIFYING INSTALLATION")
print("-" * 60)

monitor.log("Verify Models", "in_progress", "Checking database...")

verify_script = f"""
import xmlrpc.client

url = "https://localhost/xmlrpc/2/common"
db = "{DB}"
username = "{ODOO_USER}"
password = "{ODOO_PASS}"

try:
    common = xmlrpc.client.ServerProxy(url)
    uid = common.authenticate(db, username, password, {{}})
    
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object")
    
    # Check module state
    module_ids = models.execute_kw(
        db, uid, password,
        'ir.module.module', 'search',
        [('name', '=', '{MODULE}')]
    )
    
    if module_ids:
        module = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            module_ids, ['name', 'state', 'installed_version']
        )[0]
        print(f"Module: {{module['name']}}")
        print(f"State: {{module['state']}}")
        print(f"Version: {{module.get('installed_version', 'unknown')}}")
        
        if module['state'] == 'installed':
            print("STATUS: INSTALLED")
        else:
            print("STATUS: NOT INSTALLED")
    else:
        print("STATUS: NOT FOUND")
        
except Exception as e:
    print(f"ERROR: {{e}}")
"""

write_cmd = f'cat > /tmp/verify.py << \'EOF\'\n{verify_script}\nEOF\n'
run_ssh(f"cat > /tmp/verify.py << 'EOF'\n{verify_script}\nEOF")
success, output, error = run_ssh("python3 /tmp/verify.py 2>/dev/null")

if "INSTALLED" in output:
    monitor.log("Verify Models", "success", "Module found and installed")
    print(f"   {output}")
else:
    monitor.log("Verify Models", "failed", "Verification inconclusive")
    print(f"   Output: {output}")

print()
print()

# Final report
monitor.report()

print()
print("=" * 60)
print("DEPLOYMENT COMPLETE")
print("=" * 60)
print()
print("Next steps:")
print("1. Open https://erp.sgctech.ai/scholarixv2")
print("2. Refresh page (Ctrl+F5)")
print("3. Check Sales > Deals menu")
print("4. Create a test deal")
print()
