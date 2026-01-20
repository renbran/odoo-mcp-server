# VS Code Setup - Odoo MCP Server

## 🎯 Using Odoo MCP Server in VS Code

VS Code can use the Odoo MCP Server for code editing, debugging, and AI assistance through Copilot.

---

## ✅ Quick Setup (2 Steps)

### Step 1: Install Recommended Extensions

When you open this project in VS Code, you'll see a prompt:
```
"This workspace has extension recommendations"
```

Click **"Install"** or manually install:
- GitHub Copilot
- GitHub Copilot Chat
- TypeScript Nightly
- Prettier - Code Formatter
- ESLint

### Step 2: Open Copilot Chat

Press `Ctrl+Shift+I` to open Copilot Chat in VS Code.

The MCP server will be available for Copilot to use while you're working.

---

## 🔧 Configuration Files

We've created `.vscode/` folder with:

- **settings.json** - Workspace settings (formatting, extensions)
- **mcp.json** - MCP server configuration (optional)
- **extensions.json** - Recommended extensions for the project

---

## 💡 How to Use

### In Copilot Chat (Ctrl+Shift+I):

```
"Search for customers in scholarixv2"
"Create a new sales order"
"How many invoices are unpaid in eigermarvelhr?"
"Generate invoice PDF for order #100"
```

Copilot will use the Odoo MCP server to access your data.

---

## 📝 Example Workflow

**Scenario:** You're working on a sales dashboard and need customer data.

1. Open Copilot Chat (`Ctrl+Shift+I`)
2. Ask: "Get the top 10 customers by revenue in scholarixv2"
3. Copilot queries your Odoo instance
4. Results appear in chat
5. Use data in your code

---

## 🚀 Benefits Over Claude Desktop

✅ **Integrated Development** - Query Odoo while coding  
✅ **Code Context** - Copilot can see your current code  
✅ **Workspace Integration** - Uses project settings  
✅ **Faster Iteration** - No context switching  
✅ **Side-by-side** - Chat panel + code editor  

---

## 🔗 Connecting to MCP Server

The MCP server connection happens automatically when:

1. VS Code opens this workspace
2. Copilot Chat extension is installed
3. MCP server is running (`npm start`)

Optional: Configure in `settings.json` for auto-launch:

```json
{
  "mcp": {
    "autoLaunch": true,
    "serverPath": "d:\\odoo17_backup\\odoo-mcp-server\\dist\\index.js"
  }
}
```

---

## 📚 Documentation

See main docs in project root:
- [START-HERE.md](../START-HERE.md) - Quick overview
- [USAGE-GUIDE.md](../USAGE-GUIDE.md) - Complete feature guide
- [ONE-PAGE-REFERENCE.md](../ONE-PAGE-REFERENCE.md) - Cheat sheet

---

## ⚙️ Terminal Integration

VS Code's built-in terminal is configured to work with the project:

```bash
# Start the server
npm start

# Build the project
npm run build

# View logs
npm start  # Shows real-time connection status
```

---

## 🎯 Quick Reference

| Action | Shortcut | Result |
| ------ | -------- | ------ |
| Open Copilot Chat | `Ctrl+Shift+I` | Start querying Odoo |
| Format Code | `Shift+Alt+F` | Prettier formatting |
| Find in Files | `Ctrl+Shift+F` | Search project |
| Open Terminal | `` Ctrl+` `` | VS Code terminal |
| Run Build | `Ctrl+Shift+B` | Compile TypeScript |

---

## ✅ Verification

After setup, test in Copilot Chat:

```
"List all Odoo instances"
```

Should respond:
```
6 instances configured:
- scholarixv2 (v17)
- osusproperties (v17)
- eigermarvelhr (v18)
- scholarix-restaurant (v18)
- testserver-hospital (v18)
- sgctechai (v19)
```

---

**VS Code setup complete!** Start using Copilot Chat to interact with your Odoo instances. 🚀
