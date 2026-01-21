# ScholarixV2 Deep Cleanup - Complete Database Reset

## ⚠️ CRITICAL WARNING

This tool **DELETES** virtually all non-essential data from your ScholarixV2 instance. This operation is **DESTRUCTIVE** and **CANNOT BE UNDONE** without a backup.

**Use only when you understand the consequences.**

## Overview

The deep cleanup tool removes all user-created data while retaining:
- ✅ Default company structure
- ✅ Admin user accounts
- ✅ System menus and navigation
- ✅ User groups and roles
- ✅ Module structure and configuration
- ✅ System defaults

## What Gets Deleted

### 🗑️ Partners & Contacts
- All customers
- All vendors
- All contact persons
- ~~Keeps: Base company~~

### 🗑️ Sales Management
- **All** sales orders
- **All** sales quotes
- All order lines

### 🗑️ Accounting
- **All** invoices
- **All** credit notes
- **All** expense records
- Custom accounting journals
- Custom general ledger accounts

### 🗑️ Purchase Management
- **All** purchase orders
- All purchase order lines

### 🗑️ Inventory Management
- **All** stock movements
- **All** inventory adjustments
- All custom products
- ~~Keeps: Product templates~~

### 🗑️ CRM
- **All** leads
- **All** opportunities
- All follow-up records

### 🗑️ Projects
- **All** projects
- **All** tasks
- All time tracking entries

### 🗑️ HR & Employees
- **All** employees
- All leave records
- Custom departments
- ~~Keeps: HR module structure~~

### 🗑️ Calendar & Events
- **All** calendar events
- **All** event attendees

### 🗑️ Documentation
- **All** mail messages
- **All** activities
- **ALL** attachments

## Prerequisites

### ✋ BEFORE Running This Tool

