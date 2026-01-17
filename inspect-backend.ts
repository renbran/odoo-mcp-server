#!/usr/bin/env node

/**
 * Direct Odoo Backend Inspector
 * Tests connection and runs module queries directly
 */

import dotenv from 'dotenv';
import { OdooClient } from './src/odoo-client.js';

// Load environment
dotenv.config();

const config = {
  url: process.env.ODOO_URL || 'https://erp.sgctech.ai',
  db: process.env.ODOO_DB || 'commission_ax',
  username: process.env.ODOO_USERNAME || 'info@scholarixglobal.com',
  password: process.env.ODOO_PASSWORD || '123456',
};

console.log('🔍 ODOO BACKEND INSPECTOR');
console.log('========================\n');
console.log('Configuration:');
console.log(`  URL: ${config.url}`);
console.log(`  Database: ${config.db}`);
console.log(`  Username: ${config.username}`);
console.log();

async function main() {
  try {
    // Create client
    console.log('📡 Connecting to Odoo...');
    const client = new OdooClient(config);
    
    // Test authentication
    console.log('🔐 Authenticating...');
    await client.authenticate();
    console.log('✅ Authentication successful!\n');

    // Query uninstalled modules
    console.log('📦 Fetching uninstalled modules...');
    const modules = await client.search('ir.module.module', [
      ['state', '!=', 'installed']
    ]);
    
    console.log(`✅ Found ${modules.length} uninstalled modules\n`);

    if (modules.length > 0) {
      // Get details for first 20
      const limit = Math.min(20, modules.length);
      console.log(`📋 Details for first ${limit} modules:\n`);
      
      const details = await client.read('ir.module.module', modules.slice(0, limit), [
        'name',
        'version',
        'description',
        'state',
        'depends',
        'category'
      ]);

      details.forEach((mod: any) => {
        console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
        console.log(`📌 ${mod.name}`);
        console.log(`   Version: ${mod.version}`);
        console.log(`   Category: ${mod.category || 'Uncategorized'}`);
        console.log(`   Description: ${mod.description || 'No description'}`);
        console.log(`   Dependencies: ${mod.depends.length > 0 ? mod.depends.join(', ') : 'None'}`);
        console.log(`   State: ${mod.state}`);
      });

      console.log(`\n✅ Total modules shown: ${limit}/${modules.length}`);
    }

    console.log('\n✅ Backend inspection complete!');

  } catch (error: any) {
    console.error('❌ Error:', error.message);
    console.error('\nFull error:');
    console.error(error);
    process.exit(1);
  }
}

main();
