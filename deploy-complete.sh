#!/bin/bash
# Complete deployment - handles all folders properly

ADDONS_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
MODULE_PATH="$ADDONS_PATH/deals_management"
ZIP_FILE="/tmp/deals_management.zip"
DB_NAME="scholarixv2"

echo "================================================================================"
echo "COMPLETE DEPLOYMENT WITH FOLDER FIX"
echo "================================================================================"
echo ""

# Check ZIP exists
if [ ! -f "$ZIP_FILE" ]; then
    echo "ERROR: $ZIP_FILE not found"
    exit 1
fi

echo "[1/6] Deleting old module..."
sudo rm -rf "$MODULE_PATH"
echo "✓ Done"
echo ""

echo "[2/6] Extracting ZIP..."
# Extract directly to the target location
cd "$ADDONS_PATH"
sudo unzip -q -o "$ZIP_FILE"

# Check if structure is correct
if [ -d "deals_management/security" ]; then
    echo "✓ Correct structure"
elif [ -d "security" ]; then
    echo "⚠ Files extracted to wrong location, moving..."
    sudo mkdir -p deals_management
    sudo mv * deals_management/ 2>/dev/null || true
fi
echo ""

echo "[3/6] Setting permissions..."
sudo chown -R odoo:odoo "$MODULE_PATH"
sudo chmod -R 755 "$MODULE_PATH"
echo "✓ Done"
echo ""

echo "[4/6] Verifying files..."
echo "Module structure:"
sudo ls -la "$MODULE_PATH/"
echo ""

if [ -f "$MODULE_PATH/security/ir.model.access.csv" ]; then
    echo "✓ Security file found"
else
    echo "✗ ERROR: Security file missing!"
    echo "Files in module:"
    find "$MODULE_PATH" -type f
    exit 1
fi
echo ""

echo "[5/6] Cleaning database..."
sudo -u postgres psql "$DB_NAME" << 'EOSQL'
DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu');
DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window');
DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view');
DELETE FROM ir_model_data WHERE module = 'deals_management';
UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';
EOSQL
echo "✓ Done"
echo ""

echo "[6/6] Restarting Odoo..."
sudo systemctl restart odoo
sleep 5
echo "✓ Done"
echo ""

echo "================================================================================"
echo "DEPLOYMENT COMPLETE!"
echo "================================================================================"
echo ""
echo "Next: Try installing in Odoo UI"
echo ""
