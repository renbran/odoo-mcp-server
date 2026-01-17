#!/bin/bash
# ==============================================================================
# CRITICAL FIX: Delete old file from server and verify
# ==============================================================================
set -e

MODULE_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management"
MENU_FILE="$MODULE_PATH/views/deals_menu.xml"

echo "================================================================================"
echo "DIAGNOSTIC: Check current server state"
echo "================================================================================"
echo ""

echo "1. Check if module directory exists:"
if [ -d "$MODULE_PATH" ]; then
    echo "   ✓ Directory exists"
    echo "   Contents:"
    ls -la "$MODULE_PATH"
else
    echo "   ✗ Directory does not exist"
    exit 1
fi
echo ""

echo "2. Check file size and line count:"
if [ -f "$MENU_FILE" ]; then
    SIZE=$(wc -c < "$MENU_FILE")
    LINES=$(wc -l < "$MENU_FILE")
    echo "   File size: $SIZE bytes"
    echo "   Line count: $LINES lines (expected 99)"
    echo ""
    echo "   Line 67 content:"
    sed -n '67p' "$MENU_FILE"
else
    echo "   ✗ File not found"
    exit 1
fi
echo ""

echo "3. Check for bad references:"
BAD_COUNT=$(grep -c "menu_deals_projects\|action_deals_projects" "$MENU_FILE" || true)
if [ $BAD_COUNT -eq 0 ]; then
    echo "   ✓ No bad references found"
else
    echo "   ✗ Found $BAD_COUNT bad references!"
    echo ""
    echo "   GREP RESULTS:"
    grep -n "menu_deals_projects\|action_deals_projects" "$MENU_FILE" || true
fi
echo ""

echo "================================================================================"
echo "NEXT STEPS:"
echo "================================================================================"
echo ""
echo "If line count is NOT 99, or line 67 shows the bad menu:"
echo ""
echo "OPTION A: Delete module completely and re-upload fresh"
echo "  1. sudo rm -rf /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management"
echo "  2. Upload new ZIP file"
echo "  3. cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/"
echo "  4. sudo unzip -o /tmp/deals_management.zip -d deals_management"
echo "  5. sudo chown -R odoo:odoo deals_management"
echo "  6. sudo chmod -R 755 deals_management"
echo ""
echo "OPTION B: Manually replace just the deals_menu.xml file"
echo "  (Requires uploading fresh file)"
echo ""
echo "If everything looks correct (99 lines, no bad refs):"
echo "  1. Clean database: See cleanup commands below"
echo "  2. Restart Odoo: sudo systemctl restart odoo"
echo "  3. Try installation again"
echo ""
echo "================================================================================"
echo "DATABASE CLEANUP COMMANDS (run if file is correct):"
echo "================================================================================"
echo ""
echo "sudo -u postgres psql scholarixv2 << 'EOF'
DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu');
DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window');
DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view');
DELETE FROM ir_model_data WHERE module = 'deals_management';
UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';
EOF"
echo ""
