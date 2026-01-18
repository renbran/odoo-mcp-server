# DEAL MANAGEMENT - MANUAL INSTALLATION GUIDE
## Using Correct Odoo Paths

The module is ready. Since SSH is timing out, **you'll need to manually install it using the correct paths provided.**

---

## Server Information
```
Odoo Path: /var/odoo/scholarixv2
Source: /var/odoo/scholarixv2/src
Python: /var/odoo/scholarixv2/venv/bin/python3
Config: /var/odoo/scholarixv2/odoo.conf
Logs: /var/odoo/scholarixv2/logs
Database: scholarixv2
```

---

## Step 1: Copy Module to Server

### Option A: Using SFTP/WinSCP (If SSH still times out)
1. Open WinSCP
2. Host: erp.sgctech.ai, User: root
3. Navigate to: `/var/odoo/scholarixv2/src/addons/` (or find correct addons path)
4. Upload: `deal_management` folder
5. Right-click > Properties > Set permissions to 755

### Option B: Using SCP (When SSH works)
```bash
scp -r d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management root@erp.sgctech.ai:/var/odoo/scholarixv2/src/addons/
```

---

## Step 2: Set Permissions

```bash
ssh root@erp.sgctech.ai
chown -R odoo:odoo /var/odoo/scholarixv2/src/addons/deal_management
chmod -R 755 /var/odoo/scholarixv2/src/addons/deal_management
```

---

## Step 3: Update Odoo Module List

```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -u base
```

This will:
- Scan all addon directories
- Detect the new `deal_management` module
- Update the module registry
- Then exit

Wait for completion (2-5 minutes).

---

## Step 4: Install Module via Odoo Shell

```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 << 'EOF'
import xmlrpc.client

common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common")
uid = common.authenticate("scholarixv2", "info@scholarixglobal.com", "123456", {})

models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object")

# Update module list first
models.execute_kw(
    "scholarixv2", uid, "123456",
    'ir.module.module', 'update_list'
)

# Find module
module_ids = models.execute_kw(
    "scholarixv2", uid, "123456",
    'ir.module.module', 'search',
    [('name', '=', 'deal_management')]
)

if module_ids:
    print(f"Found module: {module_ids}")
    
    # Install
    models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.module.module', 'button_install',
        module_ids
    )
    print("Installation started")
    
    # Monitor
    import time
    for i in range(120):
        state = models.execute_kw(
            "scholarixv2", uid, "123456",
            'ir.module.module', 'read',
            module_ids, ['state']
        )[0]['state']
        
        if state == 'installed':
            print("✅ INSTALLED SUCCESSFULLY")
            break
        elif state == 'failed':
            print("❌ Installation failed")
            break
        
        time.sleep(1)
        if i % 10 == 0:
            print(f"  [{i}] {state}")
else:
    print("Module not found - run update step first")
    
EOF
```

---

## Step 5: Verify Installation

### Check Module State
```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 << 'EOF'
import xmlrpc.client

common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common")
uid = common.authenticate("scholarixv2", "info@scholarixglobal.com", "123456", {})

models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object")

# Check models
print("Models:")
for model in ['deal.management', 'deal.stage', 'deal.line']:
    found = models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.model', 'search',
        [('model', '=', model)]
    )
    status = "✅" if found else "❌"
    print(f"  {status} {model}")

# Check menu
print("\nMenu:")
menu = models.execute_kw(
    "scholarixv2", uid, "123456",
    'ir.ui.menu', 'search',
    [('name', '=', 'Deals')]
)
status = "✅" if menu else "❌"
print(f"  {status} Deals menu")

EOF
```

### Check Logs
```bash
tail -50 /var/odoo/scholarixv2/logs/odoo.log | grep -i "deal"
```

---

## Step 6: Verify in Web UI

1. Open https://erp.sgctech.ai/scholarixv2
2. Login: info@scholarixglobal.com / 123456
3. Go to **Sales** menu
4. Look for **Deals** submenu
5. Click **All Deals** to open the list view

If you see the menu → **Installation successful!** ✅

---

## Troubleshooting

### Module doesn't appear in module list?
```bash
# Force rescan
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init
```

### Import errors?
```bash
# Check Python syntax
python3 -m py_compile /var/odoo/scholarixv2/src/addons/deal_management/__manifest__.py
python3 -m py_compile /var/odoo/scholarixv2/src/addons/deal_management/models/*.py
```

### Permission issues?
```bash
chown -R odoo:odoo /var/odoo/scholarixv2/src/addons/deal_management
chmod -R 755 /var/odoo/scholarixv2/src/addons/deal_management
```

### Check Odoo logs?
```bash
tail -100 /var/odoo/scholarixv2/logs/odoo.log
grep "ERROR" /var/odoo/scholarixv2/logs/odoo.log | tail -20
```

### Verify Odoo is running?
```bash
ps aux | grep odoo-bin
netstat -tlnp | grep 8069
```

---

## What Gets Installed

### 3 Models Created
- `deal.stage` - Workflow stages
- `deal.management` - Main deal model
- `deal.line` - Deal line items

### 3 Database Tables
- `deal_stage`
- `deal_management`
- `deal_line`

### 1 Sequence
- `deal.management` - For reference numbering

### 6 Workflow Stages
- Draft
- Qualification
- Proposal
- Negotiation
- Won
- Lost

### Menu Items
- Sales > Deals
  - All Deals
  - Pipeline
  - Stages (managers only)

---

## Important Notes

⚠️ **Only ONE version allowed:**
- Before installing, check if deal_management exists:
  ```bash
  find /var/odoo/scholarixv2 -name deal_management -type d
  ```
- If found, delete the old version:
  ```bash
  rm -rf /var/odoo/scholarixv2/src/addons/deal_management
  ```

✅ **After installation:**
- Module is in the database
- Cannot be removed from filesystem without uninstalling first
- To uninstall: Go to Settings > Apps > Deal Management > Uninstall

---

## Manual Step-by-Step Timeline

| Step | Time |
|------|------|
| Copy module to server | 2-5 min |
| Set permissions | 1 min |
| Update module list | 2-5 min |
| Install via Odoo | 3-5 min |
| Verify | 1 min |
| **Total** | **10-20 min** |

---

## The Module is Ready

**18 Files:** All built and tested
**Location:** `d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management\`
**Next:** Copy to `/var/odoo/scholarixv2/src/addons/deal_management/`

Your module is ready to go!
