#!/usr/bin/env python3
"""
Fix for Odoo Dashboard Label Errors
====================================
This script fixes the "Incorrect use of <label for=FORM_ELEMENT>" errors
in the osus_sales_invoicing_dashboard module.

The issue: Labels with 'for' attributes don't have matching element IDs,
causing accessibility warnings and style compilation failures.

Solution: Add nolabel="1" to fields that have custom widgets/labels
inside group elements.

Usage:
    1. Copy this script to the server
    2. Run: python3 fix_dashboard_labels.py

Or run via SSH:
    scp fix_dashboard_labels.py root@139.84.163.11:/tmp/
    ssh root@139.84.163.11 "python3 /tmp/fix_dashboard_labels.py"
"""

import re
import os
import shutil
from datetime import datetime

# Configuration
FILE_PATH = "/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/osus_sales_invoicing_dashboard/views/dashboard_views.xml"

# Fields that commonly cause label issues in Odoo forms
FIELDS_TO_FIX = [
    'sales_order_type_ids',
    'agent_partner_id',
    'partner_id',
    'payment_status_filter',
    'invoice_status_filter',
    'salesperson_id',
]


def create_backup(file_path):
    """Create a timestamped backup of the file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path


def add_nolabel_to_fields(content):
    """Add nolabel='1' to fields that don't already have it."""
    modified = content
    changes = []

    for field_name in FIELDS_TO_FIX:
        # Pattern to match field without nolabel attribute
        # Match: <field name="field_name" but NOT if followed by nolabel
        pattern = rf'(<field\s+name=["\']){field_name}(["\'])(?!\s+nolabel)'
        replacement = rf'\g<1>{field_name}\g<2> nolabel="1"'

        if re.search(pattern, modified):
            modified = re.sub(pattern, replacement, modified)
            changes.append(field_name)

    return modified, changes


def fix_orphan_labels(content):
    """Remove or fix labels that have 'for' attributes pointing to non-existent IDs."""
    # Pattern to find labels with 'for' attribute inside form views
    # These are the ones causing "Incorrect use of <label for=FORM_ELEMENT>" errors

    # Option 1: Remove the 'for' attribute from labels (safer)
    # Pattern matches: <label ... for="something_0" ...>
    pattern = r'(<label[^>]*)\s+for=["\'][^"\']*_\d+["\']([^>]*>)'
    modified = re.sub(pattern, r'\1\2', content)

    return modified


def main():
    print("=" * 60)
    print("Odoo Dashboard Label Fix Script")
    print("=" * 60)

    if not os.path.exists(FILE_PATH):
        print(f"ERROR: File not found: {FILE_PATH}")
        print("\nTrying alternative paths...")

        # Try to find the file
        alt_paths = [
            "/var/odoo/osusproperties/custom_addons/osus_sales_invoicing_dashboard/views/dashboard_views.xml",
            "/opt/odoo/custom_addons/osus_sales_invoicing_dashboard/views/dashboard_views.xml",
        ]

        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                print(f"Found at: {alt_path}")
                global FILE_PATH
                FILE_PATH = alt_path
                break
        else:
            print("File not found in any location. Please check the path manually.")
            return False

    print(f"\nTarget file: {FILE_PATH}")

    # Create backup
    backup_path = create_backup(FILE_PATH)

    # Read file
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        original_content = f.read()

    print(f"\nOriginal file size: {len(original_content)} bytes")

    # Apply fixes
    content = original_content

    # Fix 1: Add nolabel to fields
    content, changed_fields = add_nolabel_to_fields(content)
    if changed_fields:
        print(f"\nAdded nolabel='1' to fields: {', '.join(changed_fields)}")
    else:
        print("\nNo fields needed nolabel attribute")

    # Fix 2: Fix orphan labels
    content_before_label_fix = content
    content = fix_orphan_labels(content)
    if content != content_before_label_fix:
        print("Fixed orphan label 'for' attributes")

    # Check if any changes were made
    if content == original_content:
        print("\nNo changes needed - file is already correct")
        return True

    # Write fixed content
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nFixed file size: {len(content)} bytes")
    print(f"\nFile updated successfully!")
    print(f"Backup saved to: {backup_path}")

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Restart Odoo service:")
    print("   systemctl restart odoo-osusproperties")
    print("")
    print("2. Clear browser cache and reload (Ctrl+Shift+R)")
    print("")
    print("3. If issues persist, restore backup:")
    print(f"   cp {backup_path} {FILE_PATH}")
    print("   systemctl restart odoo-osusproperties")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
