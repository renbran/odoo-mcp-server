# Odoo MCP Server - Setup & Usage Documentation

## 🎯 Overview

This document covers the complete setup and usage of the **Odoo MCP Server** with multi-database support (6 Odoo instances across v17, v18, v19).

### What You Have
- **6 Production Odoo Instances** connected via Model Context Protocol (MCP)
- **11 Comprehensive Tools** for CRUD operations, searches, workflows, reports, and metadata
- **Claude Desktop Integration** for AI-powered Odoo automation and queries
- **ES Module Architecture** optimized for Node.js and Cloudflare Workers

---

## 📋 Setup Status

✅ **Completed:**
- Dependencies installed (npm install)
- TypeScript compiled to ES modules
- `.env` file configured with all 6 instances
- Server tested and running locally
- Claude Desktop config prepared

**Your 6 Connected Odoo Instances:**

| Instance | Version | Provider | Status |
|----------|---------|----------|--------|
| **scholarixv2** | v17 | CloudPepper | ✅ Active |
| **osusproperties** | v17 | CloudPepper | ✅ Active |
| **eigermarvelhr** | v18 | CloudPepper | ✅ Active |
| **scholarix-restaurant** | v18 | CloudPepper | ✅ Active |
| **testserver-hospital** | v18 | CloudPepper | ✅ Active |
| **sgctechai** | v19 | On-Premise | ✅ Active |

---

## 🚀 Final Setup Steps

### Step 1: Copy Claude Desktop Config

Copy the config file to your Claude Desktop settings:

**Source:**
```
d:\odoo17_backup\odoo-mcp-server\claude_desktop_config.json
```

**Destination:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Windows Path Expanded:**
```
C:\Users\{YourUsername}\AppData\Roaming\Claude\claude_desktop_config.json
```

### Step 2: Restart Claude Desktop

1. Close Claude Desktop completely
2. Wait 3 seconds
3. Reopen Claude Desktop
4. Check bottom-left corner for "odoo-multi" server status (should show ✓)

### Step 3: Verify Connection

Ask Claude:
```
What Odoo instances are available?
```

Expected response:
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

## 🛠️ Available Tools

Your MCP server provides **11 production-ready tools**:

### 1. **odoo_search** - Find Records
Search for records matching a domain filter.

**Usage:**
```
Search for all customers in scholarixv2 with email addresses
```

**Tool Parameters:**
```json
{
  "instance": "scholarixv2",
  "model": "res.partner",
  "domain": [["customer_rank", ">", 0], ["email", "!=", false]],
  "fields": ["name", "email", "phone", "country_id"],
  "limit": 50,
  "order": "name ASC"
}
```

### 2. **odoo_search_read** - Search & Read (One Call)
More efficient for getting record details in one operation.

**Usage:**
```
Get the 10 most recent sales orders from eigermarvelhr
```

**Tool Parameters:**
```json
{
  "instance": "eigermarvelhr",
  "model": "sale.order",
  "domain": [["state", "!=", "cancel"]],
  "fields": ["name", "partner_id", "amount_total", "state", "date_order"],
  "limit": 10,
  "order": "date_order DESC"
}
```

### 3. **odoo_read** - Read Specific Records
Get details by record IDs.

**Usage:**
```
Read customer details for IDs 5, 10, 15 from scholarix-restaurant
```

**Tool Parameters:**
```json
{
  "instance": "scholarix-restaurant",
  "model": "res.partner",
  "ids": [5, 10, 15],
  "fields": ["name", "email", "phone", "street", "city", "country_id"]
}
```

### 4. **odoo_create** - Create Records
Create new records in any model.

**Usage:**
```
Create a new customer "Global Education Ltd" in osusproperties
```

**Tool Parameters:**
```json
{
  "instance": "osusproperties",
  "model": "res.partner",
  "values": {
    "name": "Global Education Ltd",
    "email": "contact@globaledu.com",
    "phone": "+1-800-123-4567",
    "is_company": true,
    "customer_rank": 1
  }
}
```

### 5. **odoo_update** - Update Records
Modify existing records.

**Usage:**
```
Update order SO001 in testserver-hospital with new notes
```

**Tool Parameters:**
```json
{
  "instance": "testserver-hospital",
  "model": "sale.order",
  "ids": [42],
  "values": {
    "note": "Updated: Priority handling required",
    "client_order_ref": "PO-2024-001"
  }
}
```

