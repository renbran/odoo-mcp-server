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

    // Models to check
    const models = [
      'recruitment.job.requisition',
      'recruitment.application',
      'recruitment.contract',
      'recruitment.deployment',
      'recruitment.supplier',
      'recruitment.candidate',
      'recruitment.subscription',
      'recruitment.followup',
      'recruitment.retention'
    ];

    for (const model of models) {
      console.log(`\n\n${'='.repeat(80)}`);
      console.log(`📋 Model: ${model}`);
      console.log('='.repeat(80));

      // Get field metadata
      const fields = await odooCall('object', 'execute_kw', [
        'eigermarvel',
        uid,
        '8586583',
        model,
        'fields_get',
        [],
        { attributes: ['string', 'type', 'relation', 'required', 'readonly', 'tracking'] }
      ]);

      // Check for chatter fields
      const chatterFields = ['message_ids', 'message_follower_ids', 'activity_ids'];
      const hasChatter = chatterFields.some(f => fields[f]);

      console.log(`\n📨 Has Chatter: ${hasChatter ? '✅ YES' : '❌ NO'}`);
      if (!hasChatter) {
        console.log(`   Missing fields: ${chatterFields.filter(f => !fields[f]).join(', ')}`);
      }

      // List all fields
      console.log(`\n📊 Total Fields: ${Object.keys(fields).length}`);
      
      // Key fields to check
      const keyFields = ['name', 'state', 'stage_id', 'partner_id', 'company_id'];
      console.log('\n🔑 Key Fields:');
      keyFields.forEach(f => {
        if (fields[f]) {
          console.log(`  ✓ ${f} (${fields[f].type}) ${fields[f].tracking ? '[TRACKED]' : ''}`);
        } else {
          console.log(`  ✗ ${f} - MISSING`);
        }
      });

      // Get inheritance info
      try {
        const inheritance = await odooCall('object', 'execute_kw', [
          'eigermarvel',
          uid,
          '8586583',
          'ir.model',
          'search_read',
          [[['model', '=', model]]],
          { fields: ['name', 'model', 'inherit', 'info'] }
        ]);

        if (inheritance.length > 0 && inheritance[0].inherit) {
          console.log(`\n🔗 Inherits from: ${inheritance[0].inherit}`);
        }
      } catch (e) {
        console.log(`\n⚠️ Could not get inheritance info: ${e.message}`);
      }

      // Check for stage/state
      if (fields.state || fields.stage_id) {
        console.log('\n🎯 Workflow Fields:');
        if (fields.state) {
          console.log(`  - state field (${fields.state.type})`);
        }
        if (fields.stage_id) {
          console.log(`  - stage_id field (${fields.stage_id.type}) -> ${fields.stage_id.relation}`);
        }
      }
    }

    console.log(`\n\n${'='.repeat(80)}`);
    console.log('✅ Analysis Complete');
    console.log('='.repeat(80));

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();
