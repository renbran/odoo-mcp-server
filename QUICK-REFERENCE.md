# 🎯 Odoo MCP Server - Quick Reference Card

## 📦 Installation (One-Time Setup)

```bash
cd d:\01_WORK_PROJECTS\odoo-mcp-server
npm install
npm run build
cp .env.example .env
# Edit .env with your Odoo credentials
```

## 🔧 Configuration

### Option 1: Single Instance (.env file)

```env
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

### Option 2: Multiple Instances

```json
ODOO_INSTANCES={
  "prod":{"url":"https://prod.odoo.com","db":"prod_db","username":"admin","password":"pass"},
  "dev":{"url":"http://localhost:8069","db":"dev_db","username":"admin","password":"admin"}
}
```

## 🚀 Quick Start Commands

```bash
# Test connection
npm run dev

# Build
npm run build

# Production start
npm start
```

Or use the helper script:

```powershell
.\start.ps1 test     # Test connection
.\start.ps1 config   # Edit configuration  
.\start.ps1 claude   # Get Claude setup info
```

## 🤖 Claude Desktop Setup

**Config File Location:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "your_database",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin"
      }
    }
  }
}
```

**After editing:** Restart Claude Desktop completely

## 📚 Available Tools (11 Total)

| Tool | Usage |
|------|-------|
| `odoo_search` | Find record IDs |
| `odoo_search_read` | Find + fetch data |
| `odoo_read` | Get record details by ID |
| `odoo_create` | Create new record |
| `odoo_update` | Update existing record |
| `odoo_delete` | Delete record |
| `odoo_execute` | Run custom method |
| `odoo_count` | Count matching records |
| `odoo_workflow_action` | Execute button/action |
| `odoo_generate_report` | Generate PDF |
| `odoo_get_model_metadata` | Get field definitions |

## 💬 Example Prompts for Claude

```
"Search for all customers in Odoo"

"Show me draft sales orders from this month"

"Create a new partner named 'Acme Corp' with email acme@example.com"

"Update sale order SO001 status to confirmed"

"What fields are available on the account.move model?"

"Generate invoice PDF for invoice INV/2024/0001"

"Count how many products are in category 'Electronics'"
```

## 🔍 Common Odoo Models

```
res.partner          # Customers/Vendors
sale.order           # Sales Orders
sale.order.line      # Order Lines
account.move         # Invoices/Bills
account.move.line    # Invoice Lines
product.product      # Products
product.template     # Product Templates
stock.picking        # Deliveries
crm.lead             # Leads/Opportunities
project.task         # Tasks
hr.employee          # Employees
purchase.order       # Purchase Orders
```

## 🎨 Domain Filter Examples

```javascript
// Simple equality
[['name', '=', 'John']]

// Greater than
[['amount_total', '>', 1000]]

// In list
[['state', 'in', ['draft', 'sent']]]

// Contains (case-insensitive)
[['email', 'ilike', '@gmail.com']]

// AND (default)
[['state', '=', 'sale'], ['amount_total', '>', 1000]]

// OR
['|', ['state', '=', 'draft'], ['state', '=', 'sent']]

// Complex: US customers with orders > $1000
['&', 
  ['partner_id.country_id.code', '=', 'US'],
  ['amount_total', '>', 1000]
]
```

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Cannot find module" | `npm install && npm run build` |
| "Authentication failed" | Check credentials in .env |
| "Connection refused" | Ensure Odoo is running |
| "Unknown instance" | Use instance name from config |
| Claude doesn't see MCP | Restart Claude, check JSON syntax |

## 📁 Project Structure

```
odoo-mcp-server/
├── src/
│   ├── index.ts          # MCP server entry
│   ├── odoo-client.ts    # Odoo XML-RPC client
│   ├── tools.ts          # Tool definitions
│   └── types.ts          # TypeScript types
├── dist/                 # Built files (generated)
├── .env                  # Your credentials
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── README.md             # Full documentation
├── SETUP-GUIDE.md        # Setup instructions
└── start.ps1             # Helper script
```

## 🔗 Useful Links

- 📖 [Full README](./README.md)
- 📋 [Setup Guide](./SETUP-GUIDE.md)
- 🌐 [MCP Documentation](https://modelcontextprotocol.io)
- 📚 [Odoo API Docs](https://www.odoo.com/documentation/17.0/developer/api/external_api.html)

---

**Quick Help:** `.\start.ps1 help`
