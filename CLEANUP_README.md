# ScholarixV2 Database Cleanup Integration

## Overview

This project now includes comprehensive database cleanup capabilities for the ScholarixV2 Odoo instance, enabling production-ready database maintenance with full safety features and detailed reporting.

## What's New

### ✨ New Features Added

1. **Database Cleanup Module** - Complete cleanup system for:
   - Removing test/demo data
   - Archiving inactive records
   - Cleaning draft documents
   - Removing orphan records
   - Cleaning activity logs
   - Removing old attachments
   - Clearing caches

2. **MCP Tool Integration** - `odoo_database_cleanup` tool with:
   - Full parameter validation
   - Dry-run support
   - Comprehensive reporting
   - Error handling

3. **NPM Scripts** - Easy command-line access:
   - `npm run cleanup:dry-run` - Preview changes
   - `npm run cleanup` - Execute full cleanup
   - `npm run cleanup:test` - Test data only
   - `npm run cleanup:drafts` - Draft cleanup only
   - `npm run cleanup:logs` - Log cleanup only

4. **Comprehensive Documentation**:
   - [DATABASE_CLEANUP_GUIDE.md](DATABASE_CLEANUP_GUIDE.md) - Full reference
   - [SCHOLARIXV2_QUICK_START.md](SCHOLARIXV2_QUICK_START.md) - Quick start guide
   - [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details

## Quick Start

### 1. Configuration

```bash
# Configure your ScholarixV2 instance
cp .env.example .env

# Edit .env with your credentials:
# ODOO_URL=https://scholarixv2.example.com
# ODOO_DB=scholarixv2_production
# ODOO_USERNAME=admin@example.com
# ODOO_PASSWORD=your_password
```

### 2. Install Dependencies

```bash
npm install
npm run build
```

### 3. Test Connection

```bash
npm run test
```

### 4. Preview Cleanup (Always Start Here!)

```bash
npm run cleanup:dry-run
```

### 5. Execute Cleanup

```bash
npm run cleanup
```

## Key Safety Features

✅ **Dry Run Mode** - Preview all changes without modifications
✅ **Logging** - Complete audit trail of all operations
✅ **Archiving** - Old records archived (not deleted) when possible
✅ **Error Handling** - Detailed error messages and recovery info
✅ **Selective Operations** - Choose which cleanup operations to perform
✅ **Configurable** - Adjust thresholds to your needs

## Files Added/Modified

### New Files
- `src/database-cleanup.ts` - Core cleanup implementation
- `scripts/database-cleanup.mjs` - Helper script
- `.env.example` - Configuration template
- `DATABASE_CLEANUP_GUIDE.md` - Full documentation
- `SCHOLARIXV2_QUICK_START.md` - Quick start guide
- `IMPLEMENTATION_SUMMARY.md` - Implementation details

### Modified Files
- `src/tools.ts` - Added cleanup tool
- `package.json` - Added cleanup scripts
- `dist/` - Compiled JavaScript files

## Usage Examples

### Using NPM Scripts

```bash
# Dry run first
npm run cleanup:dry-run

# After reviewing, execute
npm run cleanup
```

### Using cURL

```bash
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "odoo_database_cleanup",
    "arguments": {
      "instance": "scholarixv2",
      "dryRun": true
    }
  }'
```

### Using TypeScript

```typescript
import { DatabaseCleanup } from './src/database-cleanup';

const cleanup = new DatabaseCleanup(async () => client);
const report = await cleanup.executeFullCleanup({
  instance: 'scholarixv2',
  dryRun: true,
});
```

## Cleanup Operations

### Test Data Removal
Removes records with "Test" or "Demo" prefixes from:
- Partners/Contacts
- Sales Orders
- Invoices
- Stock Moves

### Inactive Records Archiving
Archives records with no activity for 180+ days from:
- Partners
- Sales Orders
- Invoices

### Draft Document Cleanup
Removes unsaved documents:
- Draft Sales Orders
- Draft Invoices
- Draft Purchase Orders

### Orphan Record Removal
Deletes orphaned records:
- Sales Order Lines without Order
- Invoice Lines without Invoice

### Activity Log Cleanup
Removes old records:
- Mail Messages (180+ days old)
- Completed Activities (180+ days old)

### Attachment Cleanup
Removes old attachments (180+ days old)

### Cache Clearing
Clears:
- Web cache
- Session cache

## Report Structure

Each cleanup generates a detailed JSON report containing:
- Success status
- Timestamp
- Summary statistics
- Detailed operation logs
- Warnings and errors

Example:
```json
{
  "success": true,
  "timestamp": "2024-01-19T10:30:45.123Z",
  "dryRun": false,
  "summary": {
    "testDataRemoved": 42,
    "inactiveRecordsArchived": 156,
    "draftsCleaned": 23,
    "orphanRecordsRemoved": 8,
    "logsCleaned": 1243,
    "attachmentsCleaned": 67,
    "totalRecordsProcessed": 1539
  }
}
```

## Best Practices

1. **Always use dry-run first**
   ```bash
   npm run cleanup:dry-run
   ```

2. **Backup before cleanup**
   ```bash
   pg_dump scholarixv2_production > backup.sql
   ```

3. **Schedule during maintenance**
   - Run during low-traffic hours
   - Inform users of potential interruption

4. **Monitor after cleanup**
   - Check performance metrics
   - Verify no data loss
   - Test critical workflows

## Configuration Options

```typescript
interface CleanupOptions {
  instance: string;                    // Instance identifier
  removeTestData?: boolean;            // Remove test data (default: true)
  removeInactivRecords?: boolean;      // Archive inactive records (default: true)
  cleanupDrafts?: boolean;             // Remove drafts (default: true)
  archiveOldRecords?: boolean;         // Archive old records (default: true)
  optimizeDatabase?: boolean;          // Optimize DB (default: true)
  daysThreshold?: number;              // Days threshold (default: 180)
  dryRun?: boolean;                    // Preview mode (default: false)
}
```

## Troubleshooting

### Connection Issues
- Verify ODOO_URL is correct
- Check network connectivity
- Ensure Odoo instance is running
- Verify credentials in .env

### Timeout Errors
- Increase timeout in .env
- Run cleanup during off-peak hours
- Check server performance

### Permission Issues
- Ensure user is admin
- Check role-based access control
- Verify no field restrictions

## Documentation

- **Full Guide**: See [DATABASE_CLEANUP_GUIDE.md](DATABASE_CLEANUP_GUIDE.md)
- **Quick Start**: See [SCHOLARIXV2_QUICK_START.md](SCHOLARIXV2_QUICK_START.md)
- **Implementation**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## Support

For detailed information:
1. Check the relevant documentation file
2. Review cleanup report for specific issues
3. Check Odoo server logs
4. Ensure database backups exist

## Version Info

- **Project**: odoo-mcp-server
- **Cleanup Module**: v1.0.0
- **Compatibility**: Odoo 17-19
- **Added**: January 19, 2024

---

**Ready to use!** Start with:
```bash
npm install && npm run build && npm run cleanup:dry-run
```
