#!/usr/bin/env python3
"""
Comprehensive fix for osusproperties Odoo instance issues
Fixes:
1. Users with multiple user type groups
2. Bad ar_001 translation file
3. View warnings (group vs groups, missing alt)
"""

import xmlrpc.client
import sys
import os

# Configuration
URL = 'http://localhost:8070'
DB = 'osusproperties'
USERNAME = 'admin@gmail.com'
PASSWORD = 'admin'

def main():
    print("="*80)
    print("OSUSPROPERTIES ODOO FIX SCRIPT")
    print("="*80)
    
    # Step 1: Fix user type conflicts
    print("\n[1/3] Fixing user type conflicts...")
    fix_user_types()
    
    # Step 2: Fix translation file
    print("\n[2/3] Fixing ar_001 translation file...")
    fix_translation_file()
    
    # Step 3: Fix view warnings
    print("\n[3/3] Fixing view warnings...")
    fix_view_warnings()
    
    print("\n" + "="*80)
    print("ALL FIXES COMPLETED!")
    print("="*80)
    print("\nNext steps:")
    print("1. Restart Odoo: sudo systemctl restart odoo-osusproperties")
    print("2. Monitor logs: sudo tail -f /var/odoo/osusproperties/logs/odoo-server.log")
    print("3. Verify registry loads without errors")

def fix_user_types():
    """Fix users with multiple user type groups"""
    try:
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        
        if not uid:
            print("✗ Authentication failed")
            return False
        
        print(f"✓ Connected to Odoo (UID: {uid})")
        
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Get user type category
        category_id = models.execute_kw(DB, uid, PASSWORD, 'ir.module.category', 'search',
            [[['name', '=', 'User types']]])
        
        if not category_id:
            print("✗ User type category not found")
            return False
        
        print(f"✓ Found user type category (ID: {category_id[0]})")
        
        # Get all user type groups
        user_type_groups = models.execute_kw(DB, uid, PASSWORD, 'res.groups', 'search_read',
            [[['category_id', '=', category_id[0]]]], {'fields': ['id', 'name']})
        
        print(f"✓ Found {len(user_type_groups)} user type groups:")
        for g in user_type_groups:
            print(f"  - {g['name']} (ID: {g['id']})")
        
        user_type_group_ids = [g['id'] for g in user_type_groups]
        
        # Find users with multiple user type groups
        all_users = models.execute_kw(DB, uid, PASSWORD, 'res.users', 'search_read',
            [[]], {'fields': ['id', 'login', 'name', 'groups_id']})
        
        print(f"\n✓ Checking {len(all_users)} users for conflicts...")
        
        conflicted_users = []
        for user in all_users:
            user_type_group_count = sum(1 for gid in user.get('groups_id', []) if gid in user_type_group_ids)
            if user_type_group_count > 1:
                user_groups = [g for g in user_type_groups if g['id'] in user.get('groups_id', [])]
                conflicted_users.append({
                    'id': user['id'],
                    'login': user['login'],
                    'name': user['name'],
                    'groups': user_groups
                })
        
        if not conflicted_users:
            print("✓ No users with conflicting user types found!")
            return True
        
        print(f"\n⚠ Found {len(conflicted_users)} users with conflicts:")
        for user in conflicted_users:
            print(f"\n  User: {user['login']} (ID: {user['id']})")
            print(f"  Groups: {', '.join([g['name'] for g in user['groups']])}")
        
        # Get specific group IDs
        portal_group = models.execute_kw(DB, uid, PASSWORD, 'ir.model.data', 'xmlid_to_res_id', ['base.group_portal'])
        public_group = models.execute_kw(DB, uid, PASSWORD, 'ir.model.data', 'xmlid_to_res_id', ['base.group_public'])
        internal_group = models.execute_kw(DB, uid, PASSWORD, 'ir.model.data', 'xmlid_to_res_id', ['base.group_user'])
        
        print(f"\n✓ Group IDs:")
        print(f"  Portal: {portal_group}")
        print(f"  Public: {public_group}")
        print(f"  Internal: {internal_group}")
        
        # Fix conflicted users
        print(f"\n→ Fixing {len(conflicted_users)} users...")
        fixed_count = 0
        
        for user in conflicted_users:
            user_group_ids = [g['id'] for g in user['groups']]
            groups_to_remove = []
            keep_type = ""
            
            # If user has internal group, remove portal and public
            if internal_group in user_group_ids:
                if portal_group in user_group_ids:
                    groups_to_remove.append(portal_group)
                if public_group in user_group_ids:
                    groups_to_remove.append(public_group)
                keep_type = "Internal User"
            # If user has portal, remove public and internal
            elif portal_group in user_group_ids:
                if public_group in user_group_ids:
                    groups_to_remove.append(public_group)
                if internal_group in user_group_ids:
                    groups_to_remove.append(internal_group)
                keep_type = "Portal"
            
            if groups_to_remove:
                try:
                    models.execute_kw(DB, uid, PASSWORD, 'res.users', 'write',
                        [[user['id']], {'groups_id': [(3, gid) for gid in groups_to_remove]}])
                    print(f"  ✓ Fixed {user['login']} - Kept: {keep_type}, Removed: {len(groups_to_remove)} groups")
                    fixed_count += 1
                except Exception as e:
                    print(f"  ✗ Failed to fix {user['login']}: {e}")
            else:
                print(f"  ⚠ {user['login']} - No groups to remove")
        
        print(f"\n✓ Fixed {fixed_count}/{len(conflicted_users)} users")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing user types: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_translation_file():
    """Fix or remove bad ar_001 translation file"""
    try:
        # Find the problematic translation file
        # Based on error: odoo.tools.translate - couldn't read translation file [lang: ar_001]
        # The file is likely in one of the addons with syntax error at line 92
        
        print("→ Searching for problematic ar_001 translation files...")
        
        # Common locations
        search_paths = [
            '/var/odoo/osusproperties/src/addons',
            '/var/odoo/osusproperties/extra-addons',
        ]
        
        problematic_files = []
        
        for base_path in search_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file == 'ar_001.po' or (file.endswith('.po') and 'ar_001' in root):
                            file_path = os.path.join(root, file)
                            problematic_files.append(file_path)
        
        if problematic_files:
            print(f"✓ Found {len(problematic_files)} ar_001 translation files:")
            for f in problematic_files:
                print(f"  - {f}")
                # Rename to .po.bak to disable
                backup_path = f + '.bak'
                try:
                    os.rename(f, backup_path)
                    print(f"    ✓ Renamed to {backup_path}")
                except Exception as e:
                    print(f"    ✗ Failed to rename: {e}")
        else:
            print("⚠ No ar_001 translation files found in common paths")
            print("  Manual search may be required")
        
        return True
        
    except Exception as e:
        print(f"✗ Error fixing translation file: {e}")
        return False

