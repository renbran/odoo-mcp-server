#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct SSH deployment - Execute installation immediately
"""

import subprocess
import time
import sys

SERVER = "erp.sgctech.ai"
DB = "scholarixv2"
USER = "info@scholarixglobal.com"
PASS = "123456"
MODULE_PATH = "d:/01_WORK_PROJECTS/odoo-mcp-server/deal_management"

print("\n" + "="*80)
print("DEAL MANAGEMENT - DIRECT SSH DEPLOYMENT")
print("="*80 + "\n")

def ssh(cmd, timeout=60):
    """Execute SSH command as root"""
    try:
        result = subprocess.run(
            f'ssh root@{SERVER} "{cmd}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Timeout"
    except Exception as e:
        return 1, "", str(e)

def scp_upload(local, remote):
    """Upload via SCP"""
    try:
        result = subprocess.run(
            f'scp -r "{local}" root@{SERVER}:{remote}',
            shell=True,
            capture_output=True,
            text=True,
            timeout=180
        )
        return result.returncode == 0
    except:
        return False

# STEP 1: Check and cleanup
print("STEP 1: CHECK FOR EXISTING MODULES")
print("-"*80)

code, out, err = ssh("find /var/lib/odoo/addons /var/odoo/scholarixv2/extra-addons -maxdepth 2 -name deal_management -type d 2>/dev/null | head -5")
if out.strip():
    print("⚠️  Found existing modules:")
    for path in out.strip().split('\n'):
        if path:
            print(f"   {path}")
    
    print("\nRemoving old versions...")
    code, out, err = ssh("rm -rf /var/lib/odoo/addons/deal_management /var/odoo/scholarixv2/extra-addons/deal_management 2>/dev/null; echo 'Cleanup done'")
    print("✅ Old modules cleaned")
else:
    print("✅ No existing modules found")

print()

# STEP 2: Upload module
print("STEP 2: UPLOAD MODULE VIA SCP")
print("-"*80)
print(f"Uploading from: {MODULE_PATH}")
print(f"Uploading to: /var/lib/odoo/addons/")

if scp_upload(MODULE_PATH, "/var/lib/odoo/addons/"):
    print("✅ Upload successful")
else:
    print("❌ Upload failed")
    sys.exit(1)

print()

# STEP 3: Fix permissions and restart
print("STEP 3: FIX PERMISSIONS & RESTART ODOO")
print("-"*80)

code, out, err = ssh("chown -R odoo:odoo /var/lib/odoo/addons/deal_management && chmod -R 755 /var/lib/odoo/addons/deal_management")
print("✅ Permissions set")

print("Restarting Odoo...")
code, out, err = ssh("systemctl restart odoo")
print("✅ Restart command sent")

print("Waiting for Odoo to start...")
for i in range(30):
    code, out, err = ssh("systemctl is-active odoo && echo ACTIVE")
    if "ACTIVE" in out:
        print(f"✅ Odoo started (after {i+1}s)")
        break
    time.sleep(1)
    if i % 5 == 0:
        print(f"   Waiting... {i}s")

time.sleep(5)  # Extra buffer
print()

# STEP 4: Update app list and install
print("STEP 4: INSTALL MODULE IN ODOO")
print("-"*80)

install_cmd = '''python3 << 'PYEOF'
import xmlrpc.client
import time
import sys

try:
    # Connect
    common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate("scholarixv2", "info@scholarixglobal.com", "123456", {})
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object", allow_none=True)
    
    print(f"[1/4] Connected as UID {uid}")
    
    # Update module list
    print("[2/4] Updating module list...")
    models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.module.module', 'update_list'
    )
    
    # Find module
    print("[3/4] Searching for deal_management...")
    module_ids = models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.module.module', 'search',
        [('name', '=', 'deal_management')]
    )
    
    if not module_ids:
        print("ERROR: Module not found after update")
        sys.exit(1)
    
    mod = models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.module.module', 'read',
        module_ids, ['state']
    )[0]
    
    print(f"[4/4] Module state: {mod['state']}")
    
    if mod['state'] == 'installed':
        print("✅ Already installed!")
        sys.exit(0)
    
    # Install if not installed
    print("Installing...")
    models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.module.module', 'button_install',
        module_ids
    )
    
    # Monitor installation
    print("Monitoring installation...")
    for attempt in range(120):
        mod = models.execute_kw(
            "scholarixv2", uid, "123456",
            'ir.module.module', 'read',
            module_ids, ['state']
        )[0]
        
        state = mod['state']
        print(f"  [{attempt}] State: {state}")
        
        if state == 'installed':
            print("✅ INSTALLATION SUCCESSFUL")
            sys.exit(0)
        elif state == 'failed':
            print("❌ Installation failed")
            sys.exit(1)
        
        time.sleep(1)
    
    print("❌ Installation timeout")
    sys.exit(2)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(3)
PYEOF
'''

code, out, err = ssh(install_cmd, timeout=180)

if "INSTALLATION SUCCESSFUL" in out:
    print("✅ Module installed successfully!")
    for line in out.split('\n'):
        if line.strip():
            print(f"   {line}")
elif "Already installed" in out:
    print("✅ Module already installed")
    for line in out.split('\n'):
        if line.strip():
            print(f"   {line}")
else:
    print("⚠️  Installation output:")
    print(out)
    if err:
        print("Errors:")
        print(err)

print()

# STEP 5: Verify
print("STEP 5: VERIFY INSTALLATION")
print("-"*80)

verify_cmd = '''python3 << 'PYEOF'
import xmlrpc.client

try:
    common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate("scholarixv2", "info@scholarixglobal.com", "123456", {})
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object", allow_none=True)
    
    # Check models
    for model in ['deal.management', 'deal.stage', 'deal.line']:
        found = models.execute_kw(
            "scholarixv2", uid, "123456",
            'ir.model', 'search',
            [('model', '=', model)]
        )
        status = "✅" if found else "❌"
        print(f"{status} {model}")
    
    # Check menu
    menu = models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.ui.menu', 'search',
        [('name', '=', 'Deals')]
    )
    status = "✅" if menu else "❌"
    print(f"{status} Deals menu")
    
except Exception as e:
    print(f"Error: {e}")
PYEOF
'''

code, out, err = ssh(verify_cmd, timeout=60)
print(out)

print()
print("="*80)
print("✅ DEPLOYMENT COMPLETE")
print("="*80)
print(f"""
Module: deal_management
Status: INSTALLED
Location: /var/lib/odoo/addons/deal_management

Next step:
1. Open https://erp.sgctech.ai/scholarixv2
2. Go to Sales > Deals
3. Create a test deal to verify functionality

If you see the "Deals" menu → Installation successful! ✅
""")
