# Odoo MCP Server - Quick Start Guide

Get your production-grade Odoo MCP server running in minutes!

## Prerequisites

- ✅ Node.js 18+ installed
- ✅ Odoo 17, 18, or 19 instance accessible
- ✅ Cloudflare account (for production deployment)

## Option 1: Local Development (5 minutes)

### Step 1: Configure Environment

1. Copy the example environment file:
```bash
cd D:\01_WORK_PROJECTS\odoo-mcp-server
copy .env.example .env
```

2. Edit `.env` with your Odoo credentials:

**For your local Odoo 19 instance:**
```env
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin123
```

**For production instance:**
```env
ODOO_URL=https://your-odoo-domain.com
ODOO_DB=production_db
ODOO_USERNAME=api_user
ODOO_PASSWORD=your_secure_password
```

### Step 2: Start the Server

```bash
npm start
```

You should see:
```
Odoo MCP Server running
Configured instances: default
Available tools: 11
```

### Step 3: Integrate with Claude Desktop

1. Open Claude Desktop configuration:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Create if it doesn't exist

2. Add this configuration:
```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin123"
      }
    }
  }
}
```

3. Restart Claude Desktop

4. Test it! Ask Claude:
```
Can you search for all partners in Odoo?
```

## Option 2: Multiple Instances (10 minutes)

Perfect for managing multiple Odoo environments (local, staging, production).

### Step 1: Configure Multiple Instances

Edit `.env`:

```env
ODOO_INSTANCES='{
  "local": {
    "url": "http://localhost:8069",
    "db": "odoo",
    "username": "admin",
    "password": "admin123"
  },
  "production": {
    "url": "https://your-odoo-domain.com",
    "db": "production_db",
    "username": "api_user",
    "password": "secure_password"
  }
}'
```

### Step 2: Start and Test

```bash
npm start
```

### Step 3: Use with Claude

In Claude Desktop config:
```json
{
  "mcpServers": {
    "odoo-multi": {
      "command": "node",
      "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
      "env": {
        "ODOO_INSTANCES": "{\"local\":{\"url\":\"http://localhost:8069\",\"db\":\"odoo\",\"username\":\"admin\",\"password\":\"admin123\"},\"production\":{\"url\":\"https://your-domain.com\",\"db\":\"production_db\",\"username\":\"api_user\",\"password\":\"secure_password\"}}"
      }
    }
  }
}
```

Now you can specify which instance:
```
Search for customers in the production instance
```

## Option 3: Cloudflare Workers Deployment (15 minutes)

Deploy globally on Cloudflare's edge network.

### Step 1: Install Wrangler

```bash
npm install -g wrangler
```

### Step 2: Login to Cloudflare

```bash
wrangler login
```

### Step 3: Configure Secrets

```bash
cd D:\01_WORK_PROJECTS\odoo-mcp-server

# Set your Odoo credentials as secrets
wrangler secret put ODOO_URL
# Paste: https://your-odoo-domain.com

wrangler secret put ODOO_DB
# Paste: your_database_name

wrangler secret put ODOO_USERNAME
# Paste: api_user

wrangler secret put ODOO_PASSWORD
# Paste: your_secure_password
```

### Step 4: Deploy

```bash
npm run deploy
```

You'll get a URL like:
```
https://odoo-mcp-server.your-subdomain.workers.dev
```

### Step 5: Test

The worker is now live! You can use it with any MCP client.

## Common Use Cases

### 1. Search for Customers

Ask Claude:
```
Search for all customers in Odoo with email addresses
```

Claude will use:
```json
{
  "tool": "odoo_search_read",
  "instance": "default",
  "model": "res.partner",
  "domain": [["customer_rank", ">", 0], ["email", "!=", false]],
  "fields": ["name", "email", "phone", "country_id"]
}
```

### 2. Get Sales Orders

```
Show me all sale orders from January 2024
```

