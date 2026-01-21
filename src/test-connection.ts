import dotenv from 'dotenv';
import Client from 'xmlrpc';

// Load environment variables
dotenv.config();

const ODOO_URL = process.env.ODOO_URL || 'https://erposus.com';
const ODOO_DB = process.env.ODOO_DB || 'osusproperties';
const ODOO_USERNAME = process.env.ODOO_USERNAME || 'salescompliance@osusproperties.com';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || '8586583';

console.log('🔗 Testing connection to Odoo Server...');
console.log(`📍 URL: ${ODOO_URL}`);
console.log(`📦 Database: ${ODOO_DB}`);
console.log(`👤 Username: ${ODOO_USERNAME}`);

// Parse URL
const urlObj = new URL(ODOO_URL);
const protocol = urlObj.protocol === 'https:' ? 'https' : 'http';
const host = urlObj.hostname;
const port = urlObj.port || (protocol === 'https' ? 443 : 80);
const path = '/xmlrpc/2/common';

console.log(`\n📡 Connecting to: ${protocol}://${host}:${port}${path}`);

// Create XML-RPC client
const client = Client.createSecureClient({
  host: host,
  port: port,
  path: path,
  isSecure: protocol === 'https',
  rejectUnauthorized: false, // For self-signed certificates
}) as any;

// Test authentication
client.methodCall('authenticate', [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}], (error: any, value: any) => {
  if (error) {
    console.error('❌ Connection failed:', error.message);
    process.exit(1);
  }

  console.log(`✅ Successfully authenticated!`);
  console.log(`🔐 User ID: ${value}`);

  // Test a simple RPC call
  const commonClient = Client.createSecureClient({
    host: host,
    port: port,
    path: '/xmlrpc/2/object',
    isSecure: protocol === 'https',
    rejectUnauthorized: false,
  }) as any;

  commonClient.methodCall(
    'execute_kw',
    [ODOO_DB, value, ODOO_PASSWORD, 'res.partner', 'search_count', [[]]],
    (error: any, count: any) => {
      if (error) {
        console.error('❌ RPC call failed:', error.message);
        process.exit(1);
      }

      console.log(`📊 Total Partners in database: ${count}`);
      console.log('\n✨ Connection test passed successfully!');
      process.exit(0);
    }
  );
});
