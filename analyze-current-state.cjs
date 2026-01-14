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
  console.log('='.repeat(60));
  console.log('RECRUITMENT UAE MODULE - CURRENT STATE ANALYSIS');
  console.log('='.repeat(60));
  console.log('');

  // 1. Check module version and state
  console.log('[1/6] Checking module version...');
  await new Promise((resolve, reject) => {
    client.methodCall('execute_kw', [
      db, uid, password,
      'ir.module.module',
      'search_read',
      [[['name', '=', 'recruitment_uae']]],
      { fields: ['name', 'state', 'installed_version', 'latest_version'] }
    ], (err, value) => {
      if (err) {
        console.error('Error:', err);
        reject(err);
      } else {
        console.log('Module Info:', JSON.stringify(value, null, 2));
        resolve();
      }
    });
  });

  // 2. Check existing views for chatter
  console.log('\n[2/6] Checking existing views...');
  await new Promise((resolve, reject) => {
    client.methodCall('execute_kw', [
      db, uid, password,
      'ir.ui.view',
      'search_read',
      [[['model', 'in', ['recruitment.job.requisition', 'recruitment.application', 'recruitment.contract', 'recruitment.deployment']]]],
      { fields: ['name', 'model', 'type', 'arch_db'], limit: 20 }
    ], (err, value) => {
      if (err) {
        console.error('Error:', err);
        reject(err);
      } else {
        console.log(`Found ${value.length} views`);
        value.forEach(view => {
          const hasChatter = view.arch_db?.includes('oe_chatter') || false;
          const hasSmartButtons = view.arch_db?.includes('oe_button_box') || false;
          console.log(`  - ${view.name} (${view.type}): Chatter=${hasChatter}, SmartButtons=${hasSmartButtons}`);
        });
        resolve();
      }
    });
  });

  // 3. Check existing email templates
  console.log('\n[3/6] Checking existing email templates...');
  await new Promise((resolve, reject) => {
    client.methodCall('execute_kw', [
      db, uid, password,
      'mail.template',
      'search_read',
      [[['model', 'like', 'recruitment%']]],
      { fields: ['name', 'model'] }
    ], (err, value) => {
      if (err) {
        console.error('Error:', err);
        reject(err);
      } else {
        console.log(`Found ${value.length} email templates:`);
        value.forEach(t => console.log(`  - ${t.name} (${t.model})`));
        resolve();
      }
    });
  });

  // 4. Check existing activity types
  console.log('\n[4/6] Checking existing activity types...');
  await new Promise((resolve, reject) => {
    client.methodCall('execute_kw', [
      db, uid, password,
      'mail.activity.type',
      'search_read',
      [[['res_model', 'like', 'recruitment%']]],
      { fields: ['name', 'res_model'] }
    ], (err, value) => {
      if (err) {
        console.error('Error:', err);
        reject(err);
      } else {
        console.log(`Found ${value.length} activity types:`);
        value.forEach(t => console.log(`  - ${t.name} (${t.res_model})`));
        resolve();
      }
    });
  });

  // 5. Check existing automated actions
  console.log('\n[5/6] Checking existing automated actions...');
  await new Promise((resolve, reject) => {
    client.methodCall('execute_kw', [
      db, uid, password,
      'base.automation',
      'search_read',
      [[['model_id.model', 'like', 'recruitment%']]],
      { fields: ['name', 'trigger', 'state'] }
    ], (err, value) => {
      if (err) {
        console.error('Error:', err);
        reject(err);
      } else {
        console.log(`Found ${value.length} automated actions:`);
        value.forEach(a => console.log(`  - ${a.name} (${a.trigger})`));
        resolve();
      }
    });
  });

  // 6. Sample data check
  console.log('\n[6/6] Checking existing records...');
  const models = [
    'recruitment.job.requisition',
    'recruitment.application',
    'recruitment.contract',
    'recruitment.deployment'
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
          console.error(`Error checking ${model}:`, err);
          reject(err);
        } else {
          console.log(`  - ${model}: ${value} records`);
          resolve();
        }
      });
    });
  }

  console.log('\n' + '='.repeat(60));
  console.log('ANALYSIS COMPLETE');
  console.log('='.repeat(60));
}

analyzeCurrentState().catch(console.error);
