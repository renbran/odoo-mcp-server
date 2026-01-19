# Odoo MCP Server

Production-grade Model Context Protocol (MCP) server for Odoo 17-19, providing comprehensive API access to Odoo instances with context-aware helpers, multi-instance support, and Cloudflare Workers deployment.

## 📚 Documentation

### 🚀 Getting Started
- **[QUICK-START.md](QUICK-START.md)** - 2-minute setup (copy config & restart Claude)
- **[IMPLEMENTATION-SUMMARY.md](IMPLEMENTATION-SUMMARY.md)** - What's been built & project stats

### 📖 Complete Guides
- **[USAGE-GUIDE.md](USAGE-GUIDE.md)** - Comprehensive 3,500+ word guide with 30 examples
- **[SETUP-CHECKLIST.md](SETUP-CHECKLIST.md)** - 6-phase verification & troubleshooting
- **[DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)** - Production deployment on Cloudflare

### 📋 Reference
- **[PROJECT-SUMMARY.md](PROJECT-SUMMARY.md)** - Project overview & next steps
- **[QUICKSTART.md](QUICKSTART.md)** - Original quickstart guide

---

## ⚡ Quick Setup (2 minutes)

**Step 1:** Copy config to Claude Desktop
```bash
copy claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
```

**Step 2:** Restart Claude Desktop

**Step 3:** Ask Claude
```
What Odoo instances are available?
```

✅ Done! See [QUICK-START.md](QUICK-START.md) for details.

---

## Features

- **Multi-Instance Support**: Connect to multiple Odoo instances (production, staging, local)
- **Comprehensive Operations**: CRUD, search, filtering, reports, workflow actions
- **Production-Ready**: Retry logic, error handling, connection pooling, timeouts
- **Context-Aware**: Built-in helpers for common Odoo models and domain syntax
- **Odoo 17-19 Compatible**: Supports all Odoo versions from 17 to 19
- **Cloudflare Workers**: Deploy anywhere with edge computing
- **Type-Safe**: Full TypeScript implementation with Zod validation

---

## Your 6 Connected Instances

| Instance | Version | Provider | Status |
| -------- | ------- | -------- | ------ |
| scholarixv2 | v17 | CloudPepper | ✅ Active |
| osusproperties | v17 | CloudPepper | ✅ Active |
| eigermarvelhr | v18 | CloudPepper | ✅ Active |
| scholarix-restaurant | v18 | CloudPepper | ✅ Active |
| testserver-hospital | v18 | CloudPepper | ✅ Active |
| sgctechai | v19 | On-Premise | ✅ Active |

---

## 11 Available Tools

### Prerequisites

- Node.js 18+ (for local development)
- Cloudflare account (for production deployment)
- Odoo 17, 18, or 19 instance(s)

### Setup

1. Clone or download this repository:
```bash
cd D:\01_WORK_PROJECTS\odoo-mcp-server
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Odoo credentials
```

### Configuration

#### Option 1: Multiple Instances (Recommended)

Set `ODOO_INSTANCES` environment variable with JSON configuration:

```bash
ODOO_INSTANCES='{
  "production": {
    "url": "https://odoo.example.com",
    "db": "production_db",
    "username": "admin",
    "password": "your_secure_password"
  },
  "staging": {
    "url": "https://staging.odoo.example.com",
    "db": "staging_db",
    "username": "admin",
    "password": "your_secure_password"
  },
  "local": {
    "url": "http://localhost:8069",
    "db": "odoo",
    "username": "admin",
    "password": "admin"
  }
}'
```

#### Option 2: Single Instance

Set individual environment variables:

```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

## Usage

### Local Development

Run the MCP server locally:

```bash
npm run dev
```

Or for production mode:

```bash
npm start
```

### MCP Tools

The server provides 11 comprehensive tools:

#### 1. odoo_search
Search for records with domain filters.

```json
{
  "instance": "production",
  "model": "res.partner",
  "domain": [["is_company", "=", true], ["country_id.code", "=", "US"]],
  "fields": ["name", "email", "phone"],
  "limit": 10,
  "order": "name ASC"
}
```

#### 2. odoo_search_read
Search and read records in one operation.

```json
{
  "instance": "production",
  "model": "sale.order",
  "domain": [["state", "=", "sale"], ["date_order", ">=", "2024-01-01"]],
  "fields": ["name", "partner_id", "amount_total", "state"],
  "limit": 50
}
```

#### 3. odoo_read
Read specific records by IDs.

```json
{
  "instance": "production",
  "model": "account.move",
  "ids": [1, 2, 3],
  "fields": ["name", "partner_id", "amount_total", "state", "invoice_date"]
}
```

#### 4. odoo_create
Create new records.

```json
{
  "instance": "production",
  "model": "res.partner",
  "values": {
    "name": "New Customer",
    "email": "customer@example.com",
    "phone": "+1234567890",
    "is_company": true
  }
}
```

#### 5. odoo_update
Update existing records.

```json
{
  "instance": "production",
  "model": "sale.order",
  "ids": [42],
  "values": {
    "note": "Updated order notes",
    "client_order_ref": "PO-2024-001"
  }
}
```

#### 6. odoo_delete
Delete records (use with caution).

```json
{
  "instance": "production",
  "model": "project.task",
  "ids": [100, 101]
}
```

#### 7. odoo_execute
Execute arbitrary methods on models.

```json
{
  "instance": "production",
  "model": "sale.order",
  "method": "action_confirm",
  "args": [[42]]
}
```

#### 8. odoo_count
Count records matching domain.

```json
{
  "instance": "production",
  "model": "res.partner",
  "domain": [["customer_rank", ">", 0]]
}
```

#### 9. odoo_workflow_action
Execute workflow actions/buttons.

```json
{
  "instance": "production",
  "model": "account.move",
  "ids": [100],
  "action": "action_post"
}
```

#### 10. odoo_generate_report
Generate PDF reports.

```json
{
  "instance": "production",
  "reportName": "account.report_invoice",
  "ids": [100, 101]
}
```

#### 11. odoo_get_model_metadata
Get model field definitions and metadata.

```json
{
  "instance": "production",
  "model": "sale.order"
}
```

### Context-Aware Prompts

The server includes helpful prompts:

- `odoo_common_models`: List of commonly used Odoo models
- `odoo_domain_filters`: Guide for domain filter syntax with examples

## Cloudflare Workers Deployment

### Prerequisites

1. Install Wrangler CLI:
```bash
npm install -g wrangler
```

2. Login to Cloudflare:
```bash
wrangler login
```

### Configure Secrets

Set your Odoo credentials as Cloudflare secrets:

```bash
# For single instance
wrangler secret put ODOO_URL
wrangler secret put ODOO_DB
wrangler secret put ODOO_USERNAME
wrangler secret put ODOO_PASSWORD

