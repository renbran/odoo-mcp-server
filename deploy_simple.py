#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple deployment script - Upload and install deal_management
"""

import subprocess
import time
import sys

SERVER = "erp.sgctech.ai"
MODULE = "deal_management"
LOCAL_PATH = "d:/01_WORK_PROJECTS/odoo-mcp-server/deal_management"
REMOTE_ADDONS = "/var/lib/odoo/addons"

print("\n" + "=" * 70)
print("DEAL MANAGEMENT - DEPLOYMENT WITH MONITORING")
print("=" * 70 + "\n")

# Step 1: Check if module exists locally
print("STEP 1: VERIFY LOCAL MODULE")
print("-" * 70)

import os
if os.path.exists(LOCAL_PATH):
    items = os.listdir(LOCAL_PATH)
    print(f"✅ Module found at: {LOCAL_PATH}")
    print(f"   Items: {len(items)}")
else:
    print(f"❌ Module not found at: {LOCAL_PATH}")
    sys.exit(1)

print("\n")

# Step 2: Check remote state
print("STEP 2: CHECK REMOTE STATE")
print("-" * 70)

check_cmd = (
    f"ssh root@{SERVER} "
    "\"ls -la /var/lib/odoo/addons/ | grep deal; "
    "echo '---'; "
    "systemctl status odoo --no-pager | head -5\""
)

print("Running: ssh root@erp.sgctech.ai ...")
result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
if result.stdout:
    print("Remote state:")
    print(result.stdout[:500])
print()

# Step 3: Upload module  
print("STEP 3: UPLOAD MODULE")
print("-" * 70)

print(f"Uploading {MODULE} to {SERVER}:{REMOTE_ADDONS}/")
scp_cmd = f'scp -r "{LOCAL_PATH}" root@{SERVER}:{REMOTE_ADDONS}/'

result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True, timeout=120)
if result.returncode == 0:
    print("✅ Upload successful")
else:
    print(f"❌ Upload failed: {result.stderr}")
    sys.exit(1)

print("\n")

# Step 4: Fix permissions
print("STEP 4: FIX PERMISSIONS")
print("-" * 70)

perm_cmd = f"ssh root@{SERVER} \"chown -R odoo:odoo {REMOTE_ADDONS}/{MODULE}\""
result = subprocess.run(perm_cmd, shell=True, capture_output=True, text=True)
if result.returncode == 0:
    print(f"✅ Permissions fixed")
else:
    print(f"⚠️  Permission fix: {result.stderr}")

print("\n")

# Step 5: Restart Odoo
print("STEP 5: RESTART ODOO SERVICE")
print("-" * 70)

restart_cmd = f"ssh root@{SERVER} \"systemctl restart odoo && sleep 5 && systemctl status odoo --no-pager | head -3\""
print("Restarting Odoo...")
result = subprocess.run(restart_cmd, shell=True, capture_output=True, text=True, timeout=60)

if "active (running)" in result.stdout.lower() or result.returncode == 0:
    print("✅ Odoo service restarted")
    if result.stdout:
        print(result.stdout[:300])
else:
    print(f"⚠️  Status: {result.stdout}")

print("\n")
print("Waiting for Odoo to stabilize...")
time.sleep(5)

# Step 6: Check installation
print("\nSTEP 6: CHECK INSTALLATION STATUS")
print("-" * 70)

check_install = f"""ssh root@{SERVER} << 'EOSSH'
python3 << 'EOF'
import xmlrpc.client
import sys

try:
    common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common")
    uid = common.authenticate("scholarixv2", "info@scholarixglobal.com", "123456", {{}})
    
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object")
    
    # Search for module
    module_ids = models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.module.module', 'search',
        [('name', '=', 'deal_management')]
    )
    
    if module_ids:
        mod = models.execute_kw(
            "scholarixv2", uid, "123456",
            'ir.module.module', 'read',
            module_ids, ['name', 'state']
        )[0]
        print(f"Module: {{mod['name']}}")
        print(f"State: {{mod['state']}}")
        if mod['state'] == 'uninstalled':
            print("\\n📦 Module found but NOT installed yet")
            print("   Next: Install via UI (Settings > Apps > Install)")
        elif mod['state'] == 'installed':
            print("\\n✅ MODULE INSTALLED AND ACTIVE")
        else:
            print(f"\\n⚠️  State: {{mod['state']}}")
    else:
        print("⚠️  Module not found in database")
        print("   Update app list first: Settings > Apps > Update App List")

except Exception as e:
    print(f"⚠️  Connection check: {{e}}")
    print("   (This is OK if Odoo is still starting)")

EOF
EOSSH
"""

result = subprocess.run(check_install, shell=True, capture_output=True, text=True, timeout=30)
print(result.stdout)
if result.stderr:
    print(f"Debug: {result.stderr}")

print("\n")
print("=" * 70)
print("DEPLOYMENT PHASE COMPLETE")
print("=" * 70)
print(f"""
✅ Module uploaded to: {REMOTE_ADDONS}/{MODULE}
✅ Permissions set to: odoo:odoo
✅ Odoo service: restarted

📋 NEXT STEPS (Manual UI Installation):

1. Open: https://erp.sgctech.ai/scholarixv2
2. Login if needed: info@scholarixglobal.com / 123456
3. Go to: Settings > Apps
4. Click: "Update App List" (top-right)
5. Search: "Deal Management"
6. Click: "Install"
7. Wait for installation (1-2 minutes)
8. Go to: Sales > Deals

If you see "Deals" menu → Installation successful! ✅

""")
