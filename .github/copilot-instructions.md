# Odoo MCP Server - AI Agent Instructions

## Architecture Overview

This is a **Model Context Protocol (MCP) server** that bridges Claude Desktop/AI agents with Odoo 17-19 via XML-RPC. It's a TypeScript Node.js application designed for both local stdio transport and Cloudflare Workers deployment.

**Core components:**
- [src/index.ts](../src/index.ts) - MCP server setup, multi-instance management, request routing
- [src/odoo-client.ts](../src/odoo-client.ts) - XML-RPC client with auth, retry logic, connection pooling
- [src/tools.ts](../src/tools.ts) - 11 MCP tools (search, CRUD, reports, workflow actions) + contextPrompts
- [src/types.ts](../src/types.ts) - TypeScript interfaces for Odoo operations

**Data flow:** Claude → MCP stdio transport → `OdooMCPServer` → `OdooTools` → `OdooClient` → Odoo XML-RPC API

## Critical Patterns

### Multi-Instance Connection Management
The server maintains a connection pool (`Map<string, OdooClient>`) with lazy authentication:

```typescript
// Instance config parsed from ODOO_INSTANCES JSON or individual env vars
// Clients created on-demand in getClient(), cached and reused
private async getClient(instance: string): Promise<OdooClient>
```

**When modifying:** Always use `instance` parameter in tool arguments. Never hardcode instance names.

### Tool Schema Validation
All tools use **Zod schemas** for runtime validation. Schema structure matches MCP requirements:

```typescript
const SearchSchema = z.object({
  instance: z.string().describe('Odoo instance identifier'),
  model: z.string().describe('Odoo model name'),
  domain: z.array(z.any()).optional(), // Odoo domain filters
  // ...
});
```

**When adding tools:** Define schema, add to `tools` array, implement handler in `OdooTools.executeTool()`.

### Odoo Domain Filters
Domains use prefix notation: `['&', ['field1', '=', 'val'], ['field2', '>', 10]]`
- Logical operators: `&` (AND), `|` (OR), `!` (NOT) precede operands
- Operators: `=`, `!=`, `>`, `<`, `>=`, `<=`, `like`, `ilike`, `in`, `not in`
- See `contextPrompts` in [tools.ts](../src/tools.ts) for examples

### Error Handling
Client methods return `OdooResponse<T>` with discriminated union:
```typescript
{ success: true, data: T, metadata?: {...} }
{ success: false, error: { code: string, message: string } }
```

**Pattern:** Check `success` before accessing `data`. Throw errors in tool handlers to trigger MCP error response.

### XML-RPC Retry Logic
[odoo-client.ts](../src/odoo-client.ts) wraps all XML-RPC calls in `executeXmlRpc()` with exponential backoff (max 3 retries, 30s timeout). Transient network errors auto-retry; auth failures fail immediately.

## Development Workflows

### Build & Test
```bash
npm install          # Install dependencies
npm run build        # TypeScript → dist/ (required before npm start)
npm run dev          # Wrangler dev mode (Cloudflare Workers local)
npm start            # Node.js stdio mode (for Claude Desktop)
```

**Critical:** `npm start` expects `dist/index.js` compiled. Always `npm run build` after TypeScript changes.

### Configuration
Two modes:
1. **Multi-instance (recommended):** `ODOO_INSTANCES='{"prod": {...}, "staging": {...}}'`
2. **Single instance:** `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`

See [README.md](../README.md) for JSON structure.

### Deployment
Cloudflare Workers: `npm run deploy` (requires `wrangler.toml` config, secrets via `wrangler secret put`)

**Note:** [wrangler.toml](../wrangler.toml) sets `compatibility_flags = ["nodejs_compat"]` for xmlrpc library.

## Project-Specific Conventions

### File Structure
```
src/
  index.ts        # Server class, env parsing, MCP handler setup
  odoo-client.ts  # Low-level Odoo API calls (search, read, create, etc.)
  tools.ts        # High-level MCP tool definitions + handlers
  types.ts        # Shared TypeScript interfaces
```

**Pattern:** Keep MCP-specific logic in `index.ts`/`tools.ts`, Odoo API logic in `odoo-client.ts`.

### TypeScript Config
- **Target:** ES2022 (modern async/await, top-level await)
- **Module:** ES2022 with `.js` extensions in imports (`'./odoo-client.js'`)
- **Strict mode:** Enabled (no implicit any, null checks)

### Common Odoo Models
Frequent targets (see `contextPrompts` for full list):
- `res.partner` - Customers/Contacts
- `sale.order` - Sales Orders
- `account.move` - Invoices/Bills
- `stock.picking` - Inventory Transfers
- `product.product` - Product Variants

### MCP Context Prompts
Two helper prompts in `tools.ts`:
- `odoo_common_models` - Model name reference
- `odoo_domain_filters` - Domain syntax examples

**Purpose:** Reduce token usage by embedding frequently-needed Odoo knowledge.

## Integration Points

### MCP SDK
Uses `@modelcontextprotocol/sdk` v1.0.4:
- `Server` class with stdio transport
- Schema: `ListToolsRequestSchema`, `CallToolRequestSchema`, `ListPromptsRequestSchema`, `GetPromptRequestSchema`
- Tool responses: `{ content: [{ type: 'text', text: JSON.stringify(...) }] }`

### XML-RPC Endpoints
Odoo XML-RPC at 3 paths:
- `/xmlrpc/2/common` - Authentication (`authenticate`, `version`)
- `/xmlrpc/2/object` - CRUD operations (`execute_kw`)
- `/xmlrpc/2/report` - PDF report generation

**Authentication:** `uid` obtained from `common.authenticate()`, used in all subsequent calls.

### External Dependencies
- **xmlrpc** (v1.3.2) - Low-level XML-RPC client (no async, wrapped in Promises)
- **zod** (v3.23.8) - Runtime schema validation
- **dotenv** (v17.2.3) - `.env` file loading (local dev only)

## Testing & Debugging

### Manual Testing
Use Claude Desktop with config:
```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["D:\\odoo17_backup\\odoo-mcp-server\\dist\\index.js"],
      "env": { "ODOO_INSTANCES": "{...}" }
    }
  }
}
```

**Debug logs:** Check `stderr` (console.error) in Claude Desktop logs (`%APPDATA%\Claude\logs`).

### Common Issues
- **"Unknown Odoo instance"**: Check `ODOO_INSTANCES` JSON syntax, instance name spelling
- **"Authentication failed"**: Verify URL, DB name, credentials (test with `curl -X POST https://odoo.example.com/xmlrpc/2/common`)
- **"Tool execution error"**: Enable verbose logging in `index.ts` handlers

## When Extending

### Adding a New Tool
1. Define Zod schema in `tools.ts` (e.g., `ArchiveSchema`)
2. Add to `tools` array with name, description, schema
3. Add case in `OdooTools.executeTool()`
4. Implement handler method (e.g., `handleArchive()`)
5. Add corresponding method in `OdooClient` if needed

### Adding Odoo Version Support
Client auto-detects version from `/xmlrpc/2/common.version()`. Version-specific behavior should check `connection.serverVersion` and branch logic (currently v17-19 have compatible APIs).

### Performance Optimization
- Connection pooling: Already implemented (`this.clients` cache)
- Response caching: Optional KV namespace in `wrangler.toml` (not yet implemented)
- Batch operations: Use `execute_kw` with arrays (e.g., read multiple IDs at once)