### 6. **odoo_delete** - Delete Records
Remove records (use with caution).

**Usage:**
```
Delete old test records from sgctechai
```

**Tool Parameters:**
```json
{
  "instance": "sgctechai",
  "model": "project.task",
  "ids": [100, 101, 102]
}
```

### 7. **odoo_execute** - Execute Methods
Call any model method with custom parameters.

**Usage:**
```
Confirm sale order in eigermarvelhr using action_confirm
```

**Tool Parameters:**
```json
{
  "instance": "eigermarvelhr",
  "model": "sale.order",
  "method": "action_confirm",
  "args": [[42]]
}
```

### 8. **odoo_count** - Count Records
Get total count matching a domain.

**Usage:**
```
How many active customers in scholarixv2?
```

**Tool Parameters:**
```json
{
  "instance": "scholarixv2",
  "model": "res.partner",
  "domain": [["customer_rank", ">", 0], ["active", "=", true]]
}
```

### 9. **odoo_workflow_action** - Execute Workflow Actions
Click workflow buttons (confirm, validate, post, etc.).

**Usage:**
```
Post invoice #INV001 in osusproperties
```

**Tool Parameters:**
```json
{
  "instance": "osusproperties",
  "model": "account.move",
  "ids": [100],
  "action": "action_post"
}
```

### 10. **odoo_generate_report** - Generate PDFs
Create PDF reports for any report template.

**Usage:**
```
Generate invoice PDF for order #100 in scholarix-restaurant
```

**Tool Parameters:**
```json
{
  "instance": "scholarix-restaurant",
  "reportName": "account.report_invoice",
  "ids": [100]
}
```

### 11. **odoo_get_model_metadata** - Get Field Definitions
See all fields available on any model.

**Usage:**
```
Show me all fields on the sale.order model in eigermarvelhr
```

**Tool Parameters:**
```json
{
  "instance": "eigermarvelhr",
  "model": "sale.order"
}
```

---

## 💡 Common Use Cases & Examples

### Use Case 1: Bulk Customer Search Across Instances

**Ask Claude:**
```
Search for all B2B customers (is_company=true) in scholarixv2 and osusproperties that have sales in the last 30 days
```

**What Claude will do:**
- Search `res.partner` model in both instances
- Filter by is_company=true
- Find linked sale orders within date range
- Return consolidated results

### Use Case 2: Create Sales Order in Multiple Instances

**Ask Claude:**
```
Create a new sales order for customer "Tech Corp" for $50,000 in both eigermarvelhr and testserver-hospital
```

**What Claude will do:**
- Find "Tech Corp" customer in both instances (or create if missing)
- Create sale.order records in each
- Set amount_total to 50,000
- Return order IDs and confirmation

### Use Case 3: Generate Monthly Reports

**Ask Claude:**
```
Generate invoice PDFs for all invoices posted in January 2024 in scholarix-restaurant
```

**What Claude will do:**
- Search account.move model for January 2024, state='posted'
- Generate PDF for each using odoo_generate_report
- Return file references

### Use Case 4: Cross-Instance Sync

**Ask Claude:**
```
Get all customers from scholarixv2 and sync them to osusproperties (create if missing, update if exists)
```

**What Claude will do:**
- Read all customers from scholarixv2
- Check for existence in osusproperties
- Create new or update existing records
- Return sync summary

### Use Case 5: Workflow Automation

**Ask Claude:**
```
In testserver-hospital, find all draft sale orders for "Hospital Admin" and confirm them
```

**What Claude will do:**
- Search for draft orders for partner "Hospital Admin"
- Execute action_confirm on each
- Return confirmation status

---

## 🔍 Domain Filter Syntax Guide

Domain filters follow Odoo's standard syntax. Learn them to unlock powerful searches:

### Basic Operators

```python
# Exact match
[['name', '=', 'John Doe']]

# Not equal
[['state', '!=', 'cancel']]

# Greater/Less than
[['amount_total', '>', 1000]]
[['amount_total', '<', 500]]
[['amount_total', '>=', 1000]]

# Contains text (case-insensitive)
[['email', 'like', '@company.com']]

# In list
[['state', 'in', ['draft', 'posted']]]

# Not in list
[['state', 'not in', ['cancel', 'archived']]]

# Is/Is not set
[['email', '!=', false]]  # Has email
[['email', '=', false]]   # No email
```

