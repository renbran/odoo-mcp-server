// Quick test connection to Odoo
import 'dotenv/config';
import { OdooClient } from './dist/odoo-client.js';

const config = {
  url: process.env.ODOO_URL,
  db: process.env.ODOO_DB,
  username: process.env.ODOO_USERNAME,
  password: process.env.ODOO_PASSWORD,
};

console.log('Testing Odoo connection...');
console.log('URL:', config.url);
console.log('DB:', config.db);
console.log('User:', config.username);

const client = new OdooClient(config);

try {
  await client.connect();
  console.log(' Connected successfully!');
  
  // Test basic query
  const models = await client.execute('ir.model', 'search_read', [[['model', 'like', 'recruitment']]], { fields: ['model', 'name'], limit: 5 });
  console.log('\n Found recruitment models:');
  models.forEach(m => console.log(`  - ${m.model}: ${m.name}`));
  
  process.exit(0);
} catch (error) {
  console.error(' Connection failed:', error.message);
  process.exit(1);
}
