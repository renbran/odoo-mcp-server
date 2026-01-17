# ⚡ QUICK REFERENCE CARD

## 🚀 START DEVELOPMENT IN 2 MINUTES

```bash
# 1. Setup environment (first time only)
cp .env.example .env
# Edit .env with your Odoo credentials

# 2. Start developing
npm run dev

# 3. In another terminal, run tests
npm run test:watch
```

---

## 📋 ESSENTIAL COMMANDS

### Building
```bash
npm run build           # Compile TypeScript → dist/
npm run clean           # Remove dist/
npm run watch           # Watch TypeScript (compile on save)
```

### Running
```bash
npm run dev             # Start server (hot reload)
npm run start           # Run compiled server
npm run dev:watch       # Watch + reload terminal
```

### Testing
```bash
npm test                # Run all tests
npm run test:watch      # Watch mode
npm run test:coverage   # Coverage report
```

### Code Quality
```bash
npm run lint            # Check style
npm run lint:fix        # Auto-fix issues
npm run type-check      # Type validation
npm run type-check:watch # Watch types
```

---

## 🔧 ENVIRONMENT SETUP

### Create .env from template
```bash
cp .env.example .env
```

### Edit .env with your Odoo details
```bash
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=admin
ODOO_PASSWORD=your_password
```

### For multiple instances (JSON)
```bash
ODOO_INSTANCES={"prod":{"url":"...","db":"...","username":"...","password":"..."},"staging":{...}}
```

---

## 📁 FOLDER STRUCTURE

```
odoo-mcp-server/
├── src/                    # TypeScript source
│   ├── index.ts           # MCP server entry
│   ├── odoo-client.ts     # Odoo client
│   ├── tools.ts           # MCP tools
│   └── types.ts           # Interfaces
├── dist/                  # Compiled JavaScript (auto-generated)
├── deals_management/      # Odoo module
│   ├── models/           # Python models
│   ├── views/            # XML views
│   └── security/         # Access control
├── package.json          # Project config
├── tsconfig.json         # TypeScript config
├── jest.config.js        # Test config
├── .eslintrc.json        # Linting rules
├── .env                  # Your config (create from .env.example)
└── .env.example          # Template
```

---

## 🛠️ CREATE NEW ODOO MODEL

### 1. Create Python Model
```python
# deals_management/models/my_model.py
from odoo import fields, models, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Custom Model'
    
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
```

### 2. Import in __init__.py
```python
# deals_management/models/__init__.py
from . import my_model
```

### 3. Create View
```xml
<!-- deals_management/views/my_model_views.xml -->
<odoo>
  <data>
    <record id="my_model_tree" model="ir.ui.view">
      <field name="name">My Model Tree</field>
      <field name="model">my.model</field>
      <field name="arch" type="xml">
        <tree><field name="name"/></tree>
      </field>
    </record>
  </data>
</odoo>
```

### 4. Update __manifest__.py
```python
'data': [
    'security/ir.model.access.csv',
    'views/my_model_views.xml',  # Add this
]
```

### 5. Update Security
```csv
# security/ir.model.access.csv
my_model_user,My Model User,model_my_model,base.group_user,1,0,0,0
my_model_manager,My Model Manager,model_my_model,base.group_user,1,1,1,1
```

---

## 🧪 WRITE UNIT TESTS

### Create Test File
```typescript
// src/my-feature.test.ts
import { OdooClient } from './odoo-client';

describe('My Feature', () => {
  let client: OdooClient;

  beforeEach(() => {
    client = new OdooClient({
      url: 'http://localhost:8069',
      db: 'test_db',
      username: 'admin',
      password: 'admin',
    });
  });

  test('should work', async () => {
    const result = await client.authenticate();
    expect(result.success).toBe(true);
  });
});
```

### Run Tests
```bash
npm test                # All tests
npm run test:watch     # Watch mode
npm run test:coverage  # Coverage report
```