# Or for multiple instances
wrangler secret put ODOO_INSTANCES
```

### Deploy

```bash
npm run deploy
```

Your MCP server will be deployed to Cloudflare Workers and accessible globally.

### Production Configuration

Edit `wrangler.toml` for production settings:

```toml
[env.production]
vars = { ENVIRONMENT = "production" }

[limits]
cpu_ms = 50000

[observability]
enabled = true
```

## Common Odoo Models

### Sales & CRM
- `sale.order` - Sales Orders
- `sale.order.line` - Sales Order Lines
- `crm.lead` - CRM Leads/Opportunities
- `crm.team` - Sales Teams

### Accounting & Invoicing
- `account.move` - Invoices & Bills
- `account.move.line` - Invoice/Bill Lines
- `account.payment` - Payments
- `account.journal` - Journals

### Inventory & Products
- `stock.picking` - Transfers
- `stock.move` - Stock Moves
- `product.product` - Products (variants)
- `product.template` - Product Templates

### Partners & Contacts
- `res.partner` - Contacts/Customers/Vendors
- `res.company` - Companies
- `res.users` - Users

### HR
- `hr.employee` - Employees
- `hr.department` - Departments
- `hr.leave` - Time Off

### Projects
- `project.project` - Projects
- `project.task` - Tasks

### Purchase
- `purchase.order` - Purchase Orders
- `purchase.order.line` - Purchase Order Lines

## Domain Filter Examples

### Basic Filters
```python
[['name', '=', 'John']]  # Exact match
[['age', '>', 18]]  # Greater than
[['email', 'like', '@example.com']]  # Contains
[['state', 'in', ['draft', 'posted']]]  # In list
```

### Logical Operators
```python
['&', ['name', '=', 'John'], ['age', '>', 18]]  # AND
['|', ['name', '=', 'John'], ['name', '=', 'Jane']]  # OR
['!', ['state', '=', 'cancel']]  # NOT
```

### Complex Filters
```python
[
  '&',
  ['state', '=', 'sale'],
  '|',
  ['amount_total', '>', 1000],
  ['partner_id.country_id.code', '=', 'US']
]
```

## Error Handling

The server includes production-grade error handling:

- **Automatic retries**: Failed requests retry with exponential backoff
- **Timeout protection**: Configurable timeouts prevent hanging requests
- **Detailed errors**: Comprehensive error messages with context
- **Connection pooling**: Efficient client reuse across requests

## Performance

- **Connection caching**: Authenticated connections are reused
- **Efficient XML-RPC**: Optimized protocol implementation
- **Parallel operations**: Multiple tools can run concurrently
- **Edge deployment**: Global CDN via Cloudflare Workers

## Security Best Practices

1. **Never commit credentials**: Use environment variables or secrets
2. **Use HTTPS**: Always connect to Odoo over HTTPS in production
3. **Rotate passwords**: Regularly update Odoo credentials
4. **Least privilege**: Use dedicated Odoo users with minimal permissions
5. **Monitor access**: Enable Cloudflare observability for audit logs

## Troubleshooting

### Authentication Failed
- Verify Odoo URL, database name, username, and password
- Check network connectivity to Odoo instance
- Ensure Odoo XML-RPC is enabled

### Timeout Errors
- Increase `ODOO_TIMEOUT` environment variable
- Check Odoo server performance and load
- Verify network latency

### Connection Refused
- Confirm Odoo is running and accessible
- Check firewall rules and network configuration
- Verify port number (default: 8069)

## Development

### Project Structure
```
odoo-mcp-server/
├── src/
│   ├── index.ts          # Main MCP server entry point
│   ├── odoo-client.ts    # Odoo XML-RPC client
│   ├── tools.ts          # MCP tools implementation
│   └── types.ts          # TypeScript type definitions
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── wrangler.toml         # Cloudflare Workers config
└── README.md            # This file
```

### Building
```bash
npm run build
```

### Testing
```bash
# Run local server for testing
npm run dev

# Test with MCP client (e.g., Claude Desktop)
# Configure in claude_desktop_config.json
```

## Claude Desktop Integration

Add to `claude_desktop_config.json`:

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
        "ODOO_PASSWORD": "admin"
      }
    }
  }
}
```

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Check the troubleshooting section
- Review Odoo documentation: https://www.odoo.com/documentation
- Review MCP documentation: https://modelcontextprotocol.io

## Author

SGC TECH AI - Production-grade Odoo development tools

---

**Note**: This MCP server is designed for production use with proper security, error handling, and performance optimizations. Always test thoroughly in staging environments before deploying to production.
