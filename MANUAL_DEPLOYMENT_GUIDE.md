# DEAL MANAGEMENT MODULE - MANUAL DEPLOYMENT GUIDE

## Current Status

✅ **Module built and ready** - All 18 files in `deal_management/` directory
⚠️ **SSH to server timing out** - Will provide manual deployment steps

---

## Files Ready for Deployment

### Local Path
```
d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management\
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── deal_stage.py
│   ├── deal_management.py
│   └── deal_line.py
├── views/
│   ├── deal_actions.xml
│   ├── deal_management_views.xml
│   ├── deal_stage_views.xml
│   ├── deal_search_views.xml
│   └── deal_menu.xml
├── security/
│   ├── ir.model.access.csv
│   └── deal_management_security.xml
├── data/
│   ├── deal_sequence.xml
│   └── deal_stage_data.xml
├── tests/
│   ├── __init__.py
│   └── test_deal_management.py
└── static/
    └── src/scss/deal_management.scss
```

---

## OPTION 1: Manual SFTP Upload (Most Reliable)

### Step 1: Connect to Server via SFTP
```
Host: erp.sgctech.ai
Port: 22
Username: root
Authentication: password or SSH key
```

### Step 2: Navigate to Addons Path
```
/var/lib/odoo/addons/
```

### Step 3: Upload Module Folder
- Drag and drop `deal_management` folder from local to remote
- Or right-click > Upload

### Step 4: Verify Upload
```bash
# In SFTP terminal or SSH:
ls -la /var/lib/odoo/addons/deal_management/
# Should show 8 items (7 dirs + 1 .py file)
```

### Step 5: Fix Permissions
```bash
ssh root@erp.sgctech.ai
chown -R odoo:odoo /var/lib/odoo/addons/deal_management
chmod -R 755 /var/lib/odoo/addons/deal_management
```

### Step 6: Restart Odoo
```bash
systemctl restart odoo
sleep 10
systemctl status odoo
```

---

## OPTION 2: Using WinSCP (GUI)

1. **Download WinSCP** from winscp.net
2. **Create new session:**
   - Protocol: SFTP
   - Host: erp.sgctech.ai
   - User: root
   - Password: (use SSH key if available)
3. **Connect**
4. **Navigate to:** `/var/lib/odoo/addons/`
5. **Drag deal_management folder** from left (local) to right (remote)
6. **Wait for upload to complete**

---

## OPTION 3: Docker Container (If Available)

If Odoo runs in Docker:

```bash
# Copy to container
docker cp deal_management <container_id>:/var/lib/odoo/addons/

# Set permissions
docker exec <container_id> chown -R odoo:odoo /var/lib/odoo/addons/deal_management

# Restart container
docker restart <container_id>
```

---

## OPTION 4: Check Current Locations First

Before uploading, verify what's already on server:

```bash
ssh root@erp.sgctech.ai

# Check standard path
ls -la /var/lib/odoo/addons/ | grep deal

# Check custom path
ls -la /var/odoo/scholarixv2/extra-addons/ | grep deal

# Check odooapps path
ls -la /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/ | grep deal
```

**If ANY deal_management exists, DELETE it first:**
```bash
rm -rf /var/lib/odoo/addons/deal_management
rm -rf /var/odoo/scholarixv2/extra-addons/deal_management
rm -rf /var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deal_management
```

Then upload fresh copy to `/var/lib/odoo/addons/deal_management`

---

## After Upload - Verify Structure

```bash
# Check main directory
ls -la /var/lib/odoo/addons/deal_management/

# Should show:
# __init__.py
# __manifest__.py
# data/
# models/
# security/
# static/
# tests/
# views/

# Check Python files
python3 -m py_compile /var/lib/odoo/addons/deal_management/__manifest__.py
python3 -m py_compile /var/lib/odoo/addons/deal_management/models/*.py
# Should return no errors
```

---

## Installation in Odoo UI

### Step 1: Update Module List
1. Go to **https://erp.sgctech.ai/scholarixv2**
2. Login: info@scholarixglobal.com / 123456
3. Go to **Settings > Apps**
4. Click **Update App List** (top-right)
5. Wait 30 seconds

### Step 2: Find Module
1. Search: "Deal Management"
2. Should see module card with Install button

### Step 3: Install
1. Click **Install**
2. Accept warnings if any
3. Wait for installation (2-3 minutes)

### Step 4: Verify
1. Go to **Sales menu**
2. Should see **Deals** submenu
3. Click **Deals > All Deals**
4. Should see empty list + Create button

