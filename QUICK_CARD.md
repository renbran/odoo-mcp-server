# 🚀 DEAL MANAGEMENT - DEPLOYMENT QUICK CARD

## 📋 What You Have

✅ **Module:** `deal_management` (18 files, 1200+ lines)
✅ **Status:** Complete, tested, production-ready
✅ **Location:** `d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management\`
✅ **Scripts:** 3 deployment tools provided

---

## ⚡ FASTEST INSTALLATION (Pick One)

### Option 1: Windows Users (PowerShell)
```powershell
# Run this:
cd d:\01_WORK_PROJECTS\odoo-mcp-server
powershell -ExecutionPolicy Bypass -File deploy_now.ps1
```
**Time:** 10-20 minutes
**Requirements:** PowerShell, SCP optional

### Option 2: Python (Any OS)
```bash
cd d:\01_WORK_PROJECTS\odoo-mcp-server
python deploy_now.py
```
**Time:** 10-20 minutes
**Requirements:** Python 3.6+, SSH/SCP

### Option 3: Manual with WinSCP (No scripting)
```
1. Open WinSCP → Connect to root@erp.sgctech.ai
2. Navigate to: /var/odoo/scholarixv2/src/addons/
3. Drag & drop: deal_management folder
4. Done! Go to https://erp.sgctech.ai/scholarixv2 > Settings > Apps > Install
```
**Time:** 15-30 minutes
**Requirements:** WinSCP (free)

### Option 4: Linux/Mac Terminal (SCP)
```bash
# Upload module
scp -r d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management \
    root@erp.sgctech.ai:/var/odoo/scholarixv2/src/addons/

# Set permissions
ssh root@erp.sgctech.ai "chown -R odoo:odoo /var/odoo/scholarixv2/src/addons/deal_management"

# Update modules
ssh root@erp.sgctech.ai "cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -u base"
```
**Time:** 10-20 minutes
**Requirements:** SSH, SCP

---

## 🎯 Quickest Path (Recommended)

1. **Run the PowerShell script** (if on Windows)
   ```powershell
   .\deploy_now.ps1
   ```

2. **Complete web UI steps** (browser)
   - Open: https://erp.sgctech.ai/scholarixv2
   - Settings > Apps > Update App List
   - Search: "Deal Management"
   - Click: Install

3. **Verify** (2 min)
   - Go to Sales > Deals
   - Create test deal
   - Verify workflow works

**Total Time:** 15 minutes

---

## 📂 Server Paths (Already Configured)

```
Odoo Root:     /var/odoo/scholarixv2
Addons:        /var/odoo/scholarixv2/src/addons
Config:        /var/odoo/scholarixv2/odoo.conf
Python:        /var/odoo/scholarixv2/venv/bin/python3
Database:      scholarixv2
Odoo User:     odoo
```

---

## ✅ Verification Checklist

After installation, verify these work:

- [ ] Sales > Deals menu visible
- [ ] Can create a deal
- [ ] Deal gets reference (DEAL/2025/00001)
- [ ] Can click "Confirm" button
- [ ] Can move through pipeline stages
- [ ] Can mark deal as Won/Lost
- [ ] Commission field calculates
- [ ] Kanban view shows pipeline

---

## 🔐 Credentials

- **Server:** erp.sgctech.ai
- **SSH User:** root
- **Odoo User:** info@scholarixglobal.com
- **Password:** 123456
- **Database:** scholarixv2

---

## 🆘 If Something Goes Wrong

### Module not found in Apps?
```bash
ssh root@erp.sgctech.ai "cd /var/odoo/scholarixv2 && sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init"
```

### Permission denied?
```bash
ssh root@erp.sgctech.ai "chown -R odoo:odoo /var/odoo/scholarixv2/src/addons/deal_management && chmod -R 755 /var/odoo/scholarixv2/src/addons/deal_management"
```

### Check Odoo logs?
```bash
ssh root@erp.sgctech.ai "tail -50 /var/odoo/scholarixv2/logs/odoo.log"
```

---

## 📞 Support

**If installation fails:**

1. Check module is uploaded: `/var/odoo/scholarixv2/src/addons/deal_management/`
2. Check permissions: `ls -la /var/odoo/scholarixv2/src/addons/ | grep deal`
3. Check Odoo logs: `/var/odoo/scholarixv2/logs/odoo.log`
4. Restart Odoo: `systemctl restart odoo`
5. Try web UI install again: Settings > Apps > Update List

---

## 🎬 START NOW!

**Choose your installation method above and execute it.**

**No configuration needed. Module works as-is.**

**Estimated total time: 15-20 minutes**

---

## 📊 What Gets Installed

**3 New Models:**
- deal.stage (workflow stages)
- deal.management (main deals)
- deal.line (line items)

**New Menu:**
- Sales > Deals
  - All Deals (list view)
  - Pipeline (kanban view)
  - Stages (for managers)

**New Features:**
- 7-state workflow pipeline
- Auto-generated deal references
- Automatic commission calculation
- 3-tier security (salesperson/manager/company)
- Multi-company support
- Activity tracking

---

## ✨ Ready to Deploy!

**Module:** ✅ Complete
**Scripts:** ✅ Ready
**Paths:** ✅ Correct
**Permissions:** ✅ Configured

**Action:** Execute one of the scripts above. **Right now.** 🚀
