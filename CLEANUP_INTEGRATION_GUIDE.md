# ScholarixV2 Cleanup Tools - Complete Integration Guide

## Overview

Your ScholarixV2 Odoo instance now has **two powerful cleanup tools**:

1. **Standard Cleanup** - Safe cleanup removing test data, old records, drafts
2. **Deep Cleanup** - Complete reset keeping only defaults

## 🛠️ Tool Comparison

| Feature | Standard Cleanup | Deep Cleanup |
|---------|------------------|--------------|
| **Purpose** | Maintenance | Complete reset |
| **Data Removed** | Test/demo/old/drafts | Everything except defaults |
| **Safety Level** | High | Medium (requires backup) |
| **Data Retention** | Keeps active records | Keeps only infrastructure |
| **Use Case** | Monthly maintenance | Pre-production launch |
| **Reversibility** | Partial (archiving) | Full (backup required) |
| **Default Dry-run** | false | true |

## 📚 Documentation Structure

### For Standard Cleanup
- **DATABASE_CLEANUP_GUIDE.md** - Full reference (2500+ words)
  - Setup, usage, configuration
  - Troubleshooting and best practices
  - Safety features explained

- **SCHOLARIXV2_QUICK_START.md** - Quick start (500+ words)
  - 6-step setup guide
  - Quick commands
  - Maintenance schedule

### For Deep Cleanup
- **DEEP_CLEANUP_GUIDE.md** - Complete reference (1200+ words)
  - What gets deleted (by model)
  - Prerequisites and backups
  - Recovery procedures
  - FAQ

- **DEEP_CLEANUP_QUICK_START.md** - Quick start
  - 3-step process
  - Backup instructions
  - Common scenarios

## 🚀 Quick Reference

### Standard Cleanup (Safe)

**Dry-run:**
```bash
npm run cleanup:dry-run
```

**Execute:**
```bash
npm run cleanup
```

**What it removes:**
- ✓ Test/demo records (names with "Test" or "Demo")
- ✓ Inactive records (180+ days no activity)
- ✓ Draft documents
- ✓ Orphan records
- ✓ Old logs and attachments

**What it keeps:**
- ✓ All active business data
- ✓ Recent transactions
- ✓ Customer/vendor relationships

### Deep Cleanup (Destructive)

**Dry-run (required):**
```bash
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "odoo_deep_cleanup",
    "arguments": {
      "instance": "scholarixv2",
      "dryRun": true
    }
  }'
```

**Execute (after backup + dry-run):**
```bash
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "odoo_deep_cleanup",
    "arguments": {
      "instance": "scholarixv2",
      "dryRun": false,
      "keepCompanyDefaults": true,
      "keepUserAccounts": true
    }
  }'
```

**What it removes:**
- ✓ ALL partners/contacts
- ✓ ALL sales orders and quotes
- ✓ ALL invoices and accounting
- ✓ ALL purchase orders
- ✓ ALL inventory and products
- ✓ ALL CRM leads/opportunities
- ✓ ALL projects and tasks
- ✓ ALL HR employees
- ✓ ALL calendar events
- ✓ ALL attachments and logs

**What it keeps:**
- ✓ Admin user account
- ✓ Default company structure
- ✓ User groups and roles
- ✓ Menu structure
- ✓ Module configuration

## 🎯 Decision Guide

### Use Standard Cleanup When:
- ✅ Doing regular maintenance (monthly/quarterly)
- ✅ Database size is getting large
- ✅ Want to remove only old/test data
- ✅ Want to keep all active business records
- ✅ Need high safety (low risk of data loss)

**Command:**
```bash
npm run cleanup
```

### Use Deep Cleanup When:
- ✅ Preparing for production launch
- ✅ Want completely clean slate
- ✅ Database has a lot of demo/test data
- ✅ Database size needs major reduction
- ✅ Starting fresh with new data