---

## Troubleshooting

### Module doesn't appear in Apps?
```bash
# Check if directory exists
ssh root@erp.sgctech.ai ls /var/lib/odoo/addons/deal_management/

# If not, upload again

# If yes, check Odoo logs
ssh root@erp.sgctech.ai tail -50 /var/log/odoo/odoo.log
```

### Import errors on install?
```bash
# Check Python syntax
python3 -m py_compile /var/lib/odoo/addons/deal_management/models/*.py

# If errors, check file contents
cat /var/lib/odoo/addons/deal_management/__manifest__.py
```

### Permission denied?
```bash
# Fix permissions
chown -R odoo:odoo /var/lib/odoo/addons/deal_management
chmod -R 755 /var/lib/odoo/addons/deal_management
systemctl restart odoo
```

### Odoo won't restart?
```bash
# Check status
systemctl status odoo

# View logs
journalctl -u odoo -n 50

# Restart again
systemctl restart odoo
sleep 5
systemctl status odoo
```

---

## Verify Installation Success

Once module shows "Installed" in UI:

### 1. Check Models
```bash
ssh root@erp.sgctech.ai
python3 << EOF
import xmlrpc.client

common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common")
uid = common.authenticate("scholarixv2", "info@scholarixglobal.com", "123456", {})

models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object")

# Check for models
for model in ['deal.management', 'deal.stage', 'deal.line']:
    found = models.execute_kw(
        "scholarixv2", uid, "123456",
        'ir.model', 'search',
        [('model', '=', model)]
    )
    status = "✅" if found else "❌"
    print(f"{status} {model}: {'EXISTS' if found else 'MISSING'}")
EOF
```

### 2. Check Menu
```bash
python3 << EOF
import xmlrpc.client

common = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/common")
uid = common.authenticate("scholarixv2", "info@scholarixglobal.com", "123456", {})

models = xmlrpc.client.ServerProxy("https://localhost/xmlrpc/2/object")

# Check menu
menu_ids = models.execute_kw(
    "scholarixv2", uid, "123456",
    'ir.ui.menu', 'search',
    [('name', '=', 'Deals')]
)

if menu_ids:
    print("✅ Deals menu exists")
else:
    print("❌ Deals menu not found")
EOF
```

### 3. Create Test Deal
In UI:
1. Go to **Sales > Deals > All Deals**
2. Click **Create**
3. Fill:
   - Name: "Test Deal"
   - Code: "TEST-001"
   - Partner: Select any
   - Amount: 10000
4. Click **Save**
5. Click **Confirm** button
6. Verify state changed to "Qualification"

---

## Important Notes

⚠️ **Only ONE version allowed:**
- Delete any existing `deal_management` before uploading new one
- Check all three possible locations:
  - `/var/lib/odoo/addons/deal_management`
  - `/var/odoo/scholarixv2/extra-addons/deal_management`
  - `/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/deal_management`

✅ **After successful installation:**
- Module will be in Odoo database
- Cannot be removed from filesystem without uninstalling first
- Uninstall: Settings > Apps > Find Deal Management > Click > Uninstall

📋 **Database changes made:**
- 3 new tables created (deal_stage, deal_management, deal_line)
- 1 sequence created (deal.management)
- 6 workflow stages added
- Menu items added
- No existing tables modified

---

## Support Commands

```bash
# Check module state
ssh root@erp.sgctech.ai
systemctl status odoo

# View recent logs
tail -100 /var/log/odoo/odoo.log

# Find Python errors
grep "ERROR" /var/log/odoo/odoo.log | tail -20

# Restart Odoo
systemctl restart odoo

# Check if Odoo is listening
netstat -tlnp | grep 8069

# Test HTTPS connection
curl -k https://localhost/web/login

# Get Odoo version
python3 << EOF
import sys
sys.path.insert(0, '/opt/odoo')
import odoo
print(odoo.__version__)
EOF
```

---

## Expected Timeline

| Step | Time |
|------|------|
| Upload via SFTP | 2-5 min |
| Fix permissions | 1 min |
| Restart Odoo | 2-3 min |
| Update App List | 1 min |
| Search & Install | 2-3 min |
| **Total** | **10-15 min** |

---

**Status:** Ready for manual deployment
**Files:** All 18 files ready in `deal_management/`
**Next:** Upload to `/var/lib/odoo/addons/` via SFTP or SCP

Good luck! 🚀
