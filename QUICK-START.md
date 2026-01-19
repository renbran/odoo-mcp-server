# Odoo MCP Server - Quick Setup Guide

**Status:** ✅ All 6 Odoo instances configured and ready to use

---

## 🚀 Get Started in 2 Steps

### Step 1: Install Claude Desktop Config (30 seconds)

**Copy this file:**
```
d:\odoo17_backup\odoo-mcp-server\claude_desktop_config.json
```

**Paste to:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Windows Users:** Press `Win + R` and paste this to open the folder:
```
%APPDATA%\Claude
```

### Step 2: Restart Claude Desktop (10 seconds)

1. Close Claude Desktop completely
2. Wait 3 seconds
3. Reopen Claude Desktop
4. Look for ✓ in bottom-left corner (green checkmark = connected)

---

## ✅ Verify It's Working

**Ask Claude:**
```
What Odoo instances are available?
```

**Expected Response:**
```
6 instances connected:
- scholarixv2 (v17)
- osusproperties (v17)
- eigermarvelhr (v18)
- scholarix-restaurant (v18)
- testserver-hospital (v18)
- sgctechai (v19)
```

---

## 📚 Learn What You Can Do

### Example 1: Search for Customers
```
Find all customers in scholarixv2 with email addresses
```

### Example 2: Get Sales Data
```
Show me the top 5 sales orders by amount in eigermarvelhr
```

### Example 3: Create Records
```
Create a new contact "Tech Solutions Inc" in osusproperties
```

### Example 4: Cross-Instance Search
```
Find all unpaid invoices across all instances
```

### Example 5: Generate Reports
```
Generate an invoice PDF for order #100 in scholarix-restaurant
```

---

## 🛠️ Your 6 Connected Databases

| Instance | URL | Version | Status |
| -------- | --- | ------- | ------ |
| scholarixv2 | https://erp.sgctech.ai | v17 | ✅ Live |
| osusproperties | https://erposus.com | v17 | ✅ Live |
| eigermarvelhr | https://eigermarvelhr.com | v18 | ✅ Live |
| scholarix-restaurant | https://scholarix.cloudpepper.site | v18 | ✅ Live |
| testserver-hospital | https://testserver.cloudpepper.site | v18 | ✅ Testing |
| sgctechai | https://scholarixglobal.com | v19 | ✅ Local |

---

## 🔧 Technical Details

**Server Location:**
```
d:\odoo17_backup\odoo-mcp-server
```

**Start/Stop Server:**
```bash
# Start
npm start

# Stop (Ctrl+C in terminal)
```

**Available Tools:**
- odoo_search
- odoo_search_read
- odoo_read
- odoo_create
- odoo_update
- odoo_delete
- odoo_execute
- odoo_count
- odoo_workflow_action
- odoo_generate_report
- odoo_get_model_metadata

---

## ❓ Need Help?

### "Instance not found"
Check the exact name: `scholarixv2` (not `scholarix-v2`)

### "Authentication failed"
Verify username/password in `.env` file

### "Model not found"
Use correct Odoo model name: `res.partner` (not `customer`)

### Claude doesn't see instances
1. Restart Claude Desktop
2. Check Claude Desktop is showing the server (bottom-left ✓)
3. Verify `%APPDATA%\Claude\claude_desktop_config.json` exists

---

## 📖 Full Documentation

For detailed information, see:
- [USAGE-GUIDE.md](USAGE-GUIDE.md) - Complete features, examples, troubleshooting
- [README.md](README.md) - Technical reference
- [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) - Production deployment

---

**You're all set! Start asking Claude questions about your Odoo instances.** 🎉
