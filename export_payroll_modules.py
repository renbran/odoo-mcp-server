#!/usr/bin/env python3
"""
Export Payroll Modules from OSUSPROPERTIES Instance
This script helps export hr_payroll_community and hr_payroll_account_community
"""

import xmlrpc.client
import os
import json
from pathlib import Path
from datetime import datetime

# OSUSPROPERTIES Configuration
OSUS_CONFIG = {
    'url': 'https://erposus.com',
    'db': 'osusproperties',
    'username': 'salescompliance@osusproperties.com',
    'password': '8586583'
}

# Modules to export
MODULES_TO_EXPORT = [
    'hr_payroll_community',
    'hr_payroll_account_community'
]

def connect_odoo(config):
    """Connect to Odoo instance"""
    print(f"Connecting to {config['url']}...")
    common = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/common")
    uid = common.authenticate(config['db'], config['username'], config['password'], {})
    
    if not uid:
        raise Exception("Authentication failed")
    
    models = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/object")
    print(f"✓ Connected (UID: {uid})\n")
    return uid, models, config

def get_module_info(uid, models, config, module_name):
    """Get detailed module information"""
    print(f"Fetching info for module: {module_name}")
    
    # Get module record
    module_ids = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.module.module', 'search',
        [[('name', '=', module_name)]]
    )
    
    if not module_ids:
        print(f"  ✗ Module not found: {module_name}\n")
        return None
    
    module_data = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.module.module', 'read',
        [module_ids, [
            'name', 'state', 'shortdesc', 'summary', 'description',
            'author', 'website', 'installed_version', 'latest_version',
            'category_id', 'license', 'dependencies_id'
        ]]
    )[0]
    
    # Get dependencies
    if module_data.get('dependencies_id'):
        deps = models.execute_kw(
            config['db'], uid, config['password'],
            'ir.module.module.dependency', 'read',
            [module_data['dependencies_id'], ['name', 'depend_id']]
        )
        module_data['dependencies'] = [d['name'] for d in deps]
    else:
        module_data['dependencies'] = []
    
    print(f"  ✓ Found: {module_data['shortdesc']} (v{module_data['installed_version']})")
    print(f"  Dependencies: {', '.join(module_data['dependencies']) if module_data['dependencies'] else 'None'}\n")
    
    return module_data

def get_module_data_files(uid, models, config, module_name):
    """Get data files (XML/CSV) for the module"""
    print(f"Fetching data files for: {module_name}")
    
    # Get ir.model.data records for this module
    data_ids = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.model.data', 'search',
        [[('module', '=', module_name)]]
    )
    
    if not data_ids:
        print(f"  ⚠ No data records found\n")
        return []
    
    data_records = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.model.data', 'read',
        [data_ids[:100], ['name', 'model', 'res_id', 'module']]  # Limit to first 100
    )
    
    print(f"  ✓ Found {len(data_records)} data records\n")
    return data_records

def get_module_models(uid, models, config, module_name):
    """Get all models defined by this module"""
    print(f"Fetching models for: {module_name}")
    
    # Get ir.model records
    model_ids = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.model', 'search',
        [[('modules', 'ilike', module_name)]]
    )
    
    if not model_ids:
        print(f"  ⚠ No models found\n")
        return []
    
    model_records = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.model', 'read',
        [model_ids, ['name', 'model', 'info', 'modules']]
    )
    
    print(f"  ✓ Found {len(model_records)} models\n")
    return model_records

def get_module_views(uid, models, config, module_name):
    """Get all views for the module"""
    print(f"Fetching views for: {module_name}")
    
    # Get views via ir.ui.view
    view_ids = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.ui.view', 'search',
        [[('xml_id', 'ilike', f'{module_name}.%')]]
    )
    
    if not view_ids:
        print(f"  ⚠ No views found\n")
        return []
    
    view_records = models.execute_kw(
        config['db'], uid, config['password'],
        'ir.ui.view', 'read',
        [view_ids[:50], ['name', 'type', 'model', 'xml_id']]  # Limit to first 50
    )
    
    print(f"  ✓ Found {len(view_records)} views\n")
    return view_records

