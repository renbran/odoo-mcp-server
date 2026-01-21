# ScholarixV2 Quick Start Guide

## Step 1: Configure Connection

Edit your `.env` file with ScholarixV2 credentials:

```bash
# .env
ODOO_URL=https://scholarixv2.yourdomain.com
ODOO_DB=scholarixv2_production
ODOO_USERNAME=admin@yourdomain.com
ODOO_PASSWORD=your_password_here
```

## Step 2: Test Connection

```bash
npm install
npm run build
npm run test  # Verify connection works
```

## Step 3: Preview Cleanup (DRY RUN - RECOMMENDED FIRST)

```bash
npm run cleanup:dry-run
```

This will show you exactly what would be cleaned up without making any changes.

## Step 4: Review the Report

The dry-run report will show:
- ✅ How many test records would be removed
- ✅ How many inactive records would be archived
- ✅ How many draft documents would be deleted
- ✅ How many orphan records would be removed
- ✅ How many old logs would be cleaned
- ✅ Any warnings or potential issues

## Step 5: Execute Cleanup (if satisfied)

```bash
npm run cleanup
```

## Step 6: Verify Results

Check your ScholarixV2 instance to verify:
1. Database size has reduced
2. No critical data was lost
3. Performance has improved
4. All key modules still function

## Quick Commands Reference

```bash
# Test connectivity
npm run test

# Preview all cleanup operations
npm run cleanup:dry-run

# Execute full cleanup
npm run cleanup

# Remove test data only
npm run cleanup:test

# Clean draft documents only
npm run cleanup:drafts

# Clean activity logs only
npm run cleanup:logs
```

## What Gets Cleaned

### Test Data
- Records with names starting with "Test" or "Demo"
- Test sales orders, invoices, purchase orders
- Test partners and contacts

### Inactive Records
- Partners, sales orders, invoices not modified in 180+ days
- Records are archived (not deleted) for safety
- Can be restored if needed

### Draft Documents
- Unsaved sales orders
- Unsaved invoices
- Unsaved purchase orders

### Orphan Records
- Sales order lines without parent order
- Invoice lines without parent invoice
- Other records with broken relationships

### Old Logs
- Mail messages older than 180 days
- Completed activities older than 180 days
- Activity tracking records

### Old Attachments
- Attachments uploaded 180+ days ago
- Orphaned files
- Temporary uploads

## Safety Tips

✅ **Always backup first:**
```bash
# PostgreSQL example
pg_dump scholarixv2_production > backup_$(date +%Y%m%d).sql
```

✅ **Test on staging first:**
Copy your database to a staging environment and test cleanup there.

✅ **Schedule maintenance window:**
Run during low-traffic hours to minimize impact.

✅ **Monitor performance:**
Check database size and application speed after cleanup.

## Troubleshooting

**Q: Connection refused?**
- A: Check ODOO_URL is correct and instance is running
- Check network connectivity: `ping scholarixv2.yourdomain.com`

**Q: Authentication failed?**
- A: Verify credentials in `.env`
- Ensure user has admin rights
- Try logging in manually to verify credentials

**Q: Cleanup is slow?**
- A: This is normal for large databases
- Can take 10-30 minutes depending on data volume
- No timeout - let it complete

**Q: How do I undo cleanup?**
- A: Restore from backup: `psql scholarixv2_production < backup.sql`
- Archived records can be reactivated by setting `active=true`

## Next Steps

1. Monitor application performance after cleanup
2. Consider scheduling regular cleanup (monthly)
3. Set up automated backups before cleanup
4. Document any custom cleanup needs

## Support

For issues or questions:
1. Check the full [DATABASE_CLEANUP_GUIDE.md](DATABASE_CLEANUP_GUIDE.md)
2. Review the dry-run report for warnings
3. Check Odoo logs for any errors

## Maintenance Schedule

**Recommended cleanup frequency:**
- **Monthly**: Small/medium instances
- **Quarterly**: Large instances
- **As needed**: Before major updates

**Best time to cleanup:**
- Weekend mornings (low traffic)
- Before backups (faster backup after cleanup)
- After month/quarter end processing
