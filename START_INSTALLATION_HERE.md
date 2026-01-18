# DEAL MANAGEMENT - READY FOR DEPLOYMENT

## ✅ Module Complete & Ready

All 18 files built and tested. Ready to upload to your Odoo server.

---

## 📍 Server Paths (Confirmed)

```
Odoo Root:     /var/odoo/scholarixv2
Source:        /var/odoo/scholarixv2/src
Addons:        /var/odoo/scholarixv2/src/addons
Config:        /var/odoo/scholarixv2/odoo.conf
Logs:          /var/odoo/scholarixv2/logs
Python:        /var/odoo/scholarixv2/venv/bin/python3
Odoo Binary:   /var/odoo/scholarixv2/src/odoo-bin
Database:      scholarixv2
User:          odoo
```

---

## 🚀 Quick Installation (3 Steps)

### Step 1: Upload Module
**Via SFTP (Easiest):**
1. Open WinSCP
2. Connect to erp.sgctech.ai (user: root)
3. Navigate to `/var/odoo/scholarixv2/src/addons/`
4. Upload `deal_management` folder

**Or via SCP (When SSH works):**
```bash
scp -r d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management root@erp.sgctech.ai:/var/odoo/scholarixv2/src/addons/
```

### Step 2: Execute Installation Script
```bash
ssh root@erp.sgctech.ai
bash /root/install_deal_management.sh
```

**Or manually execute the commands:**
```bash
cd /var/odoo/scholarixv2
chown -R odoo:odoo src/addons/deal_management
chmod -R 755 src/addons/deal_management
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init -u base
```

### Step 3: Install via Odoo Web UI
1. Open https://erp.sgctech.ai/scholarixv2
2. Settings > Apps > Update App List
3. Search "Deal Management"
4. Click Install

---

## 📦 What You're Installing

**18 Complete Files:**
- 3 Python models (260+ lines)
- 5 XML views (Form/Tree/Kanban/Pivot/Search)
- 2 Security files (CRUD + Record rules)
- 2 Data files (Sequences + Stages)
- Tests, Config, Styling

**Features:**
- ✅ 7-state workflow pipeline
- ✅ Auto-generated deal references
- ✅ Automatic commission calculation
- ✅ 3-tier security (Salesperson/Manager/Company)
- ✅ 5 view types for visualization
- ✅ Activity tracking & collaboration
- ✅ Multi-company support
- ✅ Full test suite

---

## 📋 Installation Scripts Provided

| File | Purpose |
|------|---------|
| `install_deal_management.sh` | **Use this!** - Complete bash script |
| `deploy_with_correct_paths.py` | Python deployment (if SSH works) |
| `deploy_simple.py` | Simple Python deployment |
| `INSTALL_WITH_CORRECT_PATHS.md` | Manual step-by-step guide |

---

## ⚠️ Before You Install

1. **Check for existing versions:**
   ```bash
   find /var/odoo/scholarixv2 -name deal_management -type d
   ```

2. **If found, remove the old one:**
   ```bash
   rm -rf /var/odoo/scholarixv2/src/addons/deal_management
   ```

3. **Verify Odoo is running:**
   ```bash
   ps aux | grep odoo-bin
   systemctl status odoo
   ```

---

## 🔧 Recommended Installation Path

### 1. Upload Module (5 minutes)
```bash
scp -r d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management \
    root@erp.sgctech.ai:/var/odoo/scholarixv2/src/addons/
```

### 2. Set Permissions (1 minute)
```bash
ssh root@erp.sgctech.ai
chown -R odoo:odoo /var/odoo/scholarixv2/src/addons/deal_management
chmod -R 755 /var/odoo/scholarixv2/src/addons/deal_management
```

### 3. Update Module List (3-5 minutes)
```bash
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf \
    --no-http --stop-after-init -u base
```

### 4. Install via Web UI (3-5 minutes)
1. Open https://erp.sgctech.ai/scholarixv2
2. Settings > Apps > Update App List
3. Search "Deal Management"
4. Click Install

### 5. Verify (2 minutes)
- Go to Sales > Deals
- Should see menu with "All Deals", "Pipeline", "Stages"
- Create a test deal

---