---

## 📊 MCP TOOLS USAGE

### Search for Records
```typescript
{
  "tool": "odoo_search_read",
  "params": {
    "instance": "production",
    "model": "sale.order",
    "domain": [["state", "=", "draft"]],
    "fields": ["name", "partner_id", "amount_total"],
    "limit": 10
  }
}
```

### Create Record
```typescript
{
  "tool": "odoo_create",
  "params": {
    "instance": "production",
    "model": "sale.order",
    "values": {
      "partner_id": 1,
      "order_line": [
        [0, 0, {"product_id": 1, "product_qty": 5}]
      ]
    }
  }
}
```

### Update Record
```typescript
{
  "tool": "odoo_update",
  "params": {
    "instance": "production",
    "model": "sale.order",
    "ids": [1],
    "values": {"state": "sale"}
  }
}
```

### Execute Method
```typescript
{
  "tool": "odoo_execute",
  "params": {
    "instance": "production",
    "model": "sale.order",
    "method": "action_confirm",
    "args": [[1, 2, 3]]
  }
}
```

---

## 🔍 DEBUGGING

### Enable Debug Mode
```bash
DEBUG=true npm run dev
```

### Type Check Issues
```bash
npm run type-check
```

### Lint Issues
```bash
npm run lint
npm run lint:fix
```

### Check Compilation
```bash
npm run build
# Check dist/ folder for errors
```

---

## 📈 PHASES CHECKLIST

### Phase 1: Property Model (2-3h)
- [ ] Create property.property model
- [ ] Create property views
- [ ] Add property_id to deals
- [ ] Write tests

### Phase 2: Payment Schedule (3-4h)
- [ ] Create payment.schedule model
- [ ] Create views
- [ ] Auto-generate on deal confirm
- [ ] Write tests

### Phase 3: Commission System (3-4h)
- [ ] Enhance commission calculations
- [ ] Add tiering
- [ ] Create commission reports
- [ ] Write tests

### Phase 4: Testing & Reporting (2-3h)
- [ ] Add all unit tests
- [ ] Create analytics reports
- [ ] Dashboard views
- [ ] Performance testing

---

## ⚠️ COMMON ISSUES & FIXES

### Build Fails
```bash
npm run clean && npm run build
```

### Missing Dependencies
```bash
npm install
```

### Type Errors
```bash
npm run type-check
npm run lint:fix
```

### Odoo Connection Error
```bash
# Check .env file has correct credentials
# Make sure Odoo server is running
# Verify ODOO_URL format (http://localhost:8069)
```

### Port Already in Use
```bash
# Change MCP_PORT in .env
MCP_PORT=3001
```

---

## 📚 USEFUL LINKS

- **Odoo Docs:** https://www.odoo.com/documentation
- **MCP Spec:** https://spec.modelcontextprotocol.io/
- **TypeScript:** https://www.typescriptlang.org/
- **Jest Docs:** https://jestjs.io/

---

## 🎯 PROJECT GOALS

✅ **Phase 1:** Create property model + views  
✅ **Phase 2:** Implement payment schedule  
✅ **Phase 3:** Build commission system  
✅ **Phase 4:** Complete testing & deployment  

**Timeline:** 4-6 weeks to production

---

## 💡 PRO TIPS

1. **Always backup .env** before sharing code
2. **Commit frequently** with meaningful messages
3. **Run tests** before committing
4. **Keep TypeScript strict** - don't disable checks
5. **Document** as you code
6. **Test locally** before staging

---

## 🚀 GETTING HELP

1. Check [START_HERE.md](START_HERE.md)
2. Review [README.md](README.md)
3. See [DEVELOPMENT_CHECKLIST.md](DEVELOPMENT_CHECKLIST.md)
4. Check source code comments
5. Review existing tests for examples

---

**Last Updated:** January 17, 2026  
**Status:** ✅ Ready to Use  
**Start Command:** `npm run dev`
