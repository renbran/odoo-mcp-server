# SYSTEMATIC COMMISSION_AX DEPLOYMENT - STEP BY STEP

Follow these steps in order. Check each box as you complete it.

## ✅ PHASE 1: Backend Inspector Deployment

### [ ] Step 1.1: Get Server Connection Details
```
You need:
- Server hostname/IP: _____________________
- SSH username: _____________________
- SSH key or password ready
```

### [ ] Step 1.2: Copy inspect-backend.py to Server
```powershell
# From this directory (odoo-mcp-server), run:
scp inspect-backend.py YOUR_USER@YOUR_SERVER:/var/odoo/scholarixv2/
```

Example:
```powershell
scp inspect-backend.py admin@erp.sgctech.ai:/var/odoo/scholarixv2/
```

### [ ] Step 1.3: SSH to Server
```bash
ssh YOUR_USER@YOUR_SERVER
cd /var/odoo/scholarixv2
ls -la inspect-backend.py  # Verify file exists
```

---

## ✅ PHASE 2: Test Backend Inspector

### [ ] Step 2.1: List All Modules
```bash
python3 inspect-backend.py list
```

**Expected**: List of modules with states (installed/uninstalled/to install)

### [ ] Step 2.2: Search for Commission Modules
```bash
python3 inspect-backend.py list uninstalled | grep -i commission
```

**Expected**: Shows modules with "commission" in the name

### [ ] Step 2.3: Get commission_ax Details
```bash
python3 inspect-backend.py info commission_ax
```

**Expected Output**:
- Name: commission_ax
- State: (installed/uninstalled/to install)
- Description: (module purpose)
- Dependencies: (list of required modules)
- Version: (X.X)

**Important**: Check dependencies! Note which modules need to be installed first.

---

## ✅ PHASE 3: Install commission_ax Module

### [ ] Step 3.1: Review Prerequisites
Before installing, ensure:
- [ ] All dependencies are available (check Step 2.3 output)
- [ ] Module state is NOT 'broken' or 'to remove'
- [ ] You have database admin permissions

### [ ] Step 3.2: Install Module
```bash
python3 inspect-backend.py install commission_ax
```

**What happens**:
1. Odoo checks dependencies
2. Installs missing dependencies first
3. Updates database schema
4. Initializes module data
5. Sets state to 'installed'

**Time**: May take 30 seconds to 2 minutes

### [ ] Step 3.3: Verify Installation
```bash
python3 inspect-backend.py info commission_ax
```

**Check**: State should now be 'installed'

---

## ✅ PHASE 4: Configure MCP Server

### [ ] Step 4.1: Verify MCP Build
```powershell
# Back on your Windows machine, in odoo-mcp-server directory:
cd D:\01_WORK_PROJECTS\odoo-mcp-server
Test-Path .\dist\index.js
```

**Expected**: True

If False, build it:
```powershell
npm run build
```

### [ ] Step 4.2: Update Claude Desktop Config

**File Location**: `C:\Users\YOUR_USERNAME\AppData\Roaming\Claude\claude_desktop_config.json`

**Option A: Create/Replace Entire File**
```json
{
  "mcpServers": {
    "odoo-commission-ax": {
      "command": "node",
      "args": [
        "D:/01_WORK_PROJECTS/odoo-mcp-server/dist/index.js"
      ],
      "env": {
        "ODOO_URL": "https://erp.sgctech.ai",
        "ODOO_DB": "commission_ax",
        "ODOO_USERNAME": "info@scholarixglobal.com",
        "ODOO_PASSWORD": "123456"
      }
    }
  }
}
```

**Option B: Add to Existing Config**
If you already have other MCP servers, add just the "odoo-commission-ax" section inside "mcpServers".

### [ ] Step 4.3: Verify Config File
```powershell
Get-Content "$env:APPDATA\Claude\claude_desktop_config.json"
```

**Check**:
- Valid JSON format
- Path to dist/index.js is correct
- Credentials match your .env file

---

## ✅ PHASE 5: Test Claude Desktop Integration

### [ ] Step 5.1: Restart Claude Desktop
1. **Close** Claude Desktop completely (check system tray)
2. **Relaunch** Claude Desktop
3. **Wait** ~10 seconds for MCP servers to initialize

### [ ] Step 5.2: Verify MCP Connection
In Claude Desktop, look for:
- MCP icon/indicator
- "odoo-commission-ax" in available servers list

### [ ] Step 5.3: Test Module Query
Ask Claude:
```
List all uninstalled modules in the commission_ax database. 
Show name, description, and state for each.
```

**Expected**: Claude uses odoo-commission-ax tools to query and returns module list

### [ ] Step 5.4: Test Module Information
Ask Claude:
```
Get detailed information about the commission_ax module including 
all dependencies and current installation state.
```

**Expected**: Claude retrieves module details using MCP tools

---

## ✅ VERIFICATION CHECKLIST

After completing all phases:

- [ ] Backend inspector works on server
- [ ] commission_ax module is installed (or info retrieved successfully)
- [ ] MCP server is built (dist/index.js exists)
- [ ] Claude Desktop config is updated
- [ ] Claude Desktop can connect to commission_ax database
- [ ] Claude can query modules via MCP tools

---

## 🛠️ TROUBLESHOOTING

### Backend Inspector Issues

**Problem**: "Permission denied" when running inspect-backend.py
```bash
chmod +x inspect-backend.py
sudo python3 inspect-backend.py list
```

**Problem**: "Module not found" errors
```bash
# Check Python environment
/var/odoo/scholarixv2/venv/bin/python3 --version
# Ensure using Odoo's virtual environment
```

**Problem**: "Database connection failed"
```bash
# Check odoo.conf has correct database settings
cat /var/odoo/scholarixv2/odoo.conf | grep -E "db_name|db_host|db_user"
```

### MCP Server Issues

**Problem**: Claude can't find odoo-commission-ax
- Check config path is correct (no typos)
- Restart Claude Desktop completely
- Check MCP server logs in Claude

**Problem**: "Authentication failed"
- Verify credentials in claude_desktop_config.json match .env
- Test credentials via browser login to https://erp.sgctech.ai

**Problem**: "Cannot find module" in MCP
```powershell
# Rebuild MCP server
cd D:\01_WORK_PROJECTS\odoo-mcp-server
npm run build
# Restart Claude Desktop
```

---

## 📚 QUICK REFERENCE

### Server Commands (SSH)
```bash
# List modules by state
python3 inspect-backend.py list [installed|uninstalled|to install]

# Get module info
python3 inspect-backend.py info <module_name>

# Install module
python3 inspect-backend.py install <module_name>

# Search for modules
python3 inspect-backend.py list uninstalled | grep <search_term>
```

### Local Commands (PowerShell)
```powershell
# Build MCP server
npm run build

# Check Claude config
Get-Content "$env:APPDATA\Claude\claude_desktop_config.json"

# Edit Claude config
notepad "$env:APPDATA\Claude\claude_desktop_config.json"
```

---

## ✅ COMPLETION

When all checkboxes above are marked:
- ✅ You can inspect/install modules via backend inspector
- ✅ You can use Claude Desktop with AI assistance for Odoo operations
- ✅ Both tools access the same commission_ax database

**Next Steps**: Use either tool based on your preference:
- Direct/scriptable → Backend inspector
- AI-assisted/exploratory → Claude Desktop + MCP
