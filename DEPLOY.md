# Deploy Deals Management Module - Quick Start

## Option 1: Using Automated PowerShell Script (RECOMMENDED)

### Prerequisites
- Windows with PowerShell
- SSH access to server (password or key-based)
- `scp` and `ssh` commands available (comes with Git for Windows, or install OpenSSH)

### Usage

**With SSH Key (Recommended):**
```powershell
.\deploy-deals-module.ps1 -ServerHost "your-server.com" -ServerUser "your-username" -SshKeyPath "C:\path\to\your\key.pem"
```

**With Password (Interactive):**
```powershell
.\deploy-deals-module.ps1 -ServerHost "your-server.com" -ServerUser "your-username"
```

**With Password (Non-Interactive - requires PuTTY tools):**
```powershell
.\deploy-deals-module.ps1 -ServerHost "your-server.com" -ServerUser "your-username" -ServerPassword "your-password"
```

### Example
```powershell
cd D:\01_WORK_PROJECTS\odoo-mcp-server
.\deploy-deals-module.ps1 -ServerHost "erp.sgctech.ai" -ServerUser "root" -SshKeyPath "C:\Users\branm\.ssh\id_rsa"
```

---

## Option 2: Manual Step-by-Step

### Step 1: Create ZIP (PowerShell)
```powershell
Compress-Archive -Path "D:\01_WORK_PROJECTS\odoo-mcp-server\deals_management\*" -DestinationPath "D:\deals_management.zip" -Force
```

### Step 2: Upload to Server
```powershell
scp D:\deals_management.zip your-user@your-server:/tmp/deals_management.zip
```

### Step 3: Execute on Server (SSH)
```bash
# Remove old module
sudo rm -rf /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management

# Extract new module
cd /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/
sudo unzip -o /tmp/deals_management.zip -d deals_management
sudo chown -R odoo:odoo deals_management
sudo chmod -R 755 deals_management

# Verify
wc -l /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management/views/deals_menu.xml
grep "menu_deals_projects\|action_deals_projects" /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management/views/deals_menu.xml || echo "✓ Clean"

# Clean database
sudo -u postgres psql scholarixv2 -c "DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu'); DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window'); DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view'); DELETE FROM ir_model_data WHERE module = 'deals_management'; UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';"

# Restart Odoo
sudo systemctl restart odoo
sudo systemctl status odoo
```

---

## Option 3: One-Line Deployment (Advanced)

**Create this file on your server:** `/tmp/deploy-deals.sh`

```bash
#!/bin/bash
set -e

MODULE_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deals_management"
ZIP_PATH="/tmp/deals_management.zip"
ADDONS_PATH="/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc"
DB_NAME="scholarixv2"

echo "Removing old module..."
sudo rm -rf $MODULE_PATH

echo "Extracting new module..."
cd $ADDONS_PATH
sudo unzip -o $ZIP_PATH -d deals_management
sudo chown -R odoo:odoo deals_management
sudo chmod -R 755 deals_management

echo "Verifying files..."
wc -l $MODULE_PATH/views/deals_menu.xml

echo "Cleaning database..."
sudo -u postgres psql $DB_NAME -c "DELETE FROM ir_ui_menu WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.menu'); DELETE FROM ir_act_window WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.actions.act_window'); DELETE FROM ir_ui_view WHERE id IN (SELECT res_id FROM ir_model_data WHERE module = 'deals_management' AND model = 'ir.ui.view'); DELETE FROM ir_model_data WHERE module = 'deals_management'; UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'deals_management';"

echo "Restarting Odoo..."
sudo systemctl restart odoo
sleep 5
sudo systemctl status odoo --no-pager | grep 'Active:'

echo "✓ Deployment complete!"
```

**Then from Windows:**
```powershell
# Upload ZIP
scp D:\deals_management.zip user@server:/tmp/

# Execute script
ssh user@server "bash /tmp/deploy-deals.sh"
```

---

## After Deployment

1. Wait 30 seconds for Odoo to fully restart
2. Login to Odoo: https://erp.sgctech.ai
3. Go to **Apps**
4. Remove all filters
5. Click **Update Apps List**
6. Search for **"Deals Management"**
7. Click **Install**

✅ **Module should install without errors!**
