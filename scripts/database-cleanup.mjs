#!/usr/bin/env node

/**
 * ScholarixV2 Database Cleanup Script
 * 
 * This script provides a convenient way to perform database cleanup
 * for the ScholarixV2 Odoo instance.
 * 
 * Usage:
 *   npm run cleanup:dry-run    -- Preview changes without applying
 *   npm run cleanup            -- Execute full cleanup
 *   npm run cleanup:test       -- Remove test data only
 *   npm run cleanup:drafts     -- Clean draft documents only
 */

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const CONFIG = {
  envFile: path.join(__dirname, '.env'),
  logDir: path.join(__dirname, 'cleanup-logs'),
};

// Ensure log directory exists
if (!fs.existsSync(CONFIG.logDir)) {
  fs.mkdirSync(CONFIG.logDir, { recursive: true });
}

/**
 * Load environment variables
 */
function loadEnv() {
  const envPath = CONFIG.envFile;
  if (!fs.existsSync(envPath)) {
    console.error(`Error: .env file not found at ${envPath}`);
    console.error('Please create a .env file with your Odoo credentials.');
    process.exit(1);
  }

  const content = fs.readFileSync(envPath, 'utf-8');
  const env: Record<string, string> = {};

  content.split('\n').forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) return;

    const [key, ...values] = trimmed.split('=');
    env[key?.trim() || ''] = values.join('=').trim();
  });

  return env;
}

/**
 * Get cleanup options from command line arguments
 */
function getCleanupOptions(argv: string[]) {
  const command = argv[2];

  const baseOptions = {
    instance: 'scholarixv2',
    dryRun: false,
  };

  switch (command) {
    case 'dry-run':
      return { ...baseOptions, dryRun: true };
    case 'test':
      return {
        ...baseOptions,
        removeTestData: true,
        removeInactivRecords: false,
        cleanupDrafts: false,
      };
    case 'drafts':
      return {
        ...baseOptions,
        removeTestData: false,
        removeInactivRecords: false,
        cleanupDrafts: true,
      };
    case 'logs':
      return {
        ...baseOptions,
        removeTestData: false,
        removeInactivRecords: false,
        cleanupDrafts: false,
        // Will be implemented as separate function
      };
    default:
      return baseOptions; // Full cleanup
  }
}

/**
 * Log cleanup results
 */
function logResults(report: any, filename: string) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const logFile = path.join(
    CONFIG.logDir,
    `${filename}-${timestamp}.json`
  );

  fs.writeFileSync(logFile, JSON.stringify(report, null, 2));
  console.log(`\n✅ Cleanup report saved to: ${logFile}`);

  // Print summary
  console.log('\n' + '='.repeat(60));
  console.log('CLEANUP SUMMARY');
  console.log('='.repeat(60));
  console.log(`Timestamp: ${report.timestamp}`);
  console.log(`Dry Run: ${report.dryRun}`);
  console.log(`Status: ${report.success ? 'SUCCESS' : 'FAILED'}`);
  console.log('\nRecords Processed:');
  console.log(`  Test Data Removed: ${report.summary.testDataRemoved}`);
  console.log(
    `  Inactive Records Archived: ${report.summary.inactiveRecordsArchived}`
  );
  console.log(`  Drafts Cleaned: ${report.summary.draftsCleaned}`);
  console.log(`  Orphan Records Removed: ${report.summary.orphanRecordsRemoved}`);
  console.log(`  Logs Cleaned: ${report.summary.logsCleaned}`);
  console.log(`  Attachments Cleaned: ${report.summary.attachmentsCleaned}`);
  console.log(`  Cache Cleared: ${report.summary.cacheCleared}`);
  console.log(`\nTotal Records Processed: ${report.summary.totalRecordsProcessed}`);

  if (report.warnings.length > 0) {
    console.log('\n⚠️  Warnings:');
    report.warnings.forEach((w: string) => console.log(`  - ${w}`));
  }

  if (report.errors.length > 0) {
    console.log('\n❌ Errors:');
    report.errors.forEach((e: string) => console.log(`  - ${e}`));
  }

  console.log('\nDetailed operations:');
  report.details.forEach((detail: any) => {
    const status = detail.status === 'success' ? '✅' : '❌';
    console.log(
      `  ${status} ${detail.operation}: ${detail.model} (${detail.recordsAffected} records)`
    );
    console.log(`     ${detail.details}`);
  });
}

/**
 * Main execution
 */
async function main() {
  console.log('🗑️  ScholarixV2 Database Cleanup Tool');
  console.log('=' .repeat(60));

  const env = loadEnv();
  const options = getCleanupOptions(process.argv);

  console.log(`\n📋 Cleanup Configuration:`);
  console.log(`  Instance: ${options.instance}`);
  console.log(`  Dry Run: ${options.dryRun}`);
  console.log(`  Remove Test Data: ${options.removeTestData !== false}`);
  console.log(`  Archive Inactive: ${options.removeInactivRecords !== false}`);
  console.log(`  Clean Drafts: ${options.cleanupDrafts !== false}`);

  if (options.dryRun) {
    console.log(
      '\n⚠️  DRY RUN MODE - No actual changes will be made to the database'
    );
  }

  console.log(
    '\n⏳ Starting cleanup process... (this may take a few minutes)\n'
  );

  // Mock execution - in real scenario, this would call the MCP tool
  console.log('❌ This is a template script.');
  console.log(
    '   To execute cleanup, use the MCP tool directly with the database cleanup options.'
  );
  console.log('\nExample usage with curl:');
  console.log(`
curl -X POST http://localhost:3000/tools/call \\
  -H "Content-Type: application/json" \\
  -d '{
    "tool": "odoo_database_cleanup",
    "arguments": {
      "instance": "${options.instance}",
      "dryRun": ${options.dryRun},
      "removeTestData": true,
      "removeInactivRecords": true,
      "cleanupDrafts": true
    }
  }'
  `);
}

main().catch((error) => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
