#!/bin/bash
# Complete deployment script with monitoring

SERVER="erp.sgctech.ai"
ODOO_ADDONS="/var/lib/odoo/addons"
EXTRA_ADDONS="/var/odoo/scholarixv2/extra-addons"
MODULE="deal_management"

echo "=========================================="
echo "DEAL MANAGEMENT DEPLOYMENT WITH MONITORING"
echo "=========================================="
echo ""

# Step 1: Check for existing modules
echo "STEP 1: CHECKING FOR EXISTING MODULES"
echo "------------------------------------------"

ssh root@"$SERVER" << 'EOSSH'
echo "Checking addon paths for deal_management..."
echo ""

# Check standard addons path
if [ -d /var/lib/odoo/addons/deal_management ]; then
    echo "✅ Found in /var/lib/odoo/addons/deal_management"
    echo "   Listing files:"
    ls -la /var/lib/odoo/addons/deal_management/ | head -10
else
    echo "❌ NOT in /var/lib/odoo/addons/deal_management"
fi

echo ""

# Check extra addons path
if [ -d /var/odoo/scholarixv2/extra-addons/deal_management ]; then
    echo "✅ Found in /var/odoo/scholarixv2/extra-addons/deal_management"
    echo "   Listing files:"
    ls -la /var/odoo/scholarixv2/extra-addons/deal_management/ | head -10
else
    echo "❌ NOT in /var/odoo/scholarixv2/extra-addons/deal_management"
fi

echo ""

# Check odooapps.git path
ODOOAPPS_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
if [ -d "$ODOOAPPS_PATH/deal_management" ]; then
    echo "✅ Found in $ODOOAPPS_PATH/deal_management"
    echo "   Listing files:"
    ls -la "$ODOOAPPS_PATH/deal_management/" | head -10
else
    echo "❌ NOT in $ODOOAPPS_PATH/deal_management"
fi

EOSSH

echo ""
