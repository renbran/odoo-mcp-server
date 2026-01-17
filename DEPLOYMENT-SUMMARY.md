# COMMISSION_AX - DEPLOYMENT COMPLETE

## ✅ What's Been Accomplished

### 1. Backend Tools Deployed (Server: 139.84.163.11)
```
Location: /var/odoo/scholarixv2/

Files:
  • inspect-quick.py         - Fast PostgreSQL queries (recommended)
  • inspect-backend.py       - Full Odoo shell access
  • install-commission-ax.py - Automated installer
```

### 2. Module Discovery
```
Module:        commission_ax
Status:        uninstalled
Type:          Application
License:       LGPL-3
Description:   Professional commission management with workflow

Dependencies:
  ✅ base      (installed)
  ❌ account   (uninstalled) - Accounting
  ❌ sale      (uninstalled) - Sales
  ❌ purchase  (uninstalled) - Purchasing
```

### 3. Claude Desktop MCP Server
```
Config File:   C:\Users\branm\AppData\Roaming\Claude\claude_desktop_config.json
Server Name:   odoo-commission-ax
Database:      commission_ax
URL:           https://erp.sgctech.ai
Status:        Configured (needs restart)
```

---

## 🎯 Next Actions

### IMMEDIATE: Restart Claude Desktop
1. **Close** Claude Desktop completely
2. **Relaunch** Claude Desktop  
3. **Verify** "odoo-commission-ax" appears in MCP servers

### TEST: MCP Connection
In Claude Desktop, ask:
```
"List all modules in the commission_ax database"
```

Expected: Claude uses MCP tools to query and return module list

### WHEN READY: Install Modules

#### Option A: Web Interface (Recommended)
```
1. Login: https://erp.sgctech.ai
2. Go to Apps
3. Install in order:
   a) Accounting  (account)
   b) Sales       (sale)
   c) Purchasing  (purchase)
   d) Commission AX (commission_ax)
```

#### Option B: Automated Script
```bash
ssh root@139.84.163.11
cd /var/odoo/scholarixv2
python3 install-commission-ax.py
```

The script will:
- Check current module states
- Show installation plan
- Ask for confirmation
- Install all 4 modules in order
- Report success/failures

---

## 📚 Tools Reference

### Backend Inspector (SSH to server first)

**Quick Inspector** (Fast - uses PostgreSQL directly):
```bash
# Search modules
python3 inspect-quick.py search commission

# Module info
python3 inspect-quick.py info commission_ax

# List by state
python3 inspect-quick.py list uninstalled
python3 inspect-quick.py list installed
```

**Full Inspector** (Slower - uses Odoo shell):
```bash
# Same commands, uses inspect-backend.py instead
python3 inspect-backend.py list
python3 inspect-backend.py info <module>
```

### MCP Server (Via Claude Desktop)

Just ask Claude in natural language:
```
"Show me all uninstalled modules"
"Get information about commission_ax module"
"What modules are currently installed?"
```

Claude will use the MCP tools automatically.

### Module Installer

**Automated installation**:
```bash
python3 install-commission-ax.py
```

**What it does**:
1. Checks current state of all modules
2. Shows what needs installation
3. Asks for confirmation
4. Installs: account → sale → purchase → commission_ax
5. Reports results

---

## 🔧 Troubleshooting

### Claude Desktop Can't Connect

**Check 1**: Config file syntax
```powershell
Get-Content "$env:APPDATA\Claude\claude_desktop_config.json"
```

**Check 2**: MCP server built
```powershell
Test-Path "D:\01_WORK_PROJECTS\odoo-mcp-server\dist\index.js"
```

If false, rebuild:
```powershell
cd D:\01_WORK_PROJECTS\odoo-mcp-server
npm run build
```

**Check 3**: Restart Claude Desktop completely

### Backend Inspector Issues

**Permission denied**:
```bash
chmod +x inspect-quick.py
sudo python3 inspect-quick.py list
```

**Module not found**:
```bash
# Verify database name
cat /var/odoo/scholarixv2/odoo.conf | grep db_name
```

### Installation Script Fails

**Timeout errors**:
- Modules are large, may need 5+ minutes each
- Script timeout is 5 minutes per module
- Use web interface for large modules

**Dependency errors**:
- Install dependencies in correct order
- Script handles this automatically

---

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────┐
│  LOCAL MACHINE (Windows)                                │
│                                                          │
│  ┌────────────────┐         ┌──────────────────┐       │
│  │ Claude Desktop │────────▶│ MCP Server       │       │
│  │                │         │ (Node.js)        │       │
│  └────────────────┘         └──────────────────┘       │
│                                      │                   │
│                                      │ XML-RPC           │
│                                      ▼                   │
│                             ┌──────────────────┐        │
│                             │ Odoo Server      │        │
│                             │ 139.84.163.11    │        │
│                             │ commission_ax DB │        │
│                             └──────────────────┘        │
│                                      ▲                   │
│                                      │ Direct Access     │
│                             ┌──────────────────┐        │
│                             │ Backend Tools    │        │
│                             │ (Python scripts) │        │
│                             └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

**Two Access Methods**:
1. **MCP + Claude**: AI-assisted, natural language queries
2. **Backend Scripts**: Direct, scriptable, fast queries

Both access the same `commission_ax` database!

---

## 📝 Files Created

### On Local Machine
```
D:\01_WORK_PROJECTS\odoo-mcp-server\
├── inspect-quick.py              (copied to server)
├── inspect-backend.py            (copied to server)
├── install-commission-ax.py      (copied to server)
├── claude-config-READY.json      (reference)
├── SYSTEMATIC-DEPLOYMENT-CHECKLIST.md
├── QUICK-START-COMMANDS.txt
└── THIS-FILE.md                  (DEPLOYMENT-SUMMARY.md)
```

### On Server (139.84.163.11)
```
/var/odoo/scholarixv2/
├── inspect-quick.py         ← FAST queries
├── inspect-backend.py       ← Full Odoo access
└── install-commission-ax.py ← Auto-installer
```

### Claude Desktop
```
C:\Users\branm\AppData\Roaming\Claude\
├── claude_desktop_config.json           (active)
└── claude_desktop_config.json.backup... (backup)
```

---

## ✅ Success Criteria

You'll know everything is working when:

1. ✅ Claude Desktop shows "odoo-commission-ax" in MCP servers
2. ✅ Claude can list modules from commission_ax database
3. ✅ Backend inspector returns module data
4. ✅ (After installation) commission_ax module state = "installed"

---

## 🚀 Ready to Start

**RIGHT NOW**:
- Restart Claude Desktop
- Test MCP connection

**WHEN READY TO INSTALL**:
- Choose web interface OR automated script
- Install dependencies + commission_ax
- Verify in Odoo web interface

---

## 📞 Quick Command Reference

### SSH to Server
```bash
ssh root@139.84.163.11
cd /var/odoo/scholarixv2
```

### Check Module Status
```bash
python3 inspect-quick.py info commission_ax
```

### Install Everything
```bash
python3 install-commission-ax.py
```

### Access Odoo Web
```
URL: https://erp.sgctech.ai
User: info@scholarixglobal.com
Pass: 123456
```

---

**Deployment Date**: January 17, 2026  
**Server**: 139.84.163.11  
**Database**: commission_ax  
**Status**: ✅ READY TO USE
