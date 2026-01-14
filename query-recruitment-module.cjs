const https = require('https');

// Helper function to make Odoo API calls
async function odooCall(service, method, args) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: { service, method, args },
      id: Math.random()
    });

    const options = {
      hostname: 'eigermarvelhr.com',
      port: 443,
      path: '/jsonrpc',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          if (json.error) {
            reject(new Error(json.error.data?.message || json.error.message));
          } else {
            resolve(json.result);
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function main() {
  try {
    // Authenticate
    console.log('🔐 Authenticating...');
    const uid = await odooCall('common', 'authenticate', ['eigermarvel', 'admin', '8586583', {}]);
    console.log('✅ Authenticated as user ID:', uid);

    // Search for recruitment_uae module
    console.log('\n🔍 Searching for recruitment_uae module...');
    const moduleData = await odooCall('object', 'execute_kw', [
      'eigermarvel',
      uid,
      '8586583',
      'ir.module.module',
      'search_read',
      [[['name', '=', 'recruitment_uae']]],
      { fields: ['name', 'state', 'summary', 'description', 'author', 'website', 'installed_version'] }
    ]);

    if (moduleData.length === 0) {
      console.log('❌ Module recruitment_uae not found');
      return;
    }

    console.log('\n📦 Module Information:');
    console.log(JSON.stringify(moduleData[0], null, 2));

    // Get models for this module
    console.log('\n🔍 Searching for models in recruitment_uae module...');
    const models = await odooCall('object', 'execute_kw', [
      'eigermarvel',
      uid,
      '8586583',
      'ir.model',
      'search_read',
      [[['modules', 'ilike', 'recruitment_uae']]],
      { fields: ['name', 'model', 'info'] }
    ]);

    console.log('\n📊 Models in recruitment_uae:');
    models.forEach(model => {
      console.log(`  - ${model.model} (${model.name})`);
    });

    // Get views
    console.log('\n🔍 Searching for views in recruitment_uae module...');
    const views = await odooCall('object', 'execute_kw', [
      'eigermarvel',
      uid,
      '8586583',
      'ir.ui.view',
      'search_read',
      [[['name', 'ilike', 'recruitment_uae']]],
      { fields: ['name', 'model', 'type', 'key'], limit: 50 }
    ]);

    console.log('\n👁️ Views:');
    views.forEach(view => {
      console.log(`  - ${view.name} (${view.type}) for ${view.model}`);
    });

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();
