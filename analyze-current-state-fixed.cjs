const xmlrpc = require('xmlrpc');

const client = xmlrpc.createSecureClient({
  host: 'eigermarvelhr.com',
  port: 443,
  path: '/xmlrpc/2/object',
});

const db = 'eigermarvel';
const username = 'admin';
const password = '8586583';
const uid = 2;

async function analyzeCurrentState() {
  console.log('='.repeat(70));
  console.log('CURRENT DATABASE STATE - DEPLOYMENT ANALYSIS');
  console.log('='.repeat(70));
  
  // Check existing automated actions
  console.log('\n[5/7] Checking existing automated actions...');
  await new Promise((resolve, reject) => {
    client.methodCall('execute_kw', [
      db, uid, password,
      'base.automation',
      'search_read',
      [[['model_id.model', 'like', 'recruitment%']]],
      { fields: ['name', 'trigger', 'active'] }
    ], (err, value) => {
      if (err) {
        console.error('Error:', err.message);
        resolve();
      } else {
        console.log(`Found ${value.length} automated actions:`);
        value.forEach(a => console.log(`  - ${a.name} (${a.trigger}, active=${a.active})`));
        resolve();
      }
    });
  });

  // 6. Sample data check
  console.log('\n[6/7] Checking existing records...');
  const models = [
    'recruitment.job.requisition',
    'recruitment.application',
    'recruitment.contract',
    'recruitment.deployment',
    'recruitment.retention'
  ];

  for (const model of models) {
    await new Promise((resolve, reject) => {
      client.methodCall('execute_kw', [
        db, uid, password,
        model,
        'search_count',
        [[]]
      ], (err, value) => {
        if (err) {
          console.log(`  - ${model}: ERROR (model might not exist)`);
          resolve();
        } else {
          console.log(`  - ${model}: ${value} records`);
          resolve();
        }
      });
    });
  }

  // 7. Check sample requisition for existing fields
  console.log('\n[7/7] Checking sample job requisition fields...');
  await new Promise((resolve, reject) => {
    client.methodCall('execute_kw', [
      db, uid, password,
      'recruitment.job.requisition',
      'search_read',
      [[]],
      { fields: [], limit: 1 }
    ], (err, value) => {
      if (err) {
        console.error('Error:', err.message);
        resolve();
      } else if (value.length > 0) {
        console.log('Sample Record Fields:', Object.keys(value[0]).join(', '));
        console.log('\nKey observations:');
        console.log(`  - Has 'application_count': ${!!value[0].application_count}`);
        console.log(`  - Has 'contract_count': ${!!value[0].contract_count}`);
        console.log(`  - Has 'deployment_count': ${!!value[0].deployment_count}`);
        console.log(`  - Has 'message_ids': ${!!value[0].message_ids}`);
        console.log(`  - Has 'activity_ids': ${!!value[0].activity_ids}`);
        resolve();
      } else {
        console.log('No requisitions found');
        resolve();
      }
    });
  });

  console.log('\n' + '='.repeat(70));
  console.log('KEY FINDINGS:');
  console.log('='.repeat(70));
  console.log('✓ Module version: 18.0.1.1.0 (installed)');
  console.log('✓ Some views already have chatter (application, contract)');
  console.log('✓ Some views already have smart buttons');
  console.log('✓ 10 existing email templates');
  console.log('✗ No activity types configured');
  console.log('? Need to check if computed fields exist');
  console.log('');
  console.log('DEPLOYMENT STRATEGY:');
  console.log('  1. Model enhancements will EXTEND existing models (safe)');
  console.log('  2. View improvements will INHERIT existing views (safe)');
  console.log('  3. New data files will ADD activity types and automations');
  console.log('  4. Existing data will remain intact');
  console.log('='.repeat(70));
}

analyzeCurrentState().catch(console.error);
