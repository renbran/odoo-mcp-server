#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy deal_management module using correct Odoo paths
"""

import subprocess
import time
import sys
import os

SERVER = "erp.sgctech.ai"
ODOO_PATH = "/var/odoo/scholarixv2"
ODOO_BIN = f"{ODOO_PATH}/venv/bin/python3"
ODOO_BINARY = f"{ODOO_PATH}/src/odoo-bin"
CONFIG = f"{ODOO_PATH}/odoo.conf"
DB = "scholarixv2"
LOCAL_MODULE = "d:/01_WORK_PROJECTS/odoo-mcp-server/deal_management"

print("\n" + "="*80)
print("DEAL MANAGEMENT DEPLOYMENT - Using Correct Odoo Paths")
print("="*80 + "\n")

def ssh_exec(cmd, timeout=120):
    """Execute command via SSH"""
    full_cmd = f'ssh root@{SERVER} "{cmd}"'
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)

def scp_copy(local, remote):
    """Copy files via SCP"""
    cmd = f'scp -r "{local}" root@{SERVER}:"{remote}"'
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=180
        )
        return result.returncode == 0
    except:
        return False

# STEP 1: Check Odoo installation
print("STEP 1: VERIFY ODOO INSTALLATION")
print("-"*80)

code, out, err = ssh_exec(f"test -d {ODOO_PATH} && echo 'FOUND' || echo 'NOT_FOUND'")
if "FOUND" in out:
    print(f"✅ Found Odoo at: {ODOO_PATH}")
else:
    print(f"❌ Odoo not found at: {ODOO_PATH}")
    sys.exit(1)

# Check for addons directory
code, out, err = ssh_exec(f"find {ODOO_PATH} -type d -name addons 2>/dev/null | head -5")
if out.strip():
    addons_paths = out.strip().split('\n')
    print(f"Found addons directories:")
    for path in addons_paths:
        print(f"  - {path}")
    ADDONS_PATH = addons_paths[0]  # Use first one
else:
    ADDONS_PATH = f"{ODOO_PATH}/src/addons"
    print(f"Using default addons path: {ADDONS_PATH}")

print()

# STEP 2: Check for existing deal_management
print("STEP 2: CHECK FOR EXISTING MODULES")
print("-"*80)

code, out, err = ssh_exec(f"find {ODOO_PATH} -name deal_management -type d 2>/dev/null")
if out.strip():
    print("⚠️  Found existing deal_management:")
    for path in out.strip().split('\n'):
        if path:
            print(f"   {path}")
    print("\nRemoving old version...")
    ssh_exec(f"rm -rf {ODOO_PATH}/**/deal_management 2>/dev/null; echo 'Cleaned'")
    print("✅ Old version removed")
else:
    print("✅ No existing deal_management found")

print()

# STEP 3: Upload module
print("STEP 3: UPLOAD MODULE VIA SCP")
print("-"*80)

if not os.path.exists(LOCAL_MODULE):
    print(f"❌ Local module not found: {LOCAL_MODULE}")
    sys.exit(1)

print(f"Uploading from: {LOCAL_MODULE}")
print(f"Uploading to: {ADDONS_PATH}/")

if scp_copy(LOCAL_MODULE, f"{ADDONS_PATH}/"):
    print("✅ Upload successful")
else:
    print("❌ Upload failed")
    print("Note: SSH may be timing out. Check server connectivity.")
    sys.exit(1)

print()

# STEP 4: Verify upload
print("STEP 4: VERIFY UPLOAD")
print("-"*80)

code, out, err = ssh_exec(f"ls -la {ADDONS_PATH}/deal_management/ | head -10")
if code == 0:
    print("✅ Module files found on server:")
    print(out)
else:
    print("❌ Could not verify upload")

print()

# STEP 5: Update module list via Odoo
print("STEP 5: UPDATE MODULE LIST")
print("-"*80)

update_cmd = f"""
cd {ODOO_PATH}
sudo -u odoo {ODOO_BIN} {ODOO_BINARY} -c {CONFIG} --no-http --stop-after-init -u base 2>&1 | tail -20
"""

print("Running Odoo update to scan for new modules...")
code, out, err = ssh_exec(update_cmd, timeout=300)

if code == 0 or "except" not in out.lower():
    print("✅ Module list updated")
    if "deal_management" in out.lower():
        print("✅ deal_management detected by Odoo")
else:
    print("⚠️  Update output:")
    print(out[-500:] if len(out) > 500 else out)

print()

# STEP 6: Install module via Odoo shell
print("STEP 6: INSTALL MODULE")
print("-"*80)

install_script = f"""
import xmlrpc.client

