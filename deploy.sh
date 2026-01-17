#!/bin/bash
# Deployment script - run on server

ADDONS_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
MODULE_PATH="$ADDONS_PATH/deals_management"
ZIP_FILE="/tmp/deals_management_deploy.zip"
DB_NAME="scholarixv2"

echo "================================================================================"
echo "DEPLOYING DEALS MANAGEMENT MODULE"
echo "================================================================================"
echo ""

echo "[STEP 1/5] Delete old module"
if [ -d "$MODULE_PATH" ]; then
    sudo rm -rf "$MODULE_PATH"
    echo "✓ Old module deleted"
else
    echo "ℹ Module not found (fresh install)"
fi
echo ""

echo "[STEP 2/5] Extract ZIP"
cd "$ADDONS_PATH"
sudo unzip -q -o "$ZIP_FILE" || sudo unzip -o "$ZIP_FILE"

if [ -d "deals_management" ] && [ -f "deals_management/security/ir.model.access.csv" ]; then
    echo "✓ Module extracted successfully"
else
    echo "✗ ERROR: Module extraction failed!"
    echo "Module contents:"
    ls -la deals_management/ 2>&1 | head -20
    exit 1
fi
echo ""

echo "[STEP 3/5] Set permissions"
sudo chown -R odoo:odoo deals_management
sudo chmod -R 755 deals_management
echo "✓ Permissions set"
echo ""

echo "[STEP 4/5] Clean database"
sudo -u postgres psql "$DB_NAME" << 'SQL' 2>&1 | tail -3
DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu');
DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window');
DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view');
DELETE FROM ir_model_data WHERE module = 'deals_management';
UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';
SQL
echo "✓ Database cleaned"
echo ""

echo "[STEP 5/5] Restart Odoo"
sudo systemctl restart odoo
sleep 3
echo "Waiting for Odoo to initialize..."
for i in 1 2 3 4 5; do
    if sudo systemctl is-active --quiet odoo; then
        echo "✓ Odoo is running"
        break
    fi
    sleep 2
done
echo ""

echo "================================================================================"
echo "DEPLOYMENT PHASE COMPLETE"
echo "================================================================================"
echo ""
echo "Monitoring Odoo logs for 15 seconds..."
sleep 15
echo ""
echo "Last 40 lines of Odoo log:"
tail -40 /var/odoo/scholarixv2/var/log/odoo.log
echo ""
echo "================================================================================"
echo "DEPLOYMENT STATUS"
echo "================================================================================"
echo ""

# Check for critical errors
if grep -i "ParseError\|deals_management.*error" /var/odoo/scholarixv2/var/log/odoo.log | tail -5; then
    echo ""
    echo "⚠ Errors detected - review above"
else
    echo "✓ No critical errors detected"
fi

echo ""
echo "File verification:"
for file in __manifest__.py security/ir.model.access.csv views/deals_menu.xml; do
    if [ -f "$MODULE_PATH/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ MISSING: $file"
    fi
done

echo ""
echo "Ready for installation in Odoo UI"
