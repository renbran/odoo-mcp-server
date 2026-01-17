#!/usr/bin/env python3
"""Fix the commission_ax report template - remove invalid unit_id reference"""

import sys
import re

template_file = '/var/odoo/scholarixv2/extra-addons/odooapps.git-68ee71eda34bc/commission_ax/reports/commission_report_template_enhanced.xml'

try:
    with open(template_file, 'r') as f:
        content = f.read()
    
    # The pattern to remove - looking for the unit_id conditional block
    # This is a multi-line block that needs to be removed
    pattern = r'\s+<t t-if="o\.unit_id">\s+\| Unit: <strong style="color: #8b1538;"><t t-esc="o\.unit_id\.name"/></strong>\s+</t>'
    
    # Replace with empty string
    new_content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    with open(template_file, 'w') as f:
        f.write(new_content)
    
    print('✅ Fixed template - removed unit_id reference from commission_payout_report_template_final')
    sys.exit(0)
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
