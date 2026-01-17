#!/bin/bash
# Verify current module state

MODULE_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management"
MENU_FILE="$MODULE_PATH/views/deals_menu.xml"

echo "================================================================================"
echo "VERIFICATION CHECK"
echo "================================================================================"
echo ""

echo "1. File exists?"
if [ -f "$MENU_FILE" ]; then
    echo "   ✓ Yes"
else
    echo "   ✗ No - File not found!"
    exit 1
fi
echo ""

echo "2. Line count:"
LINES=$(wc -l < "$MENU_FILE")
echo "   $LINES lines"
echo ""

echo "3. Line 67 content:"
sed -n '67p' "$MENU_FILE"
echo ""

echo "4. Check for bad references:"
if grep -q "menu_deals_projects\|action_deals_projects" "$MENU_FILE"; then
    echo "   ✗ FOUND BAD REFERENCES:"
    grep -n "menu_deals_projects\|action_deals_projects" "$MENU_FILE"
else
    echo "   ✓ CLEAN - No bad references found"
fi
echo ""

echo "================================================================================"
echo "DECISION"
echo "================================================================================"
echo ""

if ! grep -q "menu_deals_projects\|action_deals_projects" "$MENU_FILE" && [ "$LINES" -ge 98 ]; then
    echo "✓ MODULE IS READY FOR INSTALLATION"
    echo ""
    echo "Next steps:"
    echo "1. Login to Odoo: https://erp.sgctech.ai"
    echo "2. Go to Apps"
    echo "3. Update Apps List"
    echo "4. Search for 'Deals Management'"
    echo "5. Click Install"
else
    echo "⚠ MODULE NEEDS MORE FIXING"
    echo ""
    echo "Run this to clean the database and restart:"
    echo "sudo -u postgres psql scholarixv2 -c \"DELETE FROM ir_model_data WHERE module = 'deals_management';\""
    echo "sudo systemctl restart odoo"
fi
echo ""