1. **BACKUP YOUR DATABASE** ⚠️
   ```bash
   pg_dump scholarixv2_production > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **TEST ON STAGING FIRST**
   - Create a test copy of your database
   - Run deep cleanup on staging
   - Verify results

3. **INFORM STAKEHOLDERS**
   - This operation is irreversible
   - Will take 10-30 minutes
   - Services will be unavailable during cleanup

4. **CONFIRM YOU HAVE BACKUPS**
   - Verify backup integrity
   - Know how to restore
   - Test restore procedure

## Usage

### Step 1: DRY RUN (MANDATORY FIRST STEP)

**Always** preview first:

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

### Step 2: Review the Report

The dry-run will show:
- Number of records that will be deleted for each model
- What defaults will be retained
- Any warnings or issues
- Estimated impact

**DO NOT PROCEED if:**
- Numbers don't match expectations
- Any critical warnings appear
- You're not 100% sure this is what you want

### Step 3: Execute Cleanup (If Confirmed)

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

### Step 4: Monitor Progress

- Cleanup may take 10-30 minutes
- Monitor server logs for errors
- Database size will decrease significantly

### Step 5: Verify Results

After cleanup:
1. Log in to Odoo as admin
2. Verify admin account works
3. Check menu structure is intact
4. Verify configuration was preserved
5. Check database size reduction

## Configuration Options

```typescript
interface DeepCleanupOptions {
  instance: string;                  // Required: "scholarixv2"
  dryRun?: boolean;                  // Default: true (safe)
  keepCompanyDefaults?: boolean;     // Default: true
  keepUserAccounts?: boolean;        // Default: true
  keepMenus?: boolean;               // Default: true
  keepGroups?: boolean;              // Default: true
}
```

### Option Details

| Option | Default | Purpose |
|--------|---------|---------|
| `dryRun` | `true` | Preview without changes |
| `keepCompanyDefaults` | `true` | Keep base company config |
| `keepUserAccounts` | `true` | Keep admin and system users |
| `keepMenus` | `true` | Keep menu structure |
| `keepGroups` | `true` | Keep user groups |

## Report Structure

```json
{
  "success": true,
  "timestamp": "2024-01-19T10:30:45.123Z",
  "dryRun": false,
  "summary": {
    "partnersRemoved": 125,
    "salesOrdersRemoved": 342,
    "invoicesRemoved": 567,
    "purchaseOrdersRemoved": 89,
    "stockMovesRemoved": 1243,
    "productsRemoved": 456,
    "leadsRemoved": 78,
    "opportunitiesRemoved": 45,
    "projectsRemoved": 23,
    "tasksRemoved": 156,
    "eventsRemoved": 34,
    "employeesRemoved": 67,
    "logsAndAttachments": 2345,
    "totalRecordsRemoved": 5570
  },
  "defaultDataRetained": [
    "✓ Default Company Retained",
    "✓ Admin User Retained",
    "✓ Menu Structure Retained",
    "✓ User Groups Retained",
    "✓ Module Structure Intact",
    "✓ System Configuration Retained"
  ],
  "details": [
    {
      "model": "res.partner",
      "recordsRemoved": 125,
      "details": "Removed 125 partners",
      "status": "success"
    }
    // ... more details
  ],
  "warnings": [],
  "errors": []
}
```

## Safety Features

✅ **Dry-Run First**: Default is dry-run=true
✅ **Selective Retention**: Keep company, users, menus, groups
✅ **Detailed Reporting**: Know exactly what's being removed
✅ **Error Handling**: Graceful handling with detailed messages
✅ **Warnings**: Alerts for potentially problematic operations
✅ **Logging**: Complete audit trail

## Recovery

### If Something Goes Wrong

**Restore from backup:**
```bash
psql scholarixv2_production < backup_YYYYMMDD_HHMMSS.sql
```

This is why backup is **mandatory**.

### Partial Recovery

If cleanup partially completed:
1. Stop all Odoo processes
2. Restore from backup
3. Investigate issues
4. Adjust options
5. Try again

## Best Practices

### ✅ DO:
- Create backup **before** running
- Use dry-run first
- Test on staging
- Keep backup for 30 days
- Document when you ran it
- Monitor for issues after
- Keep audit logs

### ❌ DON'T:
- Run on production without staging test
- Delete backups immediately after
- Run during business hours
- Skip the dry-run
- Change options mid-process
- Assume default options are correct
- Run without understanding consequences

## Timing Expectations

| Stage | Duration | Notes |
|-------|----------|-------|
| Dry-run | 2-5 min | Quick, no changes |
| Full Cleanup | 10-30 min | Depends on data volume |
| Database Optimization | 5-10 min | Included in cleanup |
| Verification | 5 min | Manual checks |
| **Total** | **25-55 min** | Plan accordingly |

## What Happens After Cleanup

### Database State
- Size reduced by 50-80%
- Much faster queries
- No demo/test data
- Clean slate for production

### User Experience
- All previous data gone
- Admin can log in normally
- Menus and settings intact
- Ready for fresh data entry

### Application Performance
- Faster response times
- Lower memory usage
- Reduced backup size
- Better scalability

## Troubleshooting

### Issue: Cleanup Fails with Errors
**Solution:**
1. Check database logs for specific errors
2. Run dry-run to identify problematic records
3. Restore from backup
4. Adjust specific cleanup options
5. Try again with safer options

### Issue: Some Records Not Deleted
**Solution:**
1. Some records may have external references
2. Check Odoo logs for constraints
3. Run again - some might require two passes
4. Manually delete remaining records

### Issue: Performance Degradation After
**Solution:**
1. Wait 10 minutes for indexes to rebuild
2. Run: `VACUUM ANALYZE;` in PostgreSQL
3. Restart Odoo service
4. Clear browser cache

### Issue: Can't Restore from Backup
**Solution:**
1. Verify backup file integrity
2. Check PostgreSQL is running
3. Ensure sufficient disk space
4. Use standalone restore: `pg_restore -d scholarixv2_production backup.sql`

## Post-Cleanup Checklist

- [ ] Backup before cleanup? ✅
- [ ] Dry-run executed and reviewed? ✅
- [ ] Full cleanup executed? ✅
- [ ] Admin login verified? ✅
- [ ] Menus visible? ✅
- [ ] Configuration intact? ✅
- [ ] Database size reduced? ✅
- [ ] Performance improved? ✅
- [ ] Backup kept safe? ✅
- [ ] Changes documented? ✅

## FAQ

**Q: Can I undo this?**
A: Only with a backup. That's why backup is mandatory.

**Q: How long does it take?**
A: 10-30 minutes depending on data volume.

**Q: Will my admin account be deleted?**
A: No, `keepUserAccounts=true` preserves admin accounts.

**Q: What if I need some old data?**
A: Restore from backup, extract that data, then re-run cleanup.

**Q: Is the database smaller after?**
A: Yes, typically 50-80% smaller.

**Q: Is performance better after?**
A: Yes, much faster with less data.

**Q: Can I run this regularly?**
A: Yes, every month after archiving old data.

**Q: What about modules?**
A: Module structure is preserved, only data is removed.

## Support

If you encounter issues:

1. Check the detailed error messages
2. Review the dry-run report
3. Check Odoo server logs
4. Restore from backup and retry
5. Contact support with dry-run report

## Important Notes

⚠️ **This tool is not reversible without a backup**
⚠️ **Always test on staging first**
⚠️ **Always backup before running**
⚠️ **Always use dry-run first**
⚠️ **Inform stakeholders before running**
⚠️ **Monitor the operation closely**

---

**Remember: You can't get this data back without a backup.**

**Create that backup NOW before proceeding.**
