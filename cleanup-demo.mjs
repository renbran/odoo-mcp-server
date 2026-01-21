#!/usr/bin/env node

import * as dotenv from 'dotenv';
import { OdooClient } from './dist/odoo-client.js';
import { DatabaseCleanup } from './dist/database-cleanup.js';

dotenv.config();

const client = new OdooClient({
  url: process.env.ODOO_URL,
  db: process.env.ODOO_DB,
  username: process.env.ODOO_USERNAME,
  password: process.env.ODOO_PASSWORD,
});

// Create cleanup instance with proper client getter
const cleanup = new DatabaseCleanup(async () => client);

(async () => {
  try {
    console.log('🔍 Connecting to ScholarixV2 database...');
    const authResult = await client.authenticate();
    
    if (!authResult.success) {
      console.error('❌ Authentication failed! Check your credentials.');
      console.error('Details:', authResult.error);
      process.exit(1);
    }
    
    console.log('✅ Connected successfully!');
    console.log(`✅ User ID: ${authResult.data?.uid}`);
    console.log(`✅ Server Version: ${authResult.data?.serverVersion}\n`);
    
    console.log('🧹 Starting demo data cleanup (DRY RUN)...\n');
    
    const dryRun = process.env.DRY_RUN !== 'false';
    
    const result = await cleanup.executeFullCleanup({
      instance: 'scholarixv2',
      removeTestData: true,
      removeInactivRecords: false,
      cleanupDrafts: false,
      archiveOldRecords: false,
      optimizeDatabase: false,
      dryRun: dryRun,
    });
    
    console.log('\n📊 CLEANUP RESULTS:');
    console.log('═'.repeat(60));
    console.log(`Mode: ${result.dryRun ? 'DRY RUN (Preview Only)' : 'ACTUAL CLEANUP'}`);
    console.log(`Timestamp: ${result.timestamp}`);
    console.log('\nSummary:');
    console.log(`  • Test/Demo Data Removed: ${result.summary.testDataRemoved}`);
    console.log(`  • Total Records Processed: ${result.summary.totalRecordsProcessed}`);
    console.log(`  • Status: ${result.success ? '✅ Success' : '⚠️ Warnings/Errors'}`);
    
    if (result.details.length > 0) {
      console.log('\nDetails:');
      result.details.forEach(detail => {
        const icon = detail.status === 'success' ? '✅' : detail.status === 'warning' ? '⚠️' : '❌';
        console.log(`  ${icon} [${detail.model}] ${detail.details}`);
      });
    }
    
    if (result.warnings.length > 0) {
      console.log('\nWarnings:');
      result.warnings.forEach(w => console.log(`  ⚠️ ${w}`));
    }
    
    if (result.errors.length > 0) {
      console.log('\nErrors:');
      result.errors.forEach(e => console.log(`  ❌ ${e}`));
    }
    
    console.log('═'.repeat(60));
    
    if (dryRun) {
      console.log('\n💡 This is a DRY RUN. Set DRY_RUN=false to actually delete data.');
    } else {
      console.log('\n✅ Demo cleanup completed successfully!');
    }
    
  } catch (error) {
    console.error('❌ Error during cleanup:', error instanceof Error ? error.message : String(error));
    if (error instanceof Error) {
      console.error('Stack:', error.stack);
    }
    process.exit(1);
  }
})();
