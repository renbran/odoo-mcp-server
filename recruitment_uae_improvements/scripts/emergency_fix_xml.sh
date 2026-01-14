#!/bin/bash
# EMERGENCY FIX - application_views.xml XML Parsing Error
# This script fixes the XML parsing error and redeploys

set -e

REMOTE_USER="${1:-odoo}"
REMOTE_HOST="${2:-eigermarvelhr.com}"
DB_NAME="${3:-eigermarvel}"
MODULE_PATH="/var/odoo/${DB_NAME}/extra-addons/recruitment_uae"

echo "================================================================================"
echo "🚨 EMERGENCY FIX - XML Parsing Error in application_views.xml"
echo "================================================================================"
echo ""
echo "The error: xmlParseEntityRef: no name"
echo "Cause: Unescaped special characters in XML"
echo "Solution: Replace with clean, simple views"
echo ""

# Step 1: Create backup
echo "Step 1: Creating backup..."
ssh $REMOTE_USER@$REMOTE_HOST << 'BACKUP'
MODULE_PATH="/var/odoo/eigermarvel/extra-addons/recruitment_uae"
BACKUP_DIR="${MODULE_PATH}_emergency_backup_$(date +%s)"
cp -r "$MODULE_PATH" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"
BACKUP

echo ""
echo "Step 2: Replacing application_views.xml with clean version..."

# Step 2: Replace the broken file with fixed version
scp recruitment_uae_improvements/views/recruitment_application_views.xml \
    $REMOTE_USER@$REMOTE_HOST:$MODULE_PATH/views/ 2>/dev/null && echo "✅ File replaced"

echo ""
echo "Step 3: Validating XML on server..."

# Step 3: Validate
ssh $REMOTE_USER@$REMOTE_HOST << 'VALIDATE'
MODULE_PATH="/var/odoo/eigermarvel/extra-addons/recruitment_uae"
python3 << 'PYEOF'
import xml.etree.ElementTree as ET

try:
    ET.parse('$MODULE_PATH/views/recruitment_application_views.xml')
    print("✅ application_views.xml is now VALID")
except ET.ParseError as e:
    print(f"❌ Still has errors: {e}")
    exit(1)
PYEOF
VALIDATE

echo ""
echo "Step 4: Restarting Odoo..."

# Step 4: Restart Odoo
ssh $REMOTE_USER@$REMOTE_HOST << 'RESTART'
echo "Stopping Odoo..."
sudo systemctl stop odoo
sleep 5

echo "Starting Odoo..."
sudo systemctl start odoo
echo "⏳ Waiting 30 seconds..."
sleep 30

if pgrep -x "odoo" > /dev/null; then
    echo "✅ Odoo started successfully"
else
    echo "❌ Odoo failed to start"
    exit 1
fi
RESTART

echo ""
echo "Step 5: Checking logs..."

# Step 5: Check logs
ssh $REMOTE_USER@$REMOTE_HOST << 'LOGS'
echo "Checking for recruitment module errors..."
ERRORS=$(tail -100 /var/log/odoo/odoo.log | grep -i "xmlparse\|application_views" | wc -l)
if [ $ERRORS -gt 0 ]; then
    echo "⚠️ Found XML-related messages:"
    tail -100 /var/log/odoo/odoo.log | grep -i "xmlparse\|application_views" | head -10
else
    echo "✅ No XML parsing errors found"
fi

# Check if module loaded
if tail -50 /var/log/odoo/odoo.log | grep -i "recruitment_uae" | grep -i "loaded\|installed" > /dev/null; then
    echo "✅ recruitment_uae module loaded successfully"
else
    echo "⚠️ Check if recruitment_uae module loaded"
fi
LOGS

echo ""
echo "================================================================================"
echo "✅ EMERGENCY FIX COMPLETE"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "  1. Open Odoo: http://$REMOTE_HOST:8069"
echo "  2. Go to Apps → Search 'recruitment_uae'"
echo "  3. Check if module is installed (should show green checkmark)"
echo "  4. Test views load without errors"
echo ""
echo "If issues persist:"
echo "  - Check logs: tail -100 /var/log/odoo/odoo.log | grep -i error"
echo "  - Rollback: Use the backup directory created"
echo ""
