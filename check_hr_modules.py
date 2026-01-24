#!/usr/bin/env python3
"""
Check HR UAE, Payroll, and Commission modules on Odoo instances
"""

import xmlrpc.client
import json
from datetime import datetime

# Instance configurations
INSTANCES = {
    'local': {
        'url': 'http://localhost:8069',
        'db': 'odoo17_test',
        'username': 'admin',
        'password': 'admin',
        'version': 'v17'
    },
    'osusproperties': {
        'url': 'https://erposus.com',
        'db': 'osusproperties',
        'username': 'salescompliance@osusproperties.com',
        'password': '8586583',
        'version': 'v17'
    }
}

def connect_odoo(config):
    """Connect to Odoo instance"""
    common = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/common")
    uid = common.authenticate(config['db'], config['username'], config['password'], {})
    
    if not uid:
        raise Exception(f"Authentication failed for {config['url']}")
    
    models = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/object")
    return uid, models, config

def search_modules(uid, models, config, keywords):
    """Search for modules by keywords"""
    domain = ['|'] * (len(keywords) - 1)
    for keyword in keywords:
        domain.extend([('name', 'ilike', keyword)])
    
    module_ids = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.module.module', 'search',
        [domain]
    )
    
    if not module_ids:
        return []
    
    modules = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.module.module', 'read',
        [module_ids, ['name', 'state', 'shortdesc', 'summary', 'installed_version']]
    )
    
    return modules

def main():
    """Main function"""
    print("=" * 80)
    print("HR UAE, Payroll & Commission Module Check")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # Keywords to search for
    keywords = ['hr_uae', 'hr_payroll', 'payroll', 'commission', 'commission_ax']
    
    for instance_name, config in INSTANCES.items():
        print(f"\n{'=' * 80}")
        print(f"Instance: {instance_name} ({config['version']})")
        print(f"URL: {config['url']}")
        print(f"Database: {config['db']}")
        print(f"{'=' * 80}\n")
        
        try:
            uid, models, cfg = connect_odoo(config)
            print(f"✓ Connected successfully (UID: {uid})\n")
            
            modules = search_modules(uid, models, cfg, keywords)
            
            if not modules:
                print("⚠ No HR/Payroll/Commission modules found\n")
                results[instance_name] = []
                continue
            
            # Categorize modules by state
            installed = [m for m in modules if m['state'] == 'installed']
            uninstalled = [m for m in modules if m['state'] in ['uninstalled', 'to install']]
            
            print(f"Found {len(modules)} relevant modules:")
            print(f"  - Installed: {len(installed)}")
            print(f"  - Uninstalled/Available: {len(uninstalled)}\n")
            
            if installed:
                print("INSTALLED MODULES:")
                print("-" * 80)
                for mod in installed:
                    print(f"  ✓ {mod['name']}")
                    print(f"    Description: {mod['shortdesc']}")
                    if mod.get('installed_version'):
                        print(f"    Version: {mod['installed_version']}")
                    print()
            
            if uninstalled:
                print("AVAILABLE (Not Installed):")
                print("-" * 80)
                for mod in uninstalled:
                    print(f"  ○ {mod['name']}")
                    print(f"    Description: {mod['shortdesc']}")
                    print()
            
            results[instance_name] = {
                'installed': installed,
                'uninstalled': uninstalled
            }
            
        except Exception as e:
            print(f"✗ Error connecting to {instance_name}: {str(e)}\n")
            results[instance_name] = {'error': str(e)}
    
    # Save results to JSON
    output_file = f"hr_modules_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 80}\n")
    
    # Print comparison summary
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    
    osus_installed = set()
    sgc_installed = set()
    
    if 'osusproperties' in results and 'installed' in results['osusproperties']:
        osus_installed = {m['name'] for m in results['osusproperties']['installed']}
    
    if 'sgctechai' in results and 'installed' in results['sgctechai']:
        sgc_installed = {m['name'] for m in results['sgctechai']['installed']}
    
    print(f"\nModules in OSUSPROPERTIES but NOT in SGCTECHAI:")
    missing_in_sgc = osus_installed - sgc_installed
    if missing_in_sgc:
        for mod in missing_in_sgc:
            print(f"  → {mod}")
    else:
        print("  (None)")
    
    print(f"\nModules in SGCTECHAI but NOT in OSUSPROPERTIES:")
    missing_in_osus = sgc_installed - osus_installed
    if missing_in_osus:
        for mod in missing_in_osus:
            print(f"  → {mod}")
    else:
        print("  (None)")
    
    print(f"\nModules in BOTH instances:")
    common = osus_installed & sgc_installed
    if common:
        for mod in common:
            print(f"  ✓ {mod}")
    else:
        print("  (None)")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
