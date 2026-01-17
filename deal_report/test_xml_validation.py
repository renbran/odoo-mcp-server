#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET

os.chdir(os.path.dirname(__file__))
files = [
    'security/deal_report_security.xml',
    'data/deal_sequence.xml',
    'data/commission_product.xml',
    'views/deal_report_views.xml',
    'views/deal_menu.xml',
    'views/deal_report_search.xml',
    'views/deal_dashboard_views.xml',
    'views/deal_report_analytics.xml',
    'reports/deal_report_templates.xml'
]

print("\n=== XML VALIDATION ===\n")
for f in files:
    try:
        tree = ET.parse(f)
        root = tree.getroot()
        # Check if root is 'odoo'
        if root.tag != 'odoo':
            print(f'{f}: ROOT TAG IS {root.tag}, NOT odoo ❌')
        # Count data elements
        data_count = len(root.findall('data'))
        if data_count != 1:
            print(f'{f}: HAS {data_count} <data> elements (expected 1) ❌')
        else:
            # Count child elements
            if root[0].tag == 'data':
                child_count = len(root[0])
                print(f'{f}: OK ✓ ({child_count} children in <data>)')
    except Exception as e:
        print(f'{f}: ERROR - {str(e)[:100]} ❌')

print("\n=== CHECKING MANIFEST ===\n")
try:
    import ast
    with open('__manifest__.py', 'r') as f:
        manifest_str = f.read()
    manifest = ast.literal_eval(manifest_str.split('{')[1].split('}')[0].replace('{', '{"').replace(':', '":'))
    # Simple parse
    with open('__manifest__.py', 'r') as f:
        content = f.read()
        import re
        data_match = re.search(r"'data':\s*\[(.*?)\]", content, re.DOTALL)
        if data_match:
            data_files = re.findall(r"'([^']+\.xml)'", data_match.group(1))
            print(f"Found {len(data_files)} data files in manifest:")
            for df in data_files:
                print(f"  - {df}")
except Exception as e:
    print(f"Error parsing manifest: {e}")
