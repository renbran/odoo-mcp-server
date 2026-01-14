#!/bin/bash
# ============================================================================
# DIAGNOSTIC SCRIPT - Analyze XML Error on Server
# ============================================================================
# This script helps identify exactly what's wrong with the deployed files

REMOTE_USER="${1:-odoo}"
REMOTE_HOST="${2:-eigermarvelhr.com}"
DB_NAME="${3:-eigermarvel}"
MODULE_PATH="/var/odoo/${DB_NAME}/extra-addons/recruitment_uae"

echo ""
echo "================================================================================"
echo "📊 DIAGNOSTIC REPORT - recruitment_uae Module"
echo "================================================================================"
echo ""
echo "Server: ${REMOTE_USER}@${REMOTE_HOST}"
echo "Database: ${DB_NAME}"
echo "Module Path: ${MODULE_PATH}"
echo ""

# Check 1: Module exists on server
echo "🔍 Check 1: Module exists on server?"
ssh $REMOTE_USER@$REMOTE_HOST "test -d $MODULE_PATH && echo '✅ YES' || echo '❌ NO'" 2>/dev/null

echo ""

# Check 2: View files exist
echo "🔍 Check 2: View files on server?"
ssh $REMOTE_USER@$REMOTE_HOST "ls -1 $MODULE_PATH/views/*.xml 2>/dev/null | wc -l | xargs echo 'Found' && echo 'files'" 2>/dev/null

echo ""

# Check 3: Check manifest
echo "🔍 Check 3: __manifest__.py version?"
ssh $REMOTE_USER@$REMOTE_HOST "grep -o \"'version': '[^']*'\" $MODULE_PATH/__manifest__.py | head -1" 2>/dev/null

echo ""

# Check 4: Parse each view file
echo "🔍 Check 4: XML parsing test for each view file?"
ssh $REMOTE_USER@$REMOTE_HOST << 'PYEOF'
import xml.etree.ElementTree as ET
import os
import glob

module_path = "/var/odoo/eigermarvel/extra-addons/recruitment_uae"
os.chdir(module_path)

view_files = glob.glob("views/*.xml")
for file in sorted(view_files):
    try:
        ET.parse(file)
        print(f"   ✅ {file}")
    except ET.ParseError as e:
        print(f"   ❌ {file}")
        print(f"      Error: {e}")
PYEOF

echo ""

# Check 5: Odoo service status
echo "🔍 Check 5: Odoo service status?"
ssh $REMOTE_USER@$REMOTE_HOST "pgrep -x odoo > /dev/null && echo '✅ Running' || echo '❌ Not running'" 2>/dev/null

echo ""

# Check 6: Recent errors in logs
echo "🔍 Check 6: Recent errors in Odoo logs?"
ssh $REMOTE_USER@$REMOTE_HOST << 'LOGS'
ERRORS=$(tail -200 /var/log/odoo/odoo.log | grep -i "error\|critical" | wc -l)
if [ $ERRORS -gt 0 ]; then
    echo "   Found $ERRORS error(s):"
    tail -200 /var/log/odoo/odoo.log | grep -i "error\|critical" | head -5
else
    echo "   ✅ No critical errors"
fi
LOGS

echo ""

# Check 7: Module database state
echo "🔍 Check 7: Module state in database?"
ssh $REMOTE_USER@$REMOTE_HOST << 'DBCHECK'
STATE=$(sudo psql -U odoo eigermarvel -t -c "SELECT state FROM ir_module_module WHERE name = 'recruitment_uae';" 2>/dev/null | tr -d ' ')

if [ -z "$STATE" ]; then
    echo "   ⚠️  Module not in database (needs upload)"
elif [ "$STATE" = "installed" ]; then
    echo "   ✅ Module is INSTALLED"
elif [ "$STATE" = "to install" ]; then
    echo "   ℹ️  Module is 'to install' - needs installation click in UI"
else
    echo "   ℹ️  Module state: $STATE"
fi
DBCHECK

echo ""

# Check 8: Compare local vs server files (first 50 lines)
echo "🔍 Check 8: Local vs Server file comparison?"
echo "   This would require more detailed analysis..."

echo ""
echo "================================================================================"
echo "📊 END DIAGNOSTIC REPORT"
echo "================================================================================"
echo ""
echo "🔧 Interpretation:"
echo "   - If any view file shows ❌: Run the emergency_fix_complete.sh script"
echo "   - If Odoo shows ❌ Not running: Check logs for startup errors"
echo "   - If module is 'to install': Click Install in Odoo Apps UI"
echo "   - If all checks ✅: Module should be working!"
echo ""
