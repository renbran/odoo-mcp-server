# MANUAL DEPLOYMENT - Run These Commands on Your Server

## Step 1: Upload the Module ZIP (on your Windows machine)

Use your preferred SFTP client (FileZilla, WinSCP, or Web UI) to upload:
```
D:\01_WORK_PROJECTS\odoo-mcp-server\deals_management.zip
```

To:
```
/tmp/deals_management.zip
```

---

## Step 2: Execute Deployment (SSH to your server)

Once uploaded, run these commands on your server:

```bash
# Set variables
ADDONS_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
MODULE_PATH="$ADDONS_PATH/deals_management"
ZIP_FILE="/tmp/deals_management.zip"
DB_NAME="scholarixv2"

echo "================================================================================"
echo "[STEP 1/5] Delete old module"
echo "================================================================================"
if [ -d "$MODULE_PATH" ]; then
    sudo rm -rf "$MODULE_PATH"
    echo "OK: Old module deleted"
else
    echo "INFO: Module not found (fresh install)"
fi
echo ""

echo "================================================================================"
echo "[STEP 2/5] Extract ZIP"
echo "================================================================================"
cd "$ADDONS_PATH"
echo "Current path: $(pwd)"
echo "Extracting: $ZIP_FILE"
sudo unzip -q -o "$ZIP_FILE" || sudo unzip -o "$ZIP_FILE"

if [ -d "deals_management" ] && [ -f "deals_management/security/ir.model.access.csv" ]; then
    echo "OK: Module extracted successfully"
    echo "Files in module:"
    ls -1 deals_management/
else
    echo "ERROR: Module extraction failed!"
    echo "Contents of current directory:"
    ls -la
    exit 1
fi
echo ""

echo "================================================================================"
echo "[STEP 3/5] Set permissions"
echo "================================================================================"
sudo chown -R odoo:odoo deals_management
sudo chmod -R 755 deals_management
echo "OK: Permissions set"
echo ""

echo "================================================================================"
echo "[STEP 4/5] Clean database cache"
echo "================================================================================"
sudo -u postgres psql "$DB_NAME" << 'SQL'
DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu');
DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window');
DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view');
DELETE FROM ir_model_data WHERE module = 'deals_management';
UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';
SQL
echo "OK: Database cleaned"
echo ""

echo "================================================================================"
echo "[STEP 5/5] Restart Odoo"
echo "================================================================================"
sudo systemctl restart odoo
sleep 3
echo "Waiting for Odoo to initialize..."
sleep 10

if sudo systemctl is-active --quiet odoo; then
    echo "OK: Odoo is running"
else
    echo "WARNING: Verify Odoo status:"
    sudo systemctl status odoo
fi
echo ""

echo "================================================================================"
echo "MONITORING LOGS (next 30 seconds)"
echo "================================================================================"
echo ""
echo "Tailing Odoo log..."
timeout 30 tail -f /var/odoo/scholarixv2/var/log/odoo.log || true
echo ""
echo "Last 50 lines of log:"
tail -50 /var/odoo/scholarixv2/var/log/odoo.log
echo ""

echo "================================================================================"
echo "VERIFICATION"
echo "================================================================================"
echo ""

# Verify files
echo "Critical files:"
for file in __manifest__.py security/ir.model.access.csv views/deals_menu.xml views/commission_views.xml models/sale_order_deals.py; do
    if [ -f "$MODULE_PATH/$file" ]; then
        echo "  OK: $file"
    else
        echo "  MISSING: $file"
    fi
done
echo ""

# Check for errors
echo "Checking for critical errors in log:"
if grep -i "deals_management.*error\|ParseError" /var/odoo/scholarixv2/var/log/odoo.log 2>&1 | tail -10; then
    echo ""
    echo "Errors found - review above"
else
    echo "  OK: No critical errors detected"
fi

echo ""
echo "================================================================================"
echo "DEPLOYMENT STATUS: COMPLETE"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "  1. Login to Odoo: https://erp.sgctech.ai"
echo "  2. Go to Apps > Update Apps List"
echo "  3. Search for 'Deals Management'"
echo "  4. Click Install"
echo ""
```

---

## Alternative: Copy-Paste Line by Line

If the above script has issues, run these commands individually:

```bash
# Remove old module
sudo rm -rf /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management

# Go to addons directory
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/

# Extract ZIP
sudo unzip -q -o /tmp/deals_management.zip

# Set ownership and permissions
sudo chown -R odoo:odoo deals_management
sudo chmod -R 755 deals_management

# Verify structure
ls -la deals_management/

# Clean database
sudo -u postgres psql scholarixv2 << 'END'
DELETE FROM ir_model_data WHERE module = 'deals_management';
UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';
END

# Restart Odoo
sudo systemctl restart odoo

# Wait and check
sleep 10
sudo systemctl status odoo

# Monitor logs
tail -100 /var/odoo/scholarixv2/var/log/odoo.log
```

---

## Troubleshooting

### If files are in wrong directory:
```bash
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/
ls -la
# If you see __manifest__.py, __init__.py in current dir (not in deals_management subdir):
mkdir -p deals_management
sudo mv __manifest__.py __init__.py models views security deals_management/ 2>/dev/null || true
```

### Check what's in the ZIP:
```bash
unzip -l /tmp/deals_management.zip | head -30
```

### Check Odoo status:
```bash
sudo systemctl status odoo
tail -200 /var/odoo/scholarixv2/var/log/odoo.log | grep -i error
```