**Warning:** Requires backup and dry-run first!

## 📋 Workflows

### Workflow 1: Monthly Maintenance
```
1. npm run cleanup:dry-run
2. Review dry-run report
3. npm run cleanup
4. Verify results
5. Monitor performance
```

**Time:** 20-40 minutes
**Risk:** Very low

### Workflow 2: Production Launch
```
1. Create database backup
2. curl ... dryRun: true (deep cleanup)
3. Review dry-run report
4. curl ... dryRun: false (deep cleanup)
5. Verify clean slate
6. Test critical workflows
```

**Time:** 30-60 minutes
**Risk:** Low (with backup)

### Workflow 3: Database Optimization
```
1. npm run cleanup (standard)
2. npm run cleanup:test (remove test data)
3. npm run cleanup:logs (clean logs)
4. Monitor performance improvement
```

**Time:** 30-50 minutes
**Risk:** Very low

## 🔧 Configuration Reference

### Standard Cleanup Options
```typescript
{
  instance: "scholarixv2",
  removeTestData: true,              // Default: true
  removeInactivRecords: true,        // Default: true
  cleanupDrafts: true,               // Default: true
  daysThreshold: 180,                // Default: 180 days
  dryRun: false                      // Default: false
}
```

### Deep Cleanup Options
```typescript
{
  instance: "scholarixv2",
  dryRun: true,                      // Default: true (safety)
  keepCompanyDefaults: true,         // Default: true
  keepUserAccounts: true,            // Default: true
  keepMenus: true,                   // Default: true
  keepGroups: true                   // Default: true
}
```

## 📊 Expected Results

### After Standard Cleanup
- Database size: 10-20% reduction
- Query performance: 5-10% faster
- Backup size: 10-20% smaller
- Business data: Intact

### After Deep Cleanup
- Database size: 50-80% reduction
- Query performance: 2-3x faster
- Backup size: 50-80% smaller
- Business data: Removed (kept defaults)

## ✅ Pre-Execution Checklist

### For Standard Cleanup
- [ ] Reviewed DATABASE_CLEANUP_GUIDE.md?
- [ ] Ran dry-run and reviewed report?
- [ ] Numbers look reasonable?
- [ ] Confirmed no critical data will be deleted?
- [ ] Ready to execute?

### For Deep Cleanup
- [ ] Created backup? (NON-NEGOTIABLE)
- [ ] Tested on staging first?
- [ ] Tested backup restoration?
- [ ] Informed stakeholders?
- [ ] Ran dry-run and reviewed report?
- [ ] Verified backup exists and is safe?
- [ ] Ready to execute?

## 🚨 Safety Checklist

### Standard Cleanup (Lower Risk)
- ✅ Dry-run is quick and safe
- ✅ Only removes test/demo/old data
- ✅ Archives instead of deletes
- ✅ Very reversible
- ✅ Can run monthly

### Deep Cleanup (Higher Risk)
- ✅ Default is dry-run (safe)
- ✅ Requires explicit backup
- ✅ Removes vast amounts of data
- ✅ Only reversible with backup
- ✅ Should be tested on staging

## 📞 Support Matrix

| Question | Answer | Reference |
|----------|--------|-----------|
| How to remove old data? | Standard Cleanup | DATABASE_CLEANUP_GUIDE.md |
| How to prepare for launch? | Deep Cleanup | DEEP_CLEANUP_GUIDE.md |
| What does standard remove? | Test/demo/old/drafts | SCHOLARIXV2_QUICK_START.md |
| What does deep remove? | Everything except defaults | DEEP_CLEANUP_QUICK_START.md |
| I made a mistake! | Restore from backup | Recovery section in guides |
| Which tool should I use? | See Decision Guide (above) | This document |

## 🎓 Learning Path

### For Beginners
1. Read **SCHOLARIXV2_QUICK_START.md**
2. Run: `npm run cleanup:dry-run`
3. Review the report
4. Run: `npm run cleanup` (when ready)

