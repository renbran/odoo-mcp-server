#!/bin/bash
# Deploy deal_management module to Odoo server

set -e

echo "=========================================="
echo "Deal Management Module Deployment Script"
echo "=========================================="
echo ""

# Configuration
SERVER_IP="erp.sgctech.ai"
ODOO_ADDONS_PATH="/var/lib/odoo/addons"
MODULE_NAME="deal_management"
MODULE_PATH="$(pwd)/$MODULE_NAME"

if [ ! -d "$MODULE_PATH" ]; then
    echo "❌ Error: $MODULE_NAME directory not found at $MODULE_PATH"
    exit 1
fi

echo "📦 Module found: $MODULE_NAME"
echo "📍 Source: $MODULE_PATH"
echo "🎯 Target server: $SERVER_IP"
echo "📁 Target path: $ODOO_ADDONS_PATH/$MODULE_NAME"
echo ""

# Step 1: Copy module to server
echo "📤 Uploading module to server..."
scp -r "$MODULE_PATH" root@"$SERVER_IP":"$ODOO_ADDONS_PATH/"

if [ $? -eq 0 ]; then
    echo "✅ Module uploaded successfully"
else
    echo "❌ Upload failed"
    exit 1
fi

echo ""

# Step 2: Fix permissions
echo "🔐 Fixing permissions..."
ssh root@"$SERVER_IP" "chown -R odoo:odoo $ODOO_ADDONS_PATH/$MODULE_NAME"

if [ $? -eq 0 ]; then
    echo "✅ Permissions fixed"
else
    echo "❌ Permission fix failed"
    exit 1
fi

echo ""

# Step 3: Restart Odoo
echo "🔄 Restarting Odoo service..."
ssh root@"$SERVER_IP" "systemctl restart odoo"

if [ $? -eq 0 ]; then
    echo "✅ Odoo restarted"
else
    echo "❌ Restart failed"
    exit 1
fi

echo ""

# Step 4: Verify
echo "✔️  Verifying installation..."
echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open https://$SERVER_IP/scholarixv2"
echo "2. Go to Settings > Apps"
echo "3. Click 'Update App List' (top-right)"
echo "4. Search for 'Deal Management'"
echo "5. Click Install"
echo ""
echo "After installation:"
echo "1. Go to Sales > Deals"
echo "2. Create a test deal"
echo "3. Test the workflow buttons"
echo ""
