# VS Code Configuration for Odoo MCP Server

This folder contains VS Code workspace configuration for the Odoo MCP Server project.

## 📁 Files in This Folder

### **settings.json**
Workspace-specific VS Code settings:
- Markdown formatter configuration
- File exclusions (node_modules, .wrangler)
- Code formatting rules

### **extensions.json**
Recommended VS Code extensions for this project:
- GitHub Copilot
- GitHub Copilot Chat
- TypeScript Nightly
- Prettier - Code Formatter
- ESLint

### **launch.json**
Debug configurations for running the Odoo MCP Server:
- Launches with TypeScript source maps
- Auto-compiles before running
- Loads all Odoo instance credentials
- Uses integrated terminal for output

### **tasks.json**
VS Code build tasks:
- `npm: install` - Install dependencies
- `npm: build` - Compile TypeScript (default build)
- `npm: start` - Run the server
- `npm: dev` - Development mode

### **mcp.json**
MCP server configuration (optional):
- Server path
- Environment variables
- Instance credentials

### **VS-CODE-SETUP.md**
Step-by-step VS Code setup guide.

---

## 🚀 Quick Start in VS Code

### 1. Open the Project
```bash
code d:\odoo17_backup\odoo-mcp-server
```

### 2. Install Extensions
When prompted, click "Install" for recommended extensions.

### 3. Start the Server
Press `Ctrl+Shift+B` to run the default build task.

Or use the terminal:
```bash
npm start
```

### 4. Use Copilot Chat
Press `Ctrl+Shift+I` to open Copilot Chat.

Ask questions about your Odoo data:
```
"Find customers in scholarixv2"
"How many orders in eigermarvelhr?"
```

---

## 🐛 Debugging

### Debug the MCP Server
1. Open `.vscode/launch.json`
2. Click "Run" (or press F5)
3. Server starts with debugger attached
4. Set breakpoints in `src/` files
5. Step through code execution

### Debug Configuration
The launch configuration:
- Compiles TypeScript first
- Loads environment variables
- Shows output in integrated terminal
- Supports breakpoints and watches

---

## 🔨 Build Tasks

### Run a Task
Press `Ctrl+Shift+P` and search for "Tasks: Run Task"

Available tasks:
- **npm: build** (default) - Compile TypeScript to JavaScript
- **npm: start** - Run the compiled server
- **npm: dev** - Development mode (Wrangler)
- **npm: install** - Install dependencies

---

## ⚙️ Keyboard Shortcuts

| Action | Shortcut |
| ------ | -------- |
| Open Copilot Chat | `Ctrl+Shift+I` |
| Run Build Task | `Ctrl+Shift+B` |
| Run Any Task | `Ctrl+Shift+P` → "Tasks: Run Task" |
| Open Terminal | `` Ctrl+` `` |
| Format Code | `Shift+Alt+F` |
| Find in Files | `Ctrl+Shift+F` |
| Debug (F5) | `F5` |
| Toggle Sidebar | `Ctrl+B` |

---

## 📝 Settings Explained

### Markdown Settings
```json
"[markdown]": {
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true
}
```
Automatically formats markdown files on save.

### File Exclusions
```json
"files.exclude": {
  "node_modules": true,
  ".wrangler": true
}
```
Hides build artifacts from the file explorer.

---

## 🔗 Integration with Copilot

When you open Copilot Chat (`Ctrl+Shift+I`), it automatically:
1. Detects this is an MCP project
2. Loads the Odoo MCP Server configuration
3. Connects to all 6 Odoo instances
4. Makes 11 tools available

### Ask Copilot Questions Like:
```
"Search for customers in scholarixv2"
"Create a sales order in eigermarvelhr"
"Generate invoice PDF for order #100"
"How many unpaid invoices are there?"
"Show me the sale.order model fields"
```

---

## 📚 Full Documentation

See parent folder documentation:
- **START-HERE.md** - Quick overview (2 min)
- **QUICK-START.md** - Setup guide (5 min)
- **USAGE-GUIDE.md** - Complete features (30 min)
- **ONE-PAGE-REFERENCE.md** - Cheat sheet
- **SETUP-CHECKLIST.md** - Verification guide

---

## ✅ Verify Setup

In VS Code terminal (`` Ctrl+` ``):

```bash
# Start the server
npm start
```

Expected output:
```
[dotenv@17.2.3] injecting env (3) from .env
Odoo MCP Server running
Configured instances: scholarixv2, osusproperties, eigermarvelhr, scholarix-restaurant, testserver-hospital, sgctechai
Available tools: 11
```

Then in Copilot Chat ask:
```
"What Odoo instances are available?"
```

---

## 🆘 Troubleshooting

### Extensions Not Installing
1. Close VS Code
2. Open Command Palette: `Ctrl+Shift+P`
3. Search: "Extensions: Install from Workspace Folder"

### Build Fails
1. Open terminal: `` Ctrl+` ``
2. Run: `npm install`
3. Run: `npm run build`

### Server Won't Start
1. Check if port 8069 is available
2. Verify `.env` file exists with credentials
3. Check terminal for error messages

### Copilot Chat Not Showing MCP Server
1. Restart VS Code completely
2. Verify extensions are installed
3. Check Output panel for "MCP" channel

---

## 🎯 Recommended Workflow

### Development
1. Open folder in VS Code: `code .`
2. Edit TypeScript in `src/`
3. Press `Ctrl+Shift+B` to build
4. Test in Copilot Chat: `Ctrl+Shift+I`

### Debugging
1. Set breakpoint in `src/` file
2. Press `F5` to start debugger
3. Step through code with debugger controls
4. Check variables in watch panel

### Testing
1. Open terminal: `` Ctrl+` ``
2. Run: `npm start`
3. Open Copilot Chat: `Ctrl+Shift+I`
4. Test queries against live Odoo instances

---

## 📖 VS Code Resources

- [VS Code User Guide](https://code.visualstudio.com/docs)
- [Debug TypeScript](https://code.visualstudio.com/docs/typescript/typescript-debugging)
- [Tasks Reference](https://code.visualstudio.com/docs/editor/tasks)
- [Copilot Chat Help](https://github.com/features/copilot)

---

**VS Code is fully configured!** Start developing with Copilot integration. 🚀
