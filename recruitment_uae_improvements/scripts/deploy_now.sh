#!/bin/bash
# RECRUITMENT UAE - AUTOMATED DEPLOYMENT SCRIPT
# Purpose: Transfer files and run diagnostic in one command
# Usage: bash deploy_now.sh <remote_user> <remote_host> <db_name>

set -e

# Default values
REMOTE_USER="${1:-odoo}"
REMOTE_HOST="${2:-eigermarvelhr.com}"
DB_NAME="${3:-eigermarvel}"
EXTRA_ADDONS="/var/odoo/${DB_NAME}/extra-addons"

echo "================================================================================"
echo "🚀 RECRUITMENT UAE MODULE - AUTOMATED DEPLOYMENT"
echo "================================================================================"
echo "Remote User:   $REMOTE_USER"
echo "Remote Host:   $REMOTE_HOST"
echo "Database:      $DB_NAME"
echo "Extra Addons:  $EXTRA_ADDONS"
echo ""

# Verify we have SSH access
echo "Testing SSH connection..."
if ! ssh -q -o ConnectTimeout=5 $REMOTE_USER@$REMOTE_HOST "exit" 2>/dev/null; then
    echo "❌ Cannot connect to $REMOTE_HOST"
    echo "   Please check:"
    echo "   - SSH is working: ssh $REMOTE_USER@$REMOTE_HOST"
    echo "   - User/host are correct"
    echo "   - You have SSH key/password configured"
    exit 1
fi
echo "✅ SSH connection successful"
echo ""

# Step 1: Create backup on server
echo "================================================================================"
echo "STEP 1: CREATE BACKUPS"
echo "================================================================================"
ssh $REMOTE_USER@$REMOTE_HOST << 'BACKUP_SCRIPT'
MODULE_DIR=$(find /var/odoo/eigermarvel/extra-addons -maxdepth 2 -type d -name "recruitment_uae" 2>/dev/null | head -1)
if [ -z "$MODULE_DIR" ]; then
    echo "❌ Module not found!"
    exit 1
fi

echo "Found module at: $MODULE_DIR"

# Create backup
BACKUP_DIR="${MODULE_DIR}_backup_$(date +%s)"
cp -r "$MODULE_DIR" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

# List backup contents
echo "Backup contents:"
ls -la "$BACKUP_DIR" | head -10
BACKUP_SCRIPT

echo ""

# Step 2: Transfer files
echo "================================================================================"
echo "STEP 2: TRANSFER FILES"
echo "================================================================================"
echo "Transferring models..."
scp -q -r models/ $REMOTE_USER@$REMOTE_HOST:$EXTRA_ADDONS/recruitment_uae/models/ && echo "✅ models/ transferred"

echo "Transferring views..."
scp -q -r views/ $REMOTE_USER@$REMOTE_HOST:$EXTRA_ADDONS/recruitment_uae/views/ && echo "✅ views/ transferred"

echo "Transferring data..."
scp -q -r data/ $REMOTE_USER@$REMOTE_HOST:$EXTRA_ADDONS/recruitment_uae/data/ && echo "✅ data/ transferred"

echo "Transferring security..."
scp -q -r security/ $REMOTE_USER@$REMOTE_HOST:$EXTRA_ADDONS/recruitment_uae/security/ && echo "✅ security/ transferred"

echo "Transferring manifest..."
scp -q __manifest__.py $REMOTE_USER@$REMOTE_HOST:$EXTRA_ADDONS/recruitment_uae/ && echo "✅ __manifest__.py transferred"

echo "Transferring init..."
scp -q __init__.py $REMOTE_USER@$REMOTE_HOST:$EXTRA_ADDONS/recruitment_uae/ && echo "✅ __init__.py transferred"

echo ""

# Step 3: Validate files
echo "================================================================================"
echo "STEP 3: VALIDATE FILES ON SERVER"
echo "================================================================================"
ssh $REMOTE_USER@$REMOTE_HOST << 'VALIDATE_SCRIPT'
cd /var/odoo/eigermarvel/extra-addons/recruitment_uae

python3 << 'PYEOF'
import xml.etree.ElementTree as ET
import os

# Validate XML files
xml_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith('.xml'):
            xml_files.append(os.path.join(root, file))

print("Validating XML files...")
valid_count = 0
invalid_count = 0

for xml_file in sorted(xml_files):
    try:
        ET.parse(xml_file)
        print(f"  ✅ {xml_file}")
        valid_count += 1
    except ET.ParseError as e:
        print(f"  ❌ {xml_file}: {e}")
        invalid_count += 1

print("")
print(f"Results: {valid_count} valid, {invalid_count} invalid")

if invalid_count == 0:
    print("✅ ALL FILES ARE VALID")
    exit(0)
else:
    print("❌ SOME FILES HAVE ERRORS")
    exit(1)
PYEOF
VALIDATE_SCRIPT

echo ""

# Step 4: Restart Odoo
echo "================================================================================"
echo "STEP 4: RESTART ODOO SERVICE"
echo "================================================================================"
ssh $REMOTE_USER@$REMOTE_HOST << 'RESTART_SCRIPT'
echo "Stopping Odoo..."
sudo systemctl stop odoo
sleep 3

echo "Waiting for process to stop..."
sleep 7

if pgrep -x "odoo" > /dev/null; then
    echo "⚠️ Odoo still running, forcing..."
    sudo pkill -9 odoo
    sleep 2
fi

echo "✅ Odoo stopped"
echo ""

echo "Starting Odoo..."
sudo systemctl start odoo
echo "⏳ Waiting for startup (30 seconds)..."
sleep 30

if pgrep -x "odoo" > /dev/null; then
    echo "✅ Odoo started"
else
    echo "❌ Odoo failed to start!"
    exit 1
fi
RESTART_SCRIPT

echo ""

# Step 5: Check logs
echo "================================================================================"
echo "STEP 5: CHECK LOGS FOR ERRORS"
echo "================================================================================"
ssh $REMOTE_USER@$REMOTE_HOST << 'LOGS_SCRIPT'
echo "Checking for errors in logs..."
ERRORS=$(tail -100 /var/log/odoo/odoo.log | grep -i "error\|exception\|xmlparse" | wc -l)

if [ $ERRORS -gt 0 ]; then
    echo "⚠️ Found $ERRORS potential issues in logs:"
    tail -100 /var/log/odoo/odoo.log | grep -i "error\|exception\|xmlparse" | head -10
else
    echo "✅ No critical errors in logs"
fi

echo ""
echo "Recent recruitment module activity:"
tail -50 /var/log/odoo/odoo.log | grep -i "recruitment" | tail -5 || echo "No recent recruitment activity"
LOGS_SCRIPT

echo ""

# Step 6: Summary
echo "================================================================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "================================================================================"
echo ""
echo "Summary:"
echo "  ✅ Backup created on server"
echo "  ✅ All files transferred"
echo "  ✅ Files validated on server"
echo "  ✅ Odoo restarted"
echo "  ✅ Logs checked"
echo ""
echo "Next steps:"
echo "  1. Open Odoo UI: http://$REMOTE_HOST:8069"
echo "  2. Login as admin"
echo "  3. Go to Apps menu"
echo "  4. Search for 'recruitment_uae'"
echo "  5. Check if module is installed (green checkmark)"
echo "  6. Test views and features"
echo ""
echo "If issues occur:"
echo "  - Check /var/log/odoo/odoo.log for detailed errors"
echo "  - Run deploy_with_fix.sh if XML issues appear"
echo "  - Use rollback procedure if needed"
echo ""
echo "================================================================================"