def fix_view_warnings():
    """Fix view warnings by updating XML files"""
    try:
        print("→ Fixing view attribute warnings...")
        
        # Files with 'group' instead of 'groups'
        files_to_fix = [
            '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/account_line_view/views/invoice_line_view.xml',
            '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/account_line_view/views/bill_line_view.xml',
            '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/account_line_view/views/credit_note_line_view.xml',
            '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/account_line_view/views/refund_line_view.xml',
            '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/account_line_view/views/account_move_line_view.xml',
        ]
        
        fixed_count = 0
        for file_path in files_to_fix:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Replace group=" with groups="
                    if 'group="' in content:
                        new_content = content.replace('group="', 'groups="')
                        with open(file_path, 'w') as f:
                            f.write(new_content)
                        print(f"  ✓ Fixed: {os.path.basename(file_path)}")
                        fixed_count += 1
                    else:
                        print(f"  ○ No changes needed: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"  ✗ Failed to fix {file_path}: {e}")
            else:
                print(f"  ⚠ File not found: {file_path}")
        
        # Fix missing alt attribute in img tag
        img_file = '/var/odoo/osusproperties/extra-addons/odoo17_final.git-6880b7fcd4844/base_account_budget/views/account_budget_views.xml'
        if os.path.exists(img_file):
            try:
                with open(img_file, 'r') as f:
                    content = f.read()
                
                # Add alt attribute to img tags without it
                if '<img' in content and 'alt=' not in content:
                    # Simple replacement - add alt="Budget" to img tags
                    new_content = content.replace('<img ', '<img alt="Budget" ')
                    with open(img_file, 'w') as f:
                        f.write(new_content)
                    print(f"  ✓ Added alt attributes to: {os.path.basename(img_file)}")
                    fixed_count += 1
                else:
                    print(f"  ○ No changes needed: {os.path.basename(img_file)}")
            except Exception as e:
                print(f"  ✗ Failed to fix {img_file}: {e}")
        else:
            print(f"  ⚠ File not found: {img_file}")
        
        print(f"\n✓ Fixed {fixed_count} view files")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing view warnings: {e}")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
