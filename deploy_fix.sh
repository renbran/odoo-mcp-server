#!/bin/bash
# Deploy and execute the comprehensive fix script

echo "========================================================================"
echo "OSUSPROPERTIES FIX DEPLOYMENT SCRIPT"
echo "========================================================================"

SERVER="odoo@104.207.139.132"
SCRIPT_NAME="fix_all_osusproperties_issues.py"
REMOTE_PATH="/tmp/$SCRIPT_NAME"

echo ""
echo "[1/4] Uploading fix script to server..."
scp "$SCRIPT_NAME" "$SERVER:$REMOTE_PATH"

if [ $? -ne 0 ]; then
    echo "✗ Failed to upload script"
    exit 1
fi

echo "✓ Script uploaded successfully"

echo ""
echo "[2/4] Making script executable..."
ssh "$SERVER" "chmod +x $REMOTE_PATH"

echo ""
echo "[3/4] Executing fix script..."
ssh "$SERVER" "python3 $REMOTE_PATH"

if [ $? -ne 0 ]; then
    echo "✗ Script execution failed"
    exit 1
fi

echo ""
echo "[4/4] Restarting Odoo service..."
ssh "$SERVER" "sudo systemctl restart odoo-osusproperties"

if [ $? -ne 0 ]; then
    echo "✗ Failed to restart Odoo service"
    exit 1
fi

echo "✓ Odoo service restarted"

echo ""
echo "========================================================================"
echo "MONITORING SERVICE STATUS..."
echo "========================================================================"

sleep 5

ssh "$SERVER" "sudo systemctl status odoo-osusproperties --no-pager"

echo ""
echo "========================================================================"
echo "CHECKING LOGS FOR ERRORS..."
echo "========================================================================"

ssh "$SERVER" "sudo tail -n 50 /var/odoo/osusproperties/logs/odoo-server.log | grep -i -E '(error|critical|warning)'"

echo ""
echo "========================================================================"
echo "DEPLOYMENT COMPLETE!"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "1. Monitor full logs: ssh $SERVER 'sudo tail -f /var/odoo/osusproperties/logs/odoo-server.log'"
echo "2. Test the application at http://104.207.139.132:8070"
echo "3. Verify no more 'user type' errors appear"
echo ""