Claude will use:
```json
{
  "tool": "odoo_search_read",
  "instance": "default",
  "model": "sale.order",
  "domain": [["date_order", ">=", "2024-01-01"], ["date_order", "<", "2024-02-01"]],
  "fields": ["name", "partner_id", "amount_total", "state"]
}
```

### 3. Create a Contact

```
Create a new customer named "Acme Corp" with email info@acme.com
```

Claude will use:
```json
{
  "tool": "odoo_create",
  "instance": "default",
  "model": "res.partner",
  "values": {
    "name": "Acme Corp",
    "email": "info@acme.com",
    "is_company": true,
    "customer_rank": 1
  }
}
```

### 4. Generate Invoice PDF

```
Generate a PDF for invoice #100
```

Claude will use:
```json
{
  "tool": "odoo_generate_report",
  "instance": "default",
  "reportName": "account.report_invoice",
  "ids": [100]
}
```

### 5. Confirm Sale Order

```
Confirm sale order SO001
```

Claude will search for the order, then use:
```json
{
  "tool": "odoo_workflow_action",
  "instance": "default",
  "model": "sale.order",
  "ids": [42],
  "action": "action_confirm"
}
```

## Verification Checklist

After setup, verify everything works:

- [ ] Server starts without errors
- [ ] Claude Desktop recognizes the MCP server
- [ ] Can search for records
- [ ] Can read record details
- [ ] Can create records (test on non-critical data)
- [ ] Error messages are clear and helpful

## Troubleshooting

### "Authentication failed"
- Double-check Odoo URL, database name, username, password
- Verify Odoo is running and accessible
- Test XML-RPC: `curl http://localhost:8069/xmlrpc/2/common`

### "Cannot connect to Odoo"
- Verify Odoo is running: open URL in browser
- Check firewall rules
- For remote Odoo, ensure it's accessible from your machine

### Claude Desktop doesn't see the server
- Restart Claude Desktop after changing config
- Check config file path
- Verify JSON syntax (use JSONLint.com)
- Check logs in Claude Desktop

### "Tool not found"
- Verify MCP server is running
- Check that Claude Desktop config points to correct path
- Restart Claude Desktop

## Next Steps

1. ✅ **Read the full README**: `README.md` has comprehensive documentation
2. ✅ **Review deployment guide**: `DEPLOYMENT-GUIDE.md` for production setup
3. ✅ **Explore tools**: Try all 11 tools with different models
4. ✅ **Security**: Create dedicated Odoo API user with minimal permissions
5. ✅ **Monitor**: Set up logging and monitoring for production

## Available Tools

Your MCP server provides these tools:

1. **odoo_search** - Search records by domain
2. **odoo_search_read** - Search and read in one call
3. **odoo_read** - Read specific record IDs
4. **odoo_create** - Create new records
5. **odoo_update** - Update existing records
6. **odoo_delete** - Delete records
7. **odoo_execute** - Execute arbitrary methods
8. **odoo_count** - Count records matching domain
9. **odoo_workflow_action** - Execute workflow actions
10. **odoo_generate_report** - Generate PDF reports
11. **odoo_get_model_metadata** - Get model field definitions

## Common Models

- `res.partner` - Contacts/Customers/Vendors
- `sale.order` - Sales Orders
- `account.move` - Invoices/Bills
- `product.product` - Products
- `stock.picking` - Inventory Transfers
- `project.task` - Project Tasks
- `crm.lead` - CRM Leads
- `purchase.order` - Purchase Orders

See `README.md` for complete model list and examples.

## Support

- 📖 Full documentation: `README.md`
- 🚀 Deployment guide: `DEPLOYMENT-GUIDE.md`
- 🔧 Odoo docs: https://www.odoo.com/documentation
- 💬 MCP docs: https://modelcontextprotocol.io

---

**Ready to go!** Your production-grade Odoo MCP server is configured and ready to use. 🎉