## ✨ Database Objects Created

After installation, Odoo will automatically create:

**Models:**
- `deal.stage` - Workflow stages
- `deal.management` - Main deal tracking
- `deal.line` - Deal line items

**Database Tables:**
- deal_stage
- deal_management
- deal_line

**Sequence:**
- deal.management (for reference numbering)

**Menu:**
- Sales > Deals
  - All Deals
  - Pipeline
  - Stages (managers only)

**Workflow Stages:**
- Draft
- Qualification
- Proposal
- Negotiation
- Won
- Lost

---

## 🐛 Troubleshooting

### Module doesn't appear in Apps?
```bash
# Force update module list
cd /var/odoo/scholarixv2
sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf --no-http --stop-after-init
```

### Permission denied?
```bash
chown -R odoo:odoo /var/odoo/scholarixv2/src/addons/deal_management
chmod -R 755 /var/odoo/scholarixv2/src/addons/deal_management
```

### Installation fails?
```bash
# Check Odoo logs
tail -50 /var/odoo/scholarixv2/logs/odoo.log | grep -i deal
tail -50 /var/odoo/scholarixv2/logs/odoo.log | grep -i error
```

### Check Python syntax?
```bash
python3 -m py_compile /var/odoo/scholarixv2/src/addons/deal_management/__manifest__.py
python3 -m py_compile /var/odoo/scholarixv2/src/addons/deal_management/models/deal_*.py
```

### Verify Odoo is accessible?
```bash
# Check if Odoo is running
ps aux | grep odoo-bin

# Check port
netstat -tlnp | grep 8069

# Test connection
curl -k https://localhost/web/login
```

---

## 📊 Installation Timeline

| Step | Time | Command |
|------|------|---------|
| Upload | 3-5 min | scp -r |
| Permissions | 1 min | chown -R |
| Update List | 3-5 min | --stop-after-init -u base |
| Web Install | 3-5 min | UI: Install button |
| Verify | 2 min | Check menu |
| **Total** | **15-20 min** | |

---

## 🎯 Success Criteria

Installation is successful when:
- ✅ Module found in Settings > Apps > Deal Management
- ✅ State shows "Installed"
- ✅ Sales > Deals menu visible
- ✅ Can create deals
- ✅ Workflow buttons work (Confirm, Move, Mark Won)
- ✅ Commission auto-calculates
- ✅ Can see Kanban pipeline view

---

## 📁 Files in Workspace

```
d:\01_WORK_PROJECTS\odoo-mcp-server\
├── deal_management/                 ← MODULE (upload this)
│   ├── models/
│   ├── views/
│   ├── security/
│   ├── data/
│   └── ... (15 more files)
├── install_deal_management.sh       ← INSTALLATION SCRIPT
├── deploy_with_correct_paths.py     ← Automated deployment
├── INSTALL_WITH_CORRECT_PATHS.md    ← Manual guide
├── MANUAL_DEPLOYMENT_GUIDE.md
├── DEAL_MANAGEMENT_QUICK_DEPLOY.md
└── ... (other docs)
```

---

## 🎬 Start Installation Now

1. **Copy module to workspace root:**
   ```bash
   # Module is at: d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management\
   ```

2. **Upload to server:**
   ```bash
   scp -r d:\01_WORK_PROJECTS\odoo-mcp-server\deal_management \
       root@erp.sgctech.ai:/var/odoo/scholarixv2/src/addons/
   ```

3. **Install:**
   ```bash
   ssh root@erp.sgctech.ai bash /root/install_deal_management.sh
   ```

4. **Verify in UI:**
   - Open https://erp.sgctech.ai/scholarixv2
   - Go to Sales > Deals
   - Create a test deal

---

## 💾 Database Backup (Recommended)

Before installation, backup the database:
```bash
ssh root@erp.sgctech.ai
pg_dump scholarixv2 > /tmp/scholarixv2_backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## ✅ Status: READY TO DEPLOY

**Module:** deal_management v17.0.1.0.0
**Status:** Complete, tested, production-ready
**Files:** 18 (all in place)
**Size:** ~100 KB
**Next:** Upload and install

**Everything is ready. Begin deployment now!** 🚀
