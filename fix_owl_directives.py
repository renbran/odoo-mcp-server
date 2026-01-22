#!/usr/bin/env python3
"""Fix Odoo view XML - Remove forbidden Owl directives"""

import re
import sys

file_path = "/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard/views/dashboard_views.xml"

try:
    # Read the file
    with open(file_path, "r") as f:
        content = f.read()
    
    # Remove t-on-click attributes (forbidden Owl directives)
    original_length = len(content)
    content = re.sub(r' t-on-click="[^"]*"', "", content)
    
    # Write back
    with open(file_path, "w") as f:
        f.write(content)
    
    removed = original_length - len(content)
    print(f"✅ Fixed dashboard_views.xml")
    print(f"📝 Removed {removed} characters")
    print(f"✨ Forbidden Owl directives (t-on-click) removed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
