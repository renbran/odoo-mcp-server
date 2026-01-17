# QUICK DEPLOYMENT - 3 COMMANDS

## Option 1: PowerShell Script (Recommended)

### Step 1: Open PowerShell
```powershell
cd d:\01_WORK_PROJECTS\odoo-mcp-server
```

### Step 2: Run the deployment
```powershell
powershell -ExecutionPolicy Bypass -File DEPLOY-NOW.ps1
```

### Step 3: When prompted
- Enter SSH password for root@139.84.163.11
- Watch the deployment progress
- Takes 10-15 minutes

---

## Option 2: Manual SSH Commands

### Step 1: Open PowerShell or Terminal

### Step 2: Copy script to server
```bash
scp deploy-interactive.sh root@139.84.163.11:/tmp/
# Enter password when prompted
```

### Step 3: SSH to server
```bash
ssh root@139.84.163.11
# Enter password
```

### Step 4: Run deployment
```bash
cd /var/odoo/scholarixv2
bash /tmp/deploy-interactive.sh
```

### Step 5: Monitor in another terminal (optional)
```bash
ssh root@139.84.163.11
tail -f /var/log/odoo/odoo-server.log
```

---

## What Happens During Deployment

✅ **Phase 1** (1 min): Pre-checks - Validates directory, service, configuration
✅ **Phase 2** (2 min): Backups - Creates timestamped database & module backups  
✅ **Phase 3** (1 min): Stop Service - Gracefully stops Odoo
✅ **Phase 4** (2 min): Deploy Files - Copies all 4 Python & XML files
✅ **Phase 5** (1 min): Configure - Updates manifest and imports
✅ **Phase 6** (1 min): Verify Files - Confirms all files deployed correctly
✅ **Phase 7** (1 min): Start Service - Restarts Odoo with new code
✅ **Phase 8** (1 min): Verify Service - Confirms Odoo started successfully  
✅ **Phase 9** (2 min): Monitor Logs - Checks for errors during startup

**Total Time: ~15 minutes**

---

## After Deployment

### 1. Upgrade Module in Odoo UI
- Open: http://139.84.163.11:8069
- Go to: Settings → Apps
- Search: commission_ax
- Click: Upgrade button
- Wait: 2-5 minutes

### 2. Verify in Sale Orders
- Go to: Sales → Quotations
- Open any sale order
- Look for: "BROKERAGE DEAL INFORMATION" section
- Should show: Buyer Name, Project, Unit Price, Commission %

### 3. Run Tests
- Follow: TESTING-GUIDE.md
- Run all 17 test cases
- Document results

---

## Troubleshooting

### Password Issues
If SSH password isn't working:
1. Try entering password manually when script prompts
2. Check if SSH key setup is needed
3. Verify credentials in .env file

### Script Not Found
If deploy-interactive.sh not found:
```bash
ls -la d:\01_WORK_PROJECTS\odoo-mcp-server\deploy-interactive.sh
```
Make sure you're in the correct directory.

### Installation Fails
Check logs on server:
```bash
ssh root@139.84.163.11
tail -100 /var/log/odoo/odoo-server.log
```

### Rollback
If issues occur:
```bash
ssh root@139.84.163.11
cd /var/odoo/scholarixv2

# Restore from backup
systemctl stop odoo
cp -r backups/commission_ax_YYYYMMDD_HHMMSS/* \
      extra-addons/odooapps.git-68ee71eda34bc/commission_ax/

# Restore database
systemctl stop odoo
psql commission_ax < backups/commission_ax_YYYYMMDD_HHMMSS.sql

systemctl start odoo
```

---

## Ready?

Run this command to start:

```powershell
cd d:\01_WORK_PROJECTS\odoo-mcp-server
powershell -ExecutionPolicy Bypass -File DEPLOY-NOW.ps1
```

**Good luck! 🚀**
