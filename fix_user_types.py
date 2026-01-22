#!/usr/bin/env python3
"""
Fix Odoo users with multiple user types
This script identifies and fixes users who have more than one user type group
(e.g., both portal and internal user groups)
"""

import json
import subprocess
import sys

def odoo_execute(instance, model, method, args=None, kwargs=None):
    """Execute Odoo method via MCP server"""
    tool_args = {
        "instance": instance,
        "model": model,
        "method": method
    }
    if args:
        tool_args["args"] = args
    if kwargs:
        tool_args["kwargs"] = kwargs
    
    # Call via node and the MCP server
    cmd = [
        "node",
        "dist/index.js"
    ]
    
    # For now, let's use a simpler approach with direct XML-RPC
    return None

def search_read(instance, model, domain, fields):
    """Search and read records"""
    tool_args = {
        "instance": instance,
        "model": model,
        "domain": domain,
        "fields": fields
    }
    return tool_args

# Step 1: Find the user type category
print("Step 1: Finding user type groups...")

# User type groups in Odoo 17:
# - base.group_user (Internal User)
# - base.group_portal (Portal)
# - base.group_public (Public)

# Step 2: Find all users
print("\nStep 2: Searching for all users...")

users_query = {
    "instance": "osusproperties",
    "model": "res.users",
    "domain": [["active", "in", [True, False]]],
    "fields": ["id", "login", "name", "groups_id"]
}

print(f"\nQuery to find users:")
print(json.dumps(users_query, indent=2))

# Step 3: For each user, check if they have multiple user type groups
print("\n\nTo fix this issue, we need to:")
print("1. Connect to Odoo and get all users")
print("2. For each user, check their user type groups")
print("3. Remove conflicting groups")

print("\n" + "="*80)
print("SOLUTION: Run these commands via Odoo shell")
print("="*80)

shell_commands = """
# Connect to Odoo shell
sudo -u odoo /var/odoo/osusproperties/venv/bin/python /var/odoo/osusproperties/src/odoo-bin shell -d osusproperties

# Then run these commands in the Odoo shell:

# 1. Get the user type category
env.cr.execute(\"\"\"
    SELECT id FROM res_groups 
    WHERE category_id = (SELECT id FROM ir_module_category WHERE name = 'User types')
\"\")
user_type_group_ids = [r[0] for r in env.cr.fetchall()]
print(f"User type groups: {user_type_group_ids}")

# 2. Find users with multiple user type groups
env.cr.execute(\"\"\"
    SELECT user_id, COUNT(DISTINCT group_id) as group_count
    FROM res_groups_users_rel
    WHERE group_id IN %s
    GROUP BY user_id
    HAVING COUNT(DISTINCT group_id) > 1
\"\"\", (tuple(user_type_group_ids),))
conflicted_users = env.cr.fetchall()
print(f"Users with multiple types: {conflicted_users}")

# 3. Fix each conflicted user
for user_id, count in conflicted_users:
    user = env['res.users'].browse(user_id)
    print(f"\\nFixing user: {user.login} (ID: {user_id})")
    
    # Get all user type groups for this user
    user_groups = user.groups_id.filtered(lambda g: g.id in user_type_group_ids)
    print(f"  Current user type groups: {user_groups.mapped('name')}")
    
    # Keep internal user if present, otherwise keep the first one
    internal = env.ref('base.group_user', raise_if_not_found=False)
    portal = env.ref('base.group_portal', raise_if_not_found=False)
    public = env.ref('base.group_public', raise_if_not_found=False)
    
    groups_to_remove = []
    
    if internal and internal in user_groups:
        # Keep internal, remove portal and public
        if portal and portal in user_groups:
            groups_to_remove.append(portal.id)
        if public and public in user_groups:
            groups_to_remove.append(public.id)
    elif portal and portal in user_groups:
        # Keep portal, remove public and internal
        if public and public in user_groups:
            groups_to_remove.append(public.id)
        if internal and internal in user_groups:
            groups_to_remove.append(internal.id)
    
    if groups_to_remove:
        print(f"  Removing groups: {groups_to_remove}")
        user.write({'groups_id': [(3, gid) for gid in groups_to_remove]})
        env.cr.commit()
        print(f"  ✓ Fixed user {user.login}")

print("\\n✓ All users fixed!")
"""

print(shell_commands)

print("\n" + "="*80)
print("ALTERNATIVE: Quick SQL fix (use with caution)")
print("="*80)

sql_fix = """
# Connect to PostgreSQL
sudo -u postgres psql osusproperties

# First, identify the problem
SELECT u.login, u.id as user_id, COUNT(DISTINCT r.group_id) as type_count
FROM res_users u
JOIN res_groups_users_rel r ON u.id = r.user_id
JOIN res_groups g ON r.group_id = g.id
JOIN ir_module_category c ON g.category_id = c.id
WHERE c.name = 'User types'
GROUP BY u.id, u.login
HAVING COUNT(DISTINCT r.group_id) > 1;

# Get group IDs
SELECT g.id, g.name 
FROM res_groups g
JOIN ir_module_category c ON g.category_id = c.id
WHERE c.name = 'User types';

# Remove portal group from internal users (adjust IDs as needed)
-- DELETE FROM res_groups_users_rel 
-- WHERE user_id IN (SELECT user_id FROM ...) 
-- AND group_id = (SELECT id FROM res_groups WHERE name = 'Portal');
"""

print(sql_fix)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("This script provides the commands to fix user type conflicts.")
    print("Choose one of the methods above and execute it on the server.")
    print("="*80)
