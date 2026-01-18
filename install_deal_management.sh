#!/bin/bash
# DEAL MANAGEMENT MODULE - INSTALLATION SCRIPT
# Execute this on the server as root

set -e

ODOO_PATH="/var/odoo/scholarixv2"
ADDONS_PATH="$ODOO_PATH/src/addons"
ODOO_BIN="$ODOO_PATH/venv/bin/python3"
ODOO_BINARY="$ODOO_PATH/src/odoo-bin"
CONFIG="$ODOO_PATH/odoo.conf"
DB="scholarixv2"
MODULE="deal_management"

echo "=========================================="
echo "DEAL MANAGEMENT MODULE INSTALLATION"
echo "=========================================="
echo ""

# Step 1: Check Odoo exists
echo "STEP 1: Verifying Odoo installation..."
if [ ! -d "$ODOO_PATH" ]; then
    echo "❌ ERROR: Odoo not found at $ODOO_PATH"
    exit 1
fi
echo "✅ Odoo found at $ODOO_PATH"
echo ""

# Step 2: Check if module exists in addons
if [ ! -d "$ADDONS_PATH/$MODULE" ]; then
    echo "❌ ERROR: Module not found at $ADDONS_PATH/$MODULE"
    echo "   Please upload the module first"
    exit 1
fi
echo "✅ Module found at $ADDONS_PATH/$MODULE"
echo ""

# Step 3: Fix permissions
echo "STEP 2: Setting permissions..."
chown -R odoo:odoo "$ADDONS_PATH/$MODULE"
chmod -R 755 "$ADDONS_PATH/$MODULE"
echo "✅ Permissions set"
echo ""

# Step 4: Update module list
echo "STEP 3: Updating module list..."
cd "$ODOO_PATH"
sudo -u odoo $ODOO_BIN $ODOO_BINARY -c $CONFIG --no-http --stop-after-init -u base 2>&1 | tail -10
echo "✅ Module list updated"
echo ""

# Step 5: Install via Odoo
echo "STEP 4: Installing module..."
cd "$ODOO_PATH"

sudo -u odoo python3 << 'PYEOF'
import xmlrpc.client
import time

try:
    common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common")
    uid = common.authenticate("scholarixv2", "info@scholarixglobal.com", "123456", {})
    
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object")
    
    # Update module list
    models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.module.module', 'update_list'
    )
    print("[1/3] Module list updated")
    
    # Find module
    module_ids = models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.module.module', 'search',
        [('name', '=', 'deal_management')]
    )
    
    if not module_ids:
        print("[2/3] ERROR: Module not found!")
        exit(1)
    
    print(f"[2/3] Found module ID: {module_ids[0]}")
    
    # Install
    models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.module.module', 'button_install',
        module_ids
    )
    print("[3/3] Installation started, monitoring...")
    
    # Monitor
    for i in range(120):
        state = models.execute_kw(
            "scholarixv2", uid, "123456",
            'ir.module.module', 'read',
            module_ids, ['state']
        )[0]['state']
        
        if state == 'installed':
            print("\n✅ INSTALLATION SUCCESSFUL!")
            break
        elif state == 'failed':
            print("\n❌ Installation failed")
            exit(1)
        
        if i % 10 == 0:
            print(f"  [{i:3d}] {state}")
        time.sleep(1)

except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)

PYEOF

echo ""

# Step 6: Verify
echo "STEP 5: Verifying installation..."
cd "$ODOO_PATH"

sudo -u odoo python3 << 'PYEOF'
import xmlrpc.client

try:
    common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common")
    uid = common.authenticate("scholarixv2", "info@scholarixglobal.com", "123456", {})
    models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object")
    
    print("Models created:")
    for model in ['deal.management', 'deal.stage', 'deal.line']:
        found = models.execute_kw(
            "scholarixv2", uid, "123456",
            'ir.model', 'search',
            [('model', '=', model)]
        )
        status = "✅" if found else "❌"
        print(f"  {status} {model}")
    
    print("\nMenu created:")
    menu = models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.ui.menu', 'search',
        [('name', '=', 'Deals')]
    )
    status = "✅" if menu else "❌"
    print(f"  {status} Deals menu")

except Exception as e:
    print(f"⚠️  Verification error: {e}")

PYEOF

echo ""
echo "=========================================="
echo "✅ INSTALLATION COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open https://erp.sgctech.ai/scholarixv2"
echo "2. Go to Sales > Deals"
echo "3. Create a test deal"
echo ""
echo "If you see the 'Deals' menu → Success! ✅"