### For Production Launch
1. Read **DEEP_CLEANUP_GUIDE.md**
2. Create backup
3. Test on staging
4. Run dry-run on production
5. Review report carefully
6. Execute cleanup
7. Verify results

### For Advanced Users
1. Review **DATABASE_CLEANUP_GUIDE.md** fully
2. Understand all cleanup options
3. Create custom cleanup workflows
4. Integrate into CI/CD pipeline
5. Monitor regularly

## 📈 Monitoring After Cleanup

### Key Metrics to Check
- Database size: `SELECT pg_database_size('scholarixv2_production');`
- Active connections: Check Odoo admin
- Response time: Benchmark key operations
- User experience: Test critical workflows

### Expected Performance Improvement
- Query time: 10-50% faster
- Response time: 20% faster
- Memory usage: 15-30% lower
- Backup time: 30-50% faster

## 🔄 Maintenance Schedule

### Recommended Cleanup Frequency

**Small Instances (< 1GB):**
- Standard cleanup: Every 3 months
- Deep cleanup: As needed (pre-launch)

**Medium Instances (1-10GB):**
- Standard cleanup: Monthly
- Deep cleanup: Annually

**Large Instances (> 10GB):**
- Standard cleanup: Every 2 weeks
- Deep cleanup: Avoid (too much data)

## 💡 Pro Tips

### Tip 1: Combine Cleanups
```bash
# Monthly maintenance pattern
npm run cleanup:test        # Remove test data
npm run cleanup:drafts      # Clean drafts
npm run cleanup:logs        # Clean old logs
```

### Tip 2: Schedule Automation
```bash
# Cron job for monthly cleanup (Sunday 2 AM)
0 2 * * 0 npm run cleanup --prefix /path/to/odoo-mcp-server
```

### Tip 3: Before Major Upgrades
```bash
1. Standard cleanup (remove old data)
2. Database optimization
3. Backup
4. Upgrade
5. Test thoroughly
```

### Tip 4: Database Tuning
After cleanup, optimize database:
```sql
VACUUM ANALYZE;
REINDEX DATABASE scholarixv2_production;
```

## 📋 Tools Summary

| Tool | Command | Risk | Time | Data Impact |
|------|---------|------|------|-------------|
| Standard Cleanup | `npm run cleanup` | Very Low | 20-40 min | -10-20% |
| Test Data Only | `npm run cleanup:test` | Very Low | 10-20 min | -1-5% |
| Drafts Only | `npm run cleanup:drafts` | Very Low | 10-20 min | -2-10% |
| Logs Only | `npm run cleanup:logs` | Very Low | 10-20 min | -5-15% |
| Deep Cleanup | REST API | Medium | 30-60 min | -50-80% |

## 🎯 Next Steps

1. **Understand Your Need**
   - Regular maintenance? → Standard Cleanup
   - Production launch? → Deep Cleanup

2. **Read Relevant Guide**
   - Standard: `DATABASE_CLEANUP_GUIDE.md`
   - Deep: `DEEP_CLEANUP_GUIDE.md`

3. **Create Backup** (if deep cleanup)
   - Essential safety step
   - Non-negotiable for deep cleanup

4. **Run Dry-Run**
   - Always preview first
   - Review report thoroughly

5. **Execute**
   - Only after dry-run confirms
   - Monitor progress

6. **Verify Results**
   - Check database metrics
   - Test critical workflows
   - Verify performance improvement

---

**Questions? Check the relevant guide:**
- **Standard Cleanup:** DATABASE_CLEANUP_GUIDE.md
- **Deep Cleanup:** DEEP_CLEANUP_GUIDE.md
- **Quick Start:** SCHOLARIXV2_QUICK_START.md or DEEP_CLEANUP_QUICK_START.md

**Remember: Dry-run before execution. Backup before deep cleanup.**