def export_module_info(module_name, module_data, data_files, models_list, views):
    """Export all module information to JSON files"""
    output_dir = Path('payroll_export') / module_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Module info
    with open(output_dir / 'module_info.json', 'w') as f:
        json.dump(module_data, f, indent=2)
    
    # Data files
    with open(output_dir / 'data_records.json', 'w') as f:
        json.dump(data_files, f, indent=2)
    
    # Models
    with open(output_dir / 'models.json', 'w') as f:
        json.dump(models_list, f, indent=2)
    
    # Views
    with open(output_dir / 'views.json', 'w') as f:
        json.dump(views, f, indent=2)
    
    print(f"✓ Exported to: {output_dir}\n")

def create_manifest_template(module_data, output_dir):
    """Create __manifest__.py template for v19"""
    manifest_content = f'''# -*- coding: utf-8 -*-
{{
    'name': '{module_data['shortdesc']}',
    'version': '19.0.1.0.0',  # Updated to v19
    'category': '{module_data['category_id'][1] if module_data.get('category_id') else 'Human Resources'}',
    'summary': '{module_data.get('summary', '').replace("'", "\\'")}',
    'description': """
{module_data.get('description', '').replace('"""', "'''")}
    """,
    'author': '{module_data.get('author', 'Your Company')}',
    'website': '{module_data.get('website', 'https://www.yourcompany.com')}',
    'license': '{module_data.get('license', 'LGPL-3')}',
    'depends': {module_data.get('dependencies', [])},
    'data': [
        # TODO: Add your data files here
        # 'security/ir.model.access.csv',
        # 'views/*.xml',
        # 'data/*.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}}
'''
    
    with open(output_dir / '__manifest__.py.template', 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    print(f"✓ Created manifest template: {output_dir / '__manifest__.py.template'}\n")

def main():
    """Main function"""
    print("=" * 80)
    print("PAYROLL MODULE EXPORT FROM OSUSPROPERTIES")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Connect to OSUSPROPERTIES
        uid, models, config = connect_odoo(OSUS_CONFIG)
        
        export_summary = {
            'timestamp': datetime.now().isoformat(),
            'source_instance': 'osusproperties',
            'source_version': 'v17',
            'target_version': 'v19',
            'modules': {}
        }
        
        for module_name in MODULES_TO_EXPORT:
            print("=" * 80)
            print(f"EXPORTING: {module_name}")
            print("=" * 80 + "\n")
            
            # Get module info
            module_data = get_module_info(uid, models, config, module_name)
            if not module_data:
                continue
            
            # Get data files
            data_files = get_module_data_files(uid, models, config, module_name)
            
            # Get models
            models_list = get_module_models(uid, models, config, module_name)
            
            # Get views
            views = get_module_views(uid, models, config, module_name)
            
            # Export to files
            output_dir = Path('payroll_export') / module_name
            export_module_info(module_name, module_data, data_files, models_list, views)
            
            # Create manifest template
            create_manifest_template(module_data, output_dir)
            
            # Add to summary
            export_summary['modules'][module_name] = {
                'version': module_data['installed_version'],
                'dependencies': module_data.get('dependencies', []),
                'data_records': len(data_files),
                'models': len(models_list),
                'views': len(views),
                'export_path': str(output_dir)
            }
        
        # Save export summary
        with open('payroll_export/EXPORT_SUMMARY.json', 'w') as f:
            json.dump(export_summary, f, indent=2)
        
        print("\n" + "=" * 80)
        print("EXPORT COMPLETE")
        print("=" * 80)
        print(f"\nExported {len(export_summary['modules'])} modules")
        print(f"Location: ./payroll_export/")
        print("\nNext steps:")
        print("1. Review exported module information")
        print("2. Download actual module files from server (SSH/SCP)")
        print("3. Use manifest templates to upgrade to v19")
        print("4. Test installation on SGCTECHAI")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}\n")
        raise

if __name__ == '__main__':
    main()
