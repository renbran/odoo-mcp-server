# Deep Cleanup - Quick Start

## ⚠️ WARNING: This Deletes Everything!

This tool removes **all non-essential data** from your database.

**Backup first. Test on staging first. Understand what you're deleting.**

## 3-Step Process

### Step 1: Create Backup (NON-NEGOTIABLE)

```bash
# PostgreSQL
pg_dump scholarixv2_production > backup_$(date +%Y%m%d_%H%M%S).sql

# Or your preferred backup method
```

**Keep this backup safe.**

### Step 2: Dry Run (Preview)

```bash
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "odoo_deep_cleanup",
    "arguments": {
      "instance": "scholarixv2",
      "dryRun": true,
      "keepCompanyDefaults": true,
      "keepUserAccounts": true
    }
  }'
```

**Review the report:**
- How many records will be deleted?
- Are these the records you want to delete?
- Any warnings or errors?

**Do NOT proceed if:**
- Numbers look wrong
- You don't recognize what's being deleted
- There are errors in the report

### Step 3: Execute (If You're Sure)

```bash
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "odoo_deep_cleanup",
    "arguments": {
      "instance": "scholarixv2",
      "dryRun": false,
      "keepCompanyDefaults": true,
      "keepUserAccounts": true,
      "keepMenus": true,
      "keepGroups": true
    }
  }'
```

**This will:**
- Delete all partners/contacts
- Delete all orders (sales, purchase)
- Delete all invoices
- Delete all inventory
- Delete all CRM data
- Delete all projects/tasks
- Delete all events
- Delete all employees
- Delete all attachments/logs

**This will NOT:**
- Delete admin account
- Delete default company
- Delete module structure
- Delete user groups
- Delete menus

## What You Get

✅ **Clean database**
✅ **50-80% smaller**
✅ **Much faster**
✅ **Ready for production**
✅ **No demo data**
✅ **No test records**

## Restore If Needed

If anything goes wrong:

```bash
# Stop Odoo
systemctl stop odoo

# Restore database
psql scholarixv2_production < backup_YYYYMMDD_HHMMSS.sql

# Start Odoo
systemctl start odoo
```

## Expected Output (Dry-Run)

```json
{
  "success": true,
  "dryRun": true,
  "summary": {
    "partnersRemoved": 125,
    "salesOrdersRemoved": 342,
    "invoicesRemoved": 567,
    // ... more counts
    "totalRecordsRemoved": 5570
  }
}
```

## Time Required

| Step | Time |
|------|------|
| Backup | 5-15 min |
| Dry-run | 2-5 min |
| Full cleanup | 10-30 min |
| Verification | 5 min |

**Total: 25-55 minutes**

## Checklist

- [ ] Backup created?
- [ ] Backup tested/verified?
- [ ] All stakeholders informed?
- [ ] Staging tested?
- [ ] Dry-run reviewed?
- [ ] Numbers look right?
- [ ] Ready to execute?

**If all checked: PROCEED**

## Options

```typescript
{
  "instance": "scholarixv2",        // Required
  "dryRun": false,                  // true = preview, false = execute
  "keepCompanyDefaults": true,      // Keep default company
  "keepUserAccounts": true,         // Keep admin accounts
  "keepMenus": true,                // Keep menu structure  
  "keepGroups": true                // Keep user groups
}
```

## Common Scenarios

### Scenario 1: Clean Before Production Launch
```json
{
  "instance": "scholarixv2",
  "dryRun": false,
  "keepCompanyDefaults": true,
  "keepUserAccounts": true,
  "keepMenus": true,
  "keepGroups": true
}
```

### Scenario 2: Complete Reset (Dangerous!)
```json
{
  "instance": "scholarixv2",
  "dryRun": false,
  "keepCompanyDefaults": false,  // Remove even company
  "keepUserAccounts": false,     // Remove even users (except system)
  "keepMenus": false,            // Reset menus
  "keepGroups": false            // Reset groups
}
```

⚠️ **Only use if you know what you're doing**

## Support

Full documentation: [DEEP_CLEANUP_GUIDE.md](DEEP_CLEANUP_GUIDE.md)

**Remember:**
1. Backup is NOT optional
2. Dry-run is NOT optional
3. Testing on staging is NOT optional
4. Understanding what gets deleted is NOT optional

**Without these, you WILL lose data.**

---

**Backup → Dry-run → Execute**

**In that order. No exceptions.**
