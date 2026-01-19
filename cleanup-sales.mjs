#!/usr/bin/env node

import * as dotenv from 'dotenv';
import { OdooClient } from './dist/odoo-client.js';

dotenv.config();

const client = new OdooClient({
  url: process.env.ODOO_URL,
  db: process.env.ODOO_DB,
  username: process.env.ODOO_USERNAME,
  password: process.env.ODOO_PASSWORD,
});

(async () => {
  try {
    console.log('🔍 Connecting to ScholarixV2 database...');
    const authResult = await client.authenticate();
    
    if (!authResult.success) {
      console.error('❌ Authentication failed!');
      process.exit(1);
    }
    
    console.log('✅ Connected successfully!\n');
    console.log('🧹 Removing ALL sales module entries...\n');
    
    const dryRun = process.env.DRY_RUN !== 'false';
    let totalRemoved = 0;
    
    // 1. Get all sales orders (including quotations, confirmed, done)
    console.log('📋 Searching for sales orders...');
    const salesResult = await client.search({
      model: 'sale.order',
      domain: [],
      limit: 10000
    });
    
    if (salesResult.success && salesResult.data.length > 0) {
      console.log(`   Found ${salesResult.data.length} sales orders`);
      
      if (!dryRun) {
        console.log('   🗑️  Deleting sales orders...');
        const deleteResult = await client.delete({
          model: 'sale.order',
          ids: salesResult.data
        });
        
        if (deleteResult.success) {
          totalRemoved += salesResult.data.length;
          console.log(`   ✅ Deleted ${salesResult.data.length} sales orders`);
        } else {
          console.log(`   ❌ Error deleting: ${deleteResult.error?.message}`);
        }
      } else {
        console.log(`   📝 [DRY RUN] Would delete ${salesResult.data.length} sales orders`);
        totalRemoved += salesResult.data.length;
      }
    } else {
      console.log('   ✅ No sales orders found');
    }
    
    console.log('\n' + '═'.repeat(60));
    console.log(`Mode: ${dryRun ? 'DRY RUN (Preview Only)' : 'ACTUAL CLEANUP'}`);
    console.log(`Total Sales Records: ${totalRemoved}`);
    console.log('═'.repeat(60));
    
    if (dryRun) {
      console.log('\n💡 This is a DRY RUN. Set DRY_RUN=false in .env to actually delete data.');
    } else {
      console.log('\n✅ Sales module cleanup completed!');
    }
    
  } catch (error) {
    console.error('❌ Error:', error instanceof Error ? error.message : String(error));
    if (error instanceof Error) {
      console.error('Stack:', error.stack);
    }
    process.exit(1);
  }
})();
