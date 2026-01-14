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

    // Get today's date in YYYY-MM-DD format
    const today = new Date().toISOString().split('T')[0];
    console.log('📅 Searching for leads changed today:', today);

    // Search for leads that had stage changes today
    const domain = [
      ['type', '=', 'opportunity'],
      ['write_date', '>=', today + ' 00:00:00'],
      ['write_date', '<=', today + ' 23:59:59']
    ];

    const fields = ['name', 'user_id', 'stage_id', 'write_date', 'partner_id', 'expected_revenue'];

    console.log('🔍 Searching CRM leads...');
    const leadIds = await odooCall('object', 'execute_kw', [
      'eigermarvel',
      uid,
      '8586583',
      'crm.lead',
      'search_read',
      [domain],
      { fields: fields, limit: 100 }
    ]);

    console.log('\n📊 Found', leadIds.length, 'leads with changes today:\n');

    if (leadIds.length === 0) {
      console.log('No leads were modified today.');
      return;
    }

    // Group by salesperson
    const bySalesperson = {};
    leadIds.forEach(lead => {
      const salesperson = lead.user_id ? lead.user_id[1] : 'Unassigned';
      if (!bySalesperson[salesperson]) {
        bySalesperson[salesperson] = [];
      }
      bySalesperson[salesperson].push(lead);
    });

    // Display results
    for (const [salesperson, leads] of Object.entries(bySalesperson)) {
      console.log('👤', salesperson, '(' + leads.length + ' leads)');
      leads.forEach(lead => {
        const stage = lead.stage_id ? lead.stage_id[1] : 'No Stage';
        const partner = lead.partner_id ? lead.partner_id[1] : 'No Customer';
        const revenue = lead.expected_revenue || 0;
        console.log('  📌', lead.name);
        console.log('     Stage:', stage);
        console.log('     Customer:', partner);
        console.log('     Expected Revenue: $' + revenue.toFixed(2));
        console.log('     Last Updated:', lead.write_date);
        console.log('');
      });
    }

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();
