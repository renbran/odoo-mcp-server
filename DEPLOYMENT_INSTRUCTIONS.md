# Deal Report Module Deployment Guide

## Current Status
❌ **Module Not Found on Remote Server**
- URL: https://erp.sgctech.ai
- Database: scholarixv2
- User: info@scholarixglobal.com (Authenticated ✅)
- Module: deal_report (Not in addons path)

## Test Results Summary
- ✅ 4/17 Tests Passed (Partner, Project, Product creation successful)
- ❌ 13/17 Tests Failed (Models not registered, views not loaded)
- Root Cause: Module not installed on remote instance

## Deployment Options

### Option 1: Copy Module to Server (SSH/SCP)
**Best for:** Direct access to server filesystem

```bash
# 1. Connect to server
ssh user@erp.sgctech.ai

# 2. Find Odoo addons directory
find /var -type d -name addons 2>/dev/null | grep odoo

# 3. Copy module
scp -r deal_report/ user@erp.sgctech.ai:/path/to/odoo/addons/

# 4. Restart Odoo
systemctl restart odoo
```

### Option 2: Install via Odoo UI (Web Interface)
**Best for:** No SSH access, using Odoo UI

1. Navigate to: **Apps** → **Update Apps List** (developer mode)
2. Search for: `deal_report`
3. Click **Install**
4. Confirm installation

**Note:** The module must already be in the addons path for this to work.

### Option 3: Use Odoo CLI Tools
**Best for:** Server access with command line

```bash
# On the Odoo server
cd /path/to/odoo-server

# 1. Find addons path
grep -i 'addons_path' /etc/odoo/odoo.conf

# 2. Copy module
cp -r /local/path/deal_report /var/lib/odoo/addons/

# 3. Update module list and install
python3 -m odoo.cli.shell -c /etc/odoo/odoo.conf \
  --database=scholarixv2 \
  --with-demo \
  -c << 'EOF'
env['ir.module.module'].update_list()
env['ir.module.module'].search([('name', '=', 'deal_report')]).button_install()
EOF

# 4. Restart
systemctl restart odoo
```

### Option 4: Use Wrangler/Docker (If Running in Container)
**Best for:** Docker-based deployments

```bash
# 1. Find docker container
docker ps | grep odoo

# 2. Copy module into container
docker cp deal_report/ <container_id>:/var/lib/odoo/addons/

# 3. Reload/restart
docker exec <container_id> service odoo restart
```

### Option 5: Via Python RPC + File Upload
**Best for:** No direct server access

```bash
# Upload module as ZIP and extract in Odoo
python deploy_deal_report_module.py --action install \
  --url https://erp.sgctech.ai \
  --db scholarixv2 \
  --email info@scholarixglobal.com \
  --password 123456
```

## Next Steps

### Step 1: Identify Server Setup
Check the server environment:
```bash
# SSH into server and run:
cat /etc/odoo/odoo.conf | grep addons_path
find /var -type d -name "*odoo*" -o -name "*addons*" 2>/dev/null
```

### Step 2: Deploy Module
Once you know the addons path, copy the `deal_report/` directory there.

### Step 3: Verify Installation
After restarting Odoo, run the test suite:
```bash
python run_odoo_tests.py \
  --url https://erp.sgctech.ai \
  --db scholarixv2 \
  --email info@scholarixglobal.com \
  --password 123456
```

## Module Contents
The `deal_report/` module includes:

```
deal_report/
├── __manifest__.py           # Module metadata
├── __init__.py              # Module initialization
├── models/
│   ├── deal_report.py       # Main deal model
│   ├── deal_commission_line.py
│   ├── deal_bill_line.py
│   └── __init__.py
├── views/
│   ├── deal_report_views.xml
│   ├── deal_commission_line_views.xml
│   ├── deal_bill_line_views.xml
│   └── deal_menu.xml
├── security/
│   ├── deal_report_security.xml
│   └── ir.model.access.csv
├── data/
│   ├── deal_sequence.xml
│   └── commission_product.xml
└── static/
    └── src/scss/deal_report.scss
```

## Module Dependencies
The module requires these Odoo modules to be installed first:
- base (always installed)
- sale_management
- account
- product
- contacts
- mail
- project

## Troubleshooting

### "Module not found in repository"
**Cause:** Module directory not in Odoo's addons path  
**Solution:** Copy `deal_report/` to the correct addons directory on server

### "Invalid field 'version' on model 'ir.module.module'"
**Cause:** Odoo version compatibility issue  
**Solution:** Use `state` field instead of `version` for module queries

### Models/Views still not registered after install
**Cause:** Module installed but not fully activated  
**Solution:** 
1. Restart Odoo: `systemctl restart odoo`
2. Clear browser cache
3. Hard refresh Odoo UI (Ctrl+Shift+R)

## Testing Checklist

After installation, verify:
- [ ] Module appears in **Apps** list
- [ ] Module status shows "Installed"
- [ ] No error messages in Odoo logs
- [ ] Test suite passes (see next section)

## Run Full Test Suite

```bash
python run_odoo_tests.py \
  --url https://erp.sgctech.ai \
  --db scholarixv2 \
  --email info@scholarixglobal.com \
  --password 123456
```

Expected result: **17/17 tests passing** ✅

## Support
If you need help with deployment:
1. Check server SSH access and permissions
2. Verify Odoo is running: `systemctl status odoo`
3. Check Odoo logs: `tail -f /var/log/odoo/odoo.log`
4. Run diagnostic: `python diagnose_odoo_connection.py`
