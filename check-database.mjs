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
    console.log('🔍 Connecting to ScholarixV2 database...\n');
    const authResult = await client.authenticate();
    
    if (!authResult.success) {
      console.error('❌ Authentication failed!');
      process.exit(1);
    }
    
    console.log('✅ Connected successfully!\n');
    console.log('📊 Database Inventory Report');
    console.log('═'.repeat(70));
    
    const modelsToCheck = [
      { name: 'sale.order', label: 'Sales Orders' },
      { name: 'sale.order.line', label: 'Sales Order Lines' },
      { name: 'account.move', label: 'Invoices/Journal Entries' },
      { name: 'res.partner', label: 'Partners/Customers' },
      { name: 'product.product', label: 'Products' },
      { name: 'product.template', label: 'Product Templates' },
      { name: 'stock.move', label: 'Stock Moves' },
      { name: 'stock.picking', label: 'Deliveries/Pickings' },
      { name: 'purchase.order', label: 'Purchase Orders' },
      { name: 'crm.lead', label: 'CRM Leads/Opportunities' },
      { name: 'project.project', label: 'Projects' },
      { name: 'project.task', label: 'Tasks' },
      { name: 'hr.employee', label: 'Employees' },
      { name: 'calendar.event', label: 'Calendar Events' },
      { name: 'mail.message', label: 'Messages/Chatter' },
      { name: 'ir.attachment', label: 'Attachments' },
    ];
    
    for (const model of modelsToCheck) {
      try {
        const result = await client.search({
          model: model.name,
          domain: [],
          limit: 10000,
        });
        
        if (result.success && result.data) {
          const count = result.data.length;
          const icon = count > 0 ? '📦' : '  ';
          console.log(`${icon} ${model.label.padEnd(35)} : ${count.toLocaleString()}`);
        } else {
          console.log(`  ${model.label.padEnd(35)} : 0`);
        }
      } catch (error) {
        console.log(`⚠️  ${model.label.padEnd(35)} : ${error instanceof Error ? error.message : 'Error'}`);
      }
    }
    
    console.log('═'.repeat(70));
    console.log('\n✅ Inventory report complete!');
    
  } catch (error) {
    console.error('❌ Error:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
})();
