# 🎯 Quick Setup Guide - Odoo MCP Server

## Step-by-Step Installation

### 1️⃣ Install Dependencies (First Time Only)

```bash
cd d:\01_WORK_PROJECTS\odoo-mcp-server
npm install
```

### 2️⃣ Configure Your Odoo Instance

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your Odoo details:

```env
# For local Odoo development
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_dev
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# For Odoo.com (cloud)
# ODOO_URL=https://yourcompany.odoo.com
# ODOO_DB=yourcompany-main-123456
# ODOO_USERNAME=your.email@company.com
# ODOO_PASSWORD=your_password
```

**How to find your Odoo database name:**
- In Odoo: Settings → General Settings → scroll down to "About"
- Or check the URL: `https://company.odoo.com/web?db=DATABASE_NAME`

### 3️⃣ Build the Server

```bash
npm run build
```

### 4️⃣ Test It Works

```bash
npm run dev
```

You should see:
```
Odoo MCP Server running
Configured instances: default
Available tools: 11
✓ Connected to Odoo default (17.0)
```

Press `Ctrl+C` to stop.

---

## 🤖 Connect to Claude Desktop

### Step 1: Find Claude Config File

**Windows:** Press `Win+R`, type: `%APPDATA%\Claude` and press Enter

**Mac:** Open Finder → Go → Go to Folder → Type: `~/Library/Application Support/Claude`

### Step 2: Edit `claude_desktop_config.json`

If the file doesn't exist, create it. Add this:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo_dev",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin"
      }
    }
  }
}
```

**⚠️ IMPORTANT:** 
- Replace the path with your actual project path
- Use double backslashes `\\` on Windows
- Update ODOO credentials to match your instance

### Step 3: Restart Claude Desktop

1. Completely quit Claude Desktop (right-click taskbar → Quit)
2. Start Claude Desktop again
3. Look for 🔌 icon in Claude - it should show "odoo" server connected

---

## ✅ Test in Claude

Try these commands:

1. **List tools:**
   > "What Odoo tools do you have available?"

2. **Search records:**
   > "Search for all customers in Odoo"

3. **Create a test record:**
   > "Create a new contact named 'Test User' with email test@example.com in Odoo"

4. **Get model info:**
   > "Show me what fields are available on the sale.order model"

---

## 🎨 Pro Tips

### For Multiple Odoo Instances

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
      "env": {
        "ODOO_INSTANCES": "{\"production\":{\"url\":\"https://prod.odoo.com\",\"db\":\"prod_db\",\"username\":\"admin\",\"password\":\"pass123\"},\"local\":{\"url\":\"http://localhost:8069\",\"db\":\"dev_db\",\"username\":\"admin\",\"password\":\"admin\"}}"
      }
    }
  }
}
```

Then in Claude:
> "Search for orders in the **production** instance"
> "Create a customer in the **local** instance"

### Quick Commands Reference

```bash
# Development (with auto-reload)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Watch mode (rebuild on changes)
npm run watch
```

---

## 🐛 Common Issues

### ❌ "Cannot find module"
**Fix:** Run `npm install` then `npm run build`

### ❌ "Authentication failed"
**Fix:** Check your credentials in `.env` or Claude config
- Verify database name is correct
- Try logging into Odoo web interface with same credentials

### ❌ "Connection refused" or "ECONNREFUSED"
**Fix:** 
- Make sure Odoo is running (`http://localhost:8069`)
- Check firewall settings
- Verify the URL and port are correct

### ❌ Claude doesn't show the MCP server
**Fix:**
1. Check `claude_desktop_config.json` for syntax errors (use a JSON validator)
2. Verify the file path to `dist/index.js` exists and is correct
3. Completely restart Claude Desktop
4. Check Claude logs: `%APPDATA%\Claude\logs\mcp*.log`

### ❌ "Unknown instance: production"
**Fix:** You're using multiple instances - specify which one:
> "Search in the **production** instance for..."

---

## 📞 Need Help?

1. Check the [full README.md](./README.md) for detailed docs
2. Review Odoo connection in Odoo itself (Settings → Users → your user → has API access?)
3. Check Claude MCP logs for detailed errors

---

## 🎉 You're All Set!

Your Odoo MCP server is now ready! Claude can now:
- 📊 Search and read your Odoo data
- ✏️ Create, update, and delete records
- 🔄 Execute workflows (confirm orders, post invoices, etc.)
- 📄 Generate reports
- 🔍 Explore model structures

**Enjoy building with Odoo + AI! 🚀**