### Logical Operators

```python
# AND (both conditions must be true)
['&',
  ['name', '=', 'John'],
  ['country_id.code', '=', 'US']
]

# OR (at least one must be true)
['|',
  ['name', 'like', 'John'],
  ['email', 'like', 'john@']
]

# NOT (negate a condition)
['!', ['state', '=', 'cancel']]
```

### Complex Filters

```python
# Find US customers with orders over $5000
['&',
  ['partner_id.country_id.code', '=', 'US'],
  '|',
  ['amount_total', '>', 5000],
  ['state', '=', 'pending']
]

# Find B2B customers from last 3 months (draft or confirmed)
['&',
  ['is_company', '=', true],
  '&',
  ['date_order', '>=', '2024-10-13'],
  ['state', 'in', ['draft', 'confirmed']]
]
```

### Related Fields (Dot Notation)

```python
# Filter by related partner's country
[['partner_id.country_id.code', '=', 'US']]

# Filter by company name
[['company_id.name', 'like', 'Global']]

# Filter by sales team
[['team_id.name', '=', 'Direct Sales']]
```

---

## 📊 Common Odoo Models Reference

### Sales & CRM
- `sale.order` - Sales Orders
- `sale.order.line` - Order Lines
- `crm.lead` - CRM Leads
- `crm.team` - Sales Teams

### Accounting
- `account.move` - Invoices & Bills
- `account.move.line` - Invoice Lines
- `account.payment` - Payments
- `account.journal` - Journals

### Inventory
- `stock.picking` - Transfers
- `stock.move` - Stock Moves
- `product.product` - Products
- `product.template` - Product Templates

### Contacts
- `res.partner` - Customers/Vendors/Contacts
- `res.company` - Companies
- `res.users` - User Accounts

### HR
- `hr.employee` - Employees
- `hr.department` - Departments
- `hr.leave` - Time Off

### Projects
- `project.project` - Projects
- `project.task` - Tasks

### Purchase
- `purchase.order` - Purchase Orders
- `purchase.order.line` - PO Lines

---

## 🔐 Security Best Practices

### Credentials Management

1. **Never share `.env` file** - Contains database credentials
2. **Use strong passwords** - 16+ characters with mixed case, numbers, symbols
3. **Rotate credentials regularly** - At least quarterly
4. **Create API users** - Don't use admin accounts; create dedicated API users with minimal permissions

### Odoo API User Setup

In each Odoo instance, create a dedicated API user:

**Steps:**
1. Go to Settings > Users
2. Create new user (e.g., "Claude API User")
3. Set password (minimum 16 characters)
4. Grant access to necessary models only (not admin)
5. Add to appropriate groups (Sales, Accounting, etc.)
6. Update `.env` with new credentials

### Safe Operations

- **Test on staging first** - Use testserver-hospital for validation
- **Backup before bulk changes** - Always backup before odoo_update or odoo_delete
- **Use read-only where possible** - Prefer search/read over create/update
- **Log important actions** - Keep audit trail of who changed what

---

## 🐛 Troubleshooting

### Problem: "Instance not found"

**Solution:** Check spelling matches exactly:
```
✅ Correct: scholarixv2
❌ Wrong: scholarix-v2, scholarix_v2, Scholarixv2
```

**List all instances:**
```
Ask Claude: What instances are configured?
```

### Problem: "Authentication failed"

**Causes & Solutions:**

1. **Wrong password**
   - Verify credentials in `.env`
   - Check for trailing spaces in passwords
   - Test login in Odoo UI directly

2. **User doesn't exist**
   - Verify username in Odoo UI
   - Create API user if missing

3. **User lacks permissions**
   - Check user groups in Odoo
   - Add "Sales" or "Accounting" groups as needed
   - Grant model access rights

### Problem: "Model not found"

**Solution:**
1. Verify model name (use exact name from Odoo, e.g., `res.partner` not `customer`)
2. Check if model exists in this Odoo version:
   ```
   Ask Claude: Is sale.analytic.account available in eigermarvelhr?
   ```

### Problem: "Field does not exist"

**Solution:**
1. Use `odoo_get_model_metadata` to see available fields
2. Ask Claude:
   ```
   Show all fields on res.partner in scholarixv2
   ```

