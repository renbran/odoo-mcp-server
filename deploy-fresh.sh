#!/bin/bash
# ==============================================================================
# CRITICAL FIX: Completely clean and rebuild deals_management module
# ==============================================================================
set -e

ADDONS_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
MODULE_PATH="$ADDONS_PATH/deals_management"
DB_NAME="scholarixv2"
ZIP_FILE="/tmp/deals_management.zip"

echo "================================================================================"
echo "STEP 1: Verify ZIP exists"
echo "================================================================================"
if [ ! -f "$ZIP_FILE" ]; then
    echo "ERROR: $ZIP_FILE not found!"
    echo "Please upload the deals_management.zip file to /tmp/ first"
    exit 1
fi
echo "✓ ZIP file found"
echo ""

echo "================================================================================"
echo "STEP 2: Delete old module completely"
echo "================================================================================"
if [ -d "$MODULE_PATH" ]; then
    echo "Removing $MODULE_PATH..."
    sudo rm -rf "$MODULE_PATH"
    echo "✓ Old module deleted"
else
    echo "Module directory already gone"
fi
echo ""

echo "================================================================================"
echo "STEP 3: Extract fresh module from ZIP"
echo "================================================================================"
cd "$ADDONS_PATH"
echo "Extracting to $ADDONS_PATH..."
sudo unzip -o "$ZIP_FILE" -d deals_management
echo "✓ ZIP extracted"
echo ""

echo "================================================================================"
echo "STEP 4: Set correct permissions"
echo "================================================================================"
sudo chown -R odoo:odoo "$MODULE_PATH"
sudo chmod -R 755 "$MODULE_PATH"
echo "✓ Permissions set"
echo ""

echo "================================================================================"
echo "STEP 5: Verify files"
echo "================================================================================"
echo ""
echo "File structure:"
find "$MODULE_PATH" -type f -name "*.xml" -o -name "*.py" -o -name "*.csv" | sort
echo ""

MENU_FILE="$MODULE_PATH/views/deals_menu.xml"
echo "Checking $MENU_FILE..."
if [ ! -f "$MENU_FILE" ]; then
    echo "ERROR: deals_menu.xml not found!"
    exit 1
fi

LINES=$(wc -l < "$MENU_FILE")
echo "Line count: $LINES (expected 99)"

if [ "$LINES" -ne 99 ]; then
    echo "ERROR: Line count mismatch!"
    echo "Current: $LINES"
    echo "Expected: 99"
    echo ""
    echo "Line 67 content:"
    sed -n '67p' "$MENU_FILE"
    exit 1
fi

BAD_COUNT=$(grep -c "menu_deals_projects\|action_deals_projects" "$MENU_FILE" || true)
if [ $BAD_COUNT -eq 0 ]; then
    echo "✓ No bad references (clean!)"
else
    echo "ERROR: Found $BAD_COUNT bad references!"
    grep -n "menu_deals_projects\|action_deals_projects" "$MENU_FILE"
    exit 1
fi
echo ""

echo "================================================================================"
echo "STEP 6: Clean database cache"
echo "================================================================================"
echo "Deleting old module data from database..."
sudo -u postgres psql "$DB_NAME" << 'EOSQL'
DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu');
DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window');
DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view');
DELETE FROM ir_model_data WHERE module = 'deals_management';
UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';
EOSQL
echo "✓ Database cleaned"
echo ""

echo "================================================================================"
echo "STEP 7: Restart Odoo"
echo "================================================================================"
echo "Restarting Odoo service..."
sudo systemctl restart odoo
sleep 5
echo "Waiting for Odoo to stabilize..."
sleep 10
echo ""

ODOO_STATUS=$(sudo systemctl status odoo | grep 'Active:')
echo "Odoo status: $ODOO_STATUS"
echo ""

echo "================================================================================"
echo "✓ DEPLOYMENT COMPLETE!"
echo "================================================================================"
echo ""
echo "NEXT STEPS:"
echo "1. Wait 30 seconds for Odoo to fully start"
echo "2. Login to Odoo: https://erp.sgctech.ai"
echo "3. Go to Apps > Update Apps List"
echo "4. Search for 'Deals Management'"
echo "5. Click Install"
echo ""
echo "If you still get an error, check the Odoo logs:"
echo "  sudo tail -100 /var/odoo/scholarixv2/var/log/odoo.log"
echo ""