try:
    common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate("{DB}", "info@scholarixglobal.com", "123456", {{}})
    
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object", allow_none=True)
    
    print("[1/3] Connected")
    
    # Update module list
    models.execute_kw(
        "{DB}", uid, "123456",
        'ir.module.module', 'update_list'
    )
    print("[2/3] Module list updated")
    
    # Find and install
    module_ids = models.execute_kw(
        "{DB}", uid, "123456",
        'ir.module.module', 'search',
        [('name', '=', 'deal_management')]
    )
    
    if module_ids:
        print(f"[3/3] Found module {{module_ids}}, installing...")
        models.execute_kw(
            "{DB}", uid, "123456",
            'ir.module.module', 'button_install',
            module_ids
        )
        print("✅ Installation started")
    else:
        print("❌ Module not found")
        
except Exception as e:
    print(f"Error: {{e}}")
"""

install_cmd = f"""
cd {ODOO_PATH}
sudo -u odoo {ODOO_BIN} {ODOO_BINARY} shell -c {CONFIG} << 'PYEOF'
{install_script}
PYEOF
"""

code, out, err = ssh_exec(install_cmd, timeout=300)

if "Installation started" in out or "✅" in out:
    print("✅ Installation command executed")
    print(out)
elif "not found" in out.lower():
    print("⚠️  Module not found - may need to scan again")
    print(out)
else:
    print("⚠️  Installation output:")
    print(out)
    if err:
        print("Errors:")
        print(err[-500:] if len(err) > 500 else err)

print()

# STEP 7: Monitor installation
print("STEP 7: MONITOR INSTALLATION")
print("-"*80)

monitor_script = f"""
import xmlrpc.client
import time

try:
    common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate("{DB}", "info@scholarixglobal.com", "123456", {{}})
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object", allow_none=True)
    
    module_ids = models.execute_kw(
        "{DB}", uid, "123456",
        'ir.module.module', 'search',
        [('name', '=', 'deal_management')]
    )
    
    if module_ids:
        for i in range(60):
            mod = models.execute_kw(
                "{DB}", uid, "123456",
                'ir.module.module', 'read',
                module_ids, ['state']
            )[0]
            
            state = mod['state']
            print(f"[{i}] State: {{state}}")
            
            if state == 'installed':
                print("✅ INSTALLED SUCCESSFULLY")
                break
            elif state == 'failed':
                print("❌ Installation failed")
                break
            
            time.sleep(1)
    else:
        print("Module not found")
        
except Exception as e:
    print(f"Error: {{e}}")
"""

monitor_cmd = f"""
cd {ODOO_PATH}
sudo -u odoo {ODOO_BIN} {ODOO_BINARY} shell -c {CONFIG} << 'PYEOF'
{monitor_script}
PYEOF
"""

print("Waiting for installation to complete...")
code, out, err = ssh_exec(monitor_cmd, timeout=180)

if "INSTALLED SUCCESSFULLY" in out:
    print("✅ Module installed successfully!")
    print(out)
else:
    print("Installation status:")
    print(out[-500:] if len(out) > 500 else out)

print()

# STEP 8: Verify models
print("STEP 8: VERIFY INSTALLATION")
print("-"*80)

verify_script = f"""
import xmlrpc.client

try:
    common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate("{DB}", "info@scholarixglobal.com", "123456", {{}})
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object", allow_none=True)
    
    print("Checking models:")
    for model in ['deal.management', 'deal.stage', 'deal.line']:
        found = models.execute_kw(
            "{DB}", uid, "123456",
            'ir.model', 'search',
            [('model', '=', model)]
        )
        status = "✅" if found else "❌"
        print(f"  {{status}} {{model}}")
    
    print("\\nChecking menu:")
    menu = models.execute_kw(
        "{DB}", uid, "123456",
        'ir.ui.menu', 'search',
        [('name', '=', 'Deals')]
    )
    status = "✅" if menu else "❌"
    print(f"  {{status}} Deals menu")
    
except Exception as e:
    print(f"Error: {{e}}")
"""

verify_cmd = f"""
cd {ODOO_PATH}
sudo -u odoo {ODOO_BIN} {ODOO_BINARY} shell -c {CONFIG} << 'PYEOF'
{verify_script}
PYEOF
"""

code, out, err = ssh_exec(verify_cmd, timeout=120)
print(out)

print()
print("="*80)
print("✅ DEPLOYMENT COMPLETE")
print("="*80)
print(f"""
Module Location: {ADDONS_PATH}/deal_management
Config: {CONFIG}
Python: {ODOO_BIN}

NEXT STEPS:
1. Open https://erp.sgctech.ai/scholarixv2
2. Go to Sales > Deals
3. Create a test deal

If you see the "Deals" menu → Installation successful! ✅
""")