### Problem: Claude can't access instances

**Solution:**
1. Ensure Claude Desktop is restarted after config change
2. Check Claude Desktop logs: **Hamburger ☰ > Logs**
3. Verify config file path: `%APPDATA%\Claude\claude_desktop_config.json`
4. Validate JSON: Use https://jsonlint.com/

### Problem: "Connection timeout"

**Causes:**
- Network issue to Odoo server
- Odoo instance is down
- Firewall blocking connection

**Solutions:**
```bash
# Test connectivity to each instance
curl -I https://erp.sgctech.ai
curl -I https://erposus.com
curl -I https://eigermarvelhr.com
```

---

## 📈 Performance Tips

### Optimize Searches

```python
# ❌ Slow - Gets all records then filters client-side
[['state', 'in', ['draft', 'confirmed', 'sale', 'done']]]

# ✅ Fast - Server filters efficiently
['|', '|', ['state', '=', 'draft'], ['state', '=', 'confirmed']]

# ❌ Slow - No limit specified
domain = [['customer_rank', '>', 0]]

# ✅ Fast - Limited results
domain = [['customer_rank', '>', 0]]
limit = 100
```

### Use Specific Fields

```python
# ❌ Slow - Gets all fields (many might be unused)
fields = []  # Default: all fields

# ✅ Fast - Only needed fields
fields = ["name", "email", "phone", "country_id"]
```

### Batch Operations

```python
# ❌ Slow - Multiple API calls
for customer_id in [1, 2, 3, 4, 5]:
  Read customer individually

# ✅ Fast - Single API call
Read customers with IDs [1, 2, 3, 4, 5]
```

---

## 🎓 Learning Resources

### Odoo Documentation
- [Odoo Models & Fields](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html)
- [Domain Filter Syntax](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#search)
- [XML-RPC API](https://www.odoo.com/documentation/17.0/developer/reference/external_api.html)

### MCP Protocol
- [Model Context Protocol Docs](https://modelcontextprotocol.io/)
- [Building MCP Servers](https://modelcontextprotocol.io/quickstart/server)

### Claude Resources
- [Using Claude with MCP](https://claude.ai/docs)
- [Prompt Engineering Guide](https://github.com/anthropics/prompt-engineering)

---

## ⚙️ Advanced Configuration

### Adding More Instances

Edit `.env`:
```bash
ODOO_INSTANCES='{
  "existing_instance": {...},
  "new_instance": {
    "url": "https://new-odoo.com",
    "db": "new_db",
    "username": "admin",
    "password": "password123"
  }
}'
```

Then restart the server:
```bash
npm run build && npm start
```

### Cloudflare Workers Deployment

For production edge deployment:

```bash
# Install Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Set secrets
wrangler secret put ODOO_INSTANCES

# Deploy
npm run deploy
```

### Timeout Configuration

Edit `.env`:
```bash
# Request timeout in milliseconds (default: 30000)
ODOO_TIMEOUT=60000

# Retry attempts for failed requests (default: 3)
ODOO_MAX_RETRIES=5
```

---

## 📞 Support & Contact

**Issues or Questions?**

1. Check troubleshooting section above
2. Review domain filter examples
3. Verify credentials in `.env`
4. Check Claude Desktop logs

**Server Status:**
```bash
# Check if running
cd d:\odoo17_backup\odoo-mcp-server
npm start  # Should show all 6 instances

# View environment
cat .env | grep ODOO
```

---

## ✅ Checklist

Before using in production:

- [ ] All 6 instances verified and accessible
- [ ] Claude Desktop config installed and restarted
- [ ] Can ask Claude "What instances are configured?"
- [ ] Tested at least one search query
- [ ] Tested create/update on non-critical data
- [ ] Set up automated backups for each instance
- [ ] Created dedicated API users (not using admin)
- [ ] Documented instance-specific access controls
- [ ] Team members aware of this tool
- [ ] Monitoring/alerts configured (optional)

---

**🎉 Setup Complete!**

You now have a production-grade MCP server connecting 6 Odoo instances with 11 powerful tools accessible through Claude Desktop.

**Next Steps:**
1. Restart Claude Desktop
2. Ask: "What Odoo instances are available?"
3. Try a simple search: "Show me the top 5 customers in scholarixv2"
4. Explore the tools based on your needs

Happy automating! 🚀
