# Odoo MCP Server - Deployment Guide

Complete guide for deploying the Odoo MCP server to production environments.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Cloudflare Workers Deployment](#cloudflare-workers-deployment)
3. [Claude Desktop Integration](#claude-desktop-integration)
4. [Production Configuration](#production-configuration)
5. [Security Hardening](#security-hardening)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development Setup

### Step 1: Install Dependencies

```bash
cd D:\01_WORK_PROJECTS\odoo-mcp-server
npm install
```

### Step 2: Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your Odoo credentials:

```bash
# For local Odoo 19 development instance
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

Or configure multiple instances:

```bash
ODOO_INSTANCES='{
  "local": {
    "url": "http://localhost:8069",
    "db": "odoo",
    "username": "admin",
    "password": "admin"
  },
  "production": {
    "url": "https://your-odoo-domain.com",
    "db": "production_db",
    "username": "api_user",
    "password": "secure_password"
  }
}'
```

### Step 3: Build and Test

```bash
# Build TypeScript
npm run build

# Run locally
npm start
```

### Step 4: Test with Sample Commands

Open another terminal and test authentication:

```bash
# The server communicates via stdio, so you'll need an MCP client
# Or integrate with Claude Desktop (see below)
```

---

## Cloudflare Workers Deployment

### Prerequisites

1. **Cloudflare Account**: Sign up at https://cloudflare.com
2. **Wrangler CLI**: Install globally

```bash
npm install -g wrangler
```

### Step 1: Authenticate

```bash
wrangler login
```

This opens a browser for authentication.

### Step 2: Configure Secrets

**IMPORTANT**: Never commit credentials to git. Use Cloudflare secrets:

```bash
# For single instance
wrangler secret put ODOO_URL
# Enter: https://your-odoo-domain.com

wrangler secret put ODOO_DB
# Enter: your_database_name

wrangler secret put ODOO_USERNAME
# Enter: your_username

wrangler secret put ODOO_PASSWORD
# Enter: your_secure_password
```

Or for multiple instances:

```bash
wrangler secret put ODOO_INSTANCES
# Enter the full JSON configuration (paste from your local .env)
```

### Step 3: Deploy

```bash
npm run deploy
```

Expected output:
```
Total Upload: XX.XX KiB / gzip: XX.XX KiB
Uploaded odoo-mcp-server (X.XX sec)
Published odoo-mcp-server (X.XX sec)
  https://odoo-mcp-server.your-subdomain.workers.dev
```

### Step 4: Verify Deployment

```bash
wrangler tail
```

This shows real-time logs from your worker.

### Step 5: Configure Custom Domain (Optional)

In Cloudflare Dashboard:
1. Go to Workers & Pages
2. Select your worker
3. Go to Triggers → Custom Domains
4. Add your custom domain (e.g., `odoo-mcp.yourdomain.com`)

---

## Claude Desktop Integration

### Step 1: Locate Claude Desktop Config

Find your Claude Desktop config file:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Add MCP Server Configuration

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo-local": {
      "command": "node",
      "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin"
      }
    },
    "odoo-production": {
      "command": "node",
      "args": ["D:\\01_WORK_PROJECTS\\odoo-mcp-server\\dist\\index.js"],
      "env": {
        "ODOO_INSTANCES": "{\"production\":{\"url\":\"https://your-domain.com\",\"db\":\"production_db\",\"username\":\"api_user\",\"password\":\"secure_password\"}}"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. The MCP server will be available in conversations.

### Step 4: Test Integration

In Claude Desktop, try:

```
Can you search for all customers in Odoo with country USA?
```

Claude should use the `odoo_search` or `odoo_search_read` tool automatically.

---

## Production Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ODOO_INSTANCES` | Yes* | JSON config for multiple instances | See above |
| `ODOO_URL` | Yes* | Single instance URL | `https://odoo.example.com` |
| `ODOO_DB` | Yes* | Database name | `production_db` |
| `ODOO_USERNAME` | Yes | Odoo username | `api_user` |
| `ODOO_PASSWORD` | Yes | Odoo password | `secure_password` |
| `ODOO_TIMEOUT` | No | Request timeout (ms) | `30000` |
| `ODOO_MAX_RETRIES` | No | Max retry attempts | `3` |

*Either `ODOO_INSTANCES` or individual `ODOO_*` variables required.

### Wrangler Configuration

Edit `wrangler.toml` for production:

```toml
name = "odoo-mcp-server"
main = "src/index.ts"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[env.production]
vars = { ENVIRONMENT = "production" }
routes = [
  { pattern = "odoo-mcp.yourdomain.com/*", zone_name = "yourdomain.com" }
]

[limits]
cpu_ms = 50000  # Adjust based on usage

[observability]
enabled = true
```

---

## Security Hardening

### 1. Odoo User Permissions

Create a dedicated API user in Odoo with minimal permissions:

1. Go to Settings → Users & Companies → Users
2. Create new user: `mcp_api_user`
3. Set access rights:
   - Sales: User (Own Documents Only)
   - Inventory: User
   - Accounting: Billing
   - Contacts: User (Own Documents Only)
4. **Never use admin account for API access**

### 2. Network Security

- **Use HTTPS**: Always connect to Odoo via HTTPS
- **Firewall**: Restrict Odoo server access to known IPs
- **VPN**: Consider VPN for production Odoo access

### 3. Credential Management

- **Rotate passwords**: Change Odoo passwords quarterly
- **Strong passwords**: Use 20+ character passwords with symbols
- **Secret management**: Use Cloudflare secrets (never commit to git)

### 4. Rate Limiting

Add to `wrangler.toml`:

```toml
[rate_limit]
enabled = true
simple = { limit = 100, period = 60 }  # 100 requests per minute
```

### 5. Logging & Monitoring

Enable Cloudflare observability:

```toml
[observability]
enabled = true
```

Monitor:
- Request volumes
- Error rates
- Authentication failures
- Response times

---

## Monitoring & Maintenance

### Cloudflare Dashboard

Monitor your worker in Cloudflare Dashboard:

1. **Analytics**: Request volume, errors, CPU time
2. **Logs**: Real-time logs with `wrangler tail`
3. **Alerts**: Set up alerts for errors/downtime

### Health Checks

Create a health check endpoint:

```typescript
// Add to src/index.ts
async function healthCheck() {
  return {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    instances: Array.from(this.instances.keys()),
  };
}
```

### Backup & Recovery

1. **Version control**: Keep all code in git
2. **Rollback**: Use Cloudflare rollback if issues occur
3. **Secrets backup**: Document all secret names (not values!)

### Updates & Patches

```bash
# Update dependencies
npm update

# Rebuild
npm run build

# Deploy new version
npm run deploy
```

### Troubleshooting Production Issues

#### High Error Rate

```bash
# View real-time logs
wrangler tail --format pretty

# Check for authentication failures
wrangler tail | grep "AUTH_ERROR"
```

#### Slow Response Times

1. Check Odoo server performance
2. Review domain filter complexity
3. Increase timeout: `ODOO_TIMEOUT=60000`

#### Connection Failures

1. Verify Odoo is accessible from Cloudflare
2. Check firewall rules
3. Verify SSL certificates (for HTTPS)

---

## Testing Checklist

Before production deployment:

- [ ] All environment variables configured
- [ ] Credentials stored as secrets (not in code)
- [ ] Test authentication with all instances
- [ ] Test CRUD operations on non-critical data
- [ ] Test error handling (invalid credentials, network issues)
- [ ] Test rate limiting
- [ ] Monitor logs during initial deployment
- [ ] Configure alerts for errors
- [ ] Document rollback procedure
- [ ] Test from Claude Desktop integration

---

## Support Resources

- **Odoo Documentation**: https://www.odoo.com/documentation
- **MCP Documentation**: https://modelcontextprotocol.io
- **Cloudflare Workers**: https://developers.cloudflare.com/workers
- **Wrangler CLI**: https://developers.cloudflare.com/workers/wrangler

---

## Quick Reference Commands

```bash
# Local development
npm install
npm run build
npm start

# Cloudflare deployment
wrangler login
wrangler secret put ODOO_INSTANCES
npm run deploy
wrangler tail

# Testing
npm run build && npm start
```

---

**Production Checklist Complete** ✓

Your Odoo MCP server is now ready for production deployment with security, monitoring, and error handling in place.
