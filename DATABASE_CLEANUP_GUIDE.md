# ScholarixV2 Database Cleanup Guide

## Overview

This guide provides comprehensive instructions for connecting to the ScholarixV2 database and performing production-ready cleanup operations using the Odoo MCP Server.

## Prerequisites

- Node.js 18.0.0 or later
- Access to ScholarixV2 Odoo instance
- Admin credentials for the database
- Network connectivity to the Odoo server

## Setup Instructions

### 1. Configure Environment Variables

Create a `.env` file in the project root with your ScholarixV2 credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
ODOO_URL=https://scholarixv2.example.com
ODOO_DB=scholarixv2_production
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=your_secure_password_here
ODOO_API_KEY=optional_api_key_if_needed
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Build the Project

```bash
npm run build
```

## Database Cleanup Operations

### Overview of Cleanup Operations

The database cleanup tool performs the following operations:

1. **Remove Test Data** - Deletes records with "Test" or "Demo" prefixes
2. **Archive Inactive Records** - Marks old records as inactive (180+ days by default)
3. **Clean Draft Documents** - Removes draft sales orders, invoices, and purchase orders
4. **Remove Orphan Records** - Deletes orphaned line items with missing parent records
5. **Clean Activity Logs** - Removes old mail messages and completed activities
6. **Clean Attachments** - Removes old file attachments
7. **Clear Caches** - Clears web and session caches for optimal performance

### Usage

#### Option 1: Dry Run (Recommended First Step)

Preview all changes that would be made **without actually modifying the database**:

```bash
npm run cleanup:dry-run
```

This will generate a detailed report showing:
- Number of records that would be deleted
- Number of records that would be archived
- Estimated impact on database size
- Any warnings or issues encountered

#### Option 2: Full Cleanup

Execute complete database cleanup:

```bash
npm run cleanup
```

#### Option 3: Selective Cleanup

Clean up specific types of records:

```bash
# Remove test data only
npm run cleanup:test

# Clean draft documents only
npm run cleanup:drafts

# Clean activity logs only
npm run cleanup:logs
```

### Advanced Configuration

You can customize cleanup parameters by modifying the cleanup call:

```typescript
// Custom cleanup with specific parameters
const cleanupOptions = {
  instance: 'scholarixv2',
  removeTestData: true,
  removeInactivRecords: true,
  cleanupDrafts: true,
  archiveOldRecords: true,
  optimizeDatabase: true,
  daysThreshold: 180,  // Archive records older than 180 days
  dryRun: false        // Set to true to preview changes
};
```

## Using the MCP Tool Directly

### With curl

```bash
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "odoo_database_cleanup",
    "arguments": {
      "instance": "scholarixv2",
      "removeTestData": true,
      "removeInactivRecords": true,
      "cleanupDrafts": true,
      "daysThreshold": 180,
      "dryRun": true
    }
  }'
```

### With JavaScript/Node.js

```typescript
import { OdooClient } from './src/odoo-client';
import { DatabaseCleanup } from './src/database-cleanup';

const client = new OdooClient({
  url: process.env.ODOO_URL!,
  db: process.env.ODOO_DB!,
  username: process.env.ODOO_USERNAME!,
  password: process.env.ODOO_PASSWORD!,
});

// Authenticate
await client.authenticate();

// Create cleanup instance
const cleanup = new DatabaseCleanup(async () => client);

// Execute cleanup
const report = await cleanup.executeFullCleanup({
  instance: 'scholarixv2',
  dryRun: true,  // Preview first
  daysThreshold: 180,
});

console.log(report);
```

## Cleanup Report Structure

After cleanup execution, you'll receive a detailed JSON report:

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
    "cacheCleared": true,
    "totalRecordsProcessed": 1539
  },
  "details": [
    {
      "operation": "remove_test_data",
      "model": "res.partner",
      "recordsAffected": 15,
      "details": "Removed 15 test/demo records",
      "status": "success"
    }
    // ... more details
  ],
  "warnings": [],
  "errors": []
}
```

## Best Practices

### 1. Always Start with Dry Run

```bash
npm run cleanup:dry-run
```

Review the report thoroughly before executing actual cleanup.

### 2. Backup Your Database

Before running cleanup in production:

```bash
# Create database backup (depends on your database system)
pg_dump scholarixv2_production > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 3. Schedule Cleanup During Maintenance Window

- Run cleanup during low-traffic periods
- Inform users of potential service interruption
- Allow sufficient time for the operation to complete

### 4. Monitor After Cleanup

After cleanup completion:

- Check application performance
- Verify no data loss occurred
- Test critical workflows

### 5. Archive Instead of Delete

For important records, the tool archives (sets `active=false`) rather than deletes, allowing recovery if needed.

## Troubleshooting

### Authentication Failures

**Problem**: "Authentication failed" error

**Solution**:
1. Verify credentials in `.env` file
2. Check that the user has admin rights
3. Ensure the Odoo instance is accessible
4. Verify network connectivity

```bash
# Test connection
curl https://scholarixv2.example.com
```

### Timeout Errors

**Problem**: "Request timeout" error

**Solution**:
1. Increase timeout value: Set `ODOO_TIMEOUT=60000` in `.env`
2. Run cleanup on records in smaller batches
3. Check server performance during cleanup

### Permission Denied

**Problem**: "Permission denied" or "Access denied" error

**Solution**:
1. Ensure user is admin
2. Check role-based access control settings
3. Verify no restrictions on the models being cleaned

### Orphan Records Not Removed

**Problem**: Some orphan records remain after cleanup

**Solution**:
1. Run cleanup again - some orphans may require multiple passes
2. Check for circular references in data
3. Manually review and delete stubborn records

## Safety Features

The cleanup tool includes several safety mechanisms:

1. **Dry Run Mode** - Preview all changes without modification
2. **Logging** - All operations are logged for audit trail
3. **Error Handling** - Graceful error handling with detailed error messages
4. **Selective Operations** - Choose which cleanup operations to perform
5. **Configurable Thresholds** - Adjust age thresholds for archiving

## Advanced Topics

### Custom Cleanup Policies

You can extend the DatabaseCleanup class for custom cleanup logic:

```typescript
class CustomCleanup extends DatabaseCleanup {
  async removeCustomTestData(client: OdooClient) {
    // Add your custom cleanup logic here
  }
}
```

### Integration with CI/CD

Add cleanup to your deployment pipeline:

```yaml
# Example GitHub Actions
- name: Database Cleanup
  run: npm run cleanup:dry-run
```

### Automated Scheduling

Set up cron jobs for regular cleanup:

```bash
# Cleanup every Sunday at 2 AM
0 2 * * 0 cd /path/to/odoo-mcp-server && npm run cleanup
```

## Support and Resources

- **Odoo Documentation**: https://www.odoo.com/documentation
- **MCP Server Issues**: Check the project repository
- **Odoo Community**: https://www.odoo-community.org

## Important Notes

⚠️ **WARNING**: Database cleanup operations are potentially destructive. Always:

1. Create a backup before running in production
2. Run in dry-run mode first
3. Test in a staging environment
4. Have a rollback plan ready

## License

This database cleanup tool is part of the Odoo MCP Server project and is licensed under the MIT License.
