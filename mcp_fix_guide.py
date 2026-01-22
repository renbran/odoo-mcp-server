"""
Fix osusproperties user type conflicts using Odoo MCP Server
This script uses the MCP tools to identify and fix users with multiple user types
"""

import json
import subprocess
import sys

def run_mcp_tool(tool_name, args):
    """Run an MCP tool via the Odoo MCP server"""
    print(f"\n→ Running MCP tool: {tool_name}")
    print(f"   Arguments: {json.dumps(args, indent=2)}")
    
    # The MCP server is already running via Claude Desktop
    # We need to build and use it directly
    cmd = ["node", "dist/index.js"]
    
    # For now, we'll output the commands that Claude can execute
    return None

# Step 1: Get user type category
print("="*80)
print("STEP 1: Find user type category")
print("="*80)

search_category = {
    "instance": "osusproperties",
    "model": "ir.module.category",
    "domain": [["name", "=", "User types"]],
    "fields": ["id", "name"]
}

print("\nMCP Tool Call: odoo_search_read")
print(json.dumps(search_category, indent=2))

# Step 2: Get all user type groups
print("\n" + "="*80)
print("STEP 2: Get user type groups (assume category_id = 14)")
print("="*80)

search_groups = {
    "instance": "osusproperties",
    "model": "res.groups",
    "domain": [["category_id", "=", 14]],
    "fields": ["id", "name", "category_id"]
}

print("\nMCP Tool Call: odoo_search_read")
print(json.dumps(search_groups, indent=2))

# Step 3: Get all users with their groups
print("\n" + "="*80)
print("STEP 3: Get all users")
print("="*80)

search_users = {
    "instance": "osusproperties",
    "model": "res.users",
    "domain": [],
    "fields": ["id", "login", "name", "groups_id"],
    "limit": 1000
}

print("\nMCP Tool Call: odoo_search_read")
print(json.dumps(search_users, indent=2))

# Step 4: Get specific group IDs
print("\n" + "="*80)
print("STEP 4: Get specific group XML IDs")
print("="*80)

# We need to search for the XML ID records
xmlid_searches = [
    {
        "instance": "osusproperties",
        "model": "ir.model.data",
        "domain": [["module", "=", "base"], ["name", "=", "group_user"]],
        "fields": ["res_id", "name", "module"]
    },
    {
        "instance": "osusproperties",
        "model": "ir.model.data",
        "domain": [["module", "=", "base"], ["name", "=", "group_portal"]],
        "fields": ["res_id", "name", "module"]
    },
    {
        "instance": "osusproperties",
        "model": "ir.model.data",
        "domain": [["module", "=", "base"], ["name", "=", "group_public"]],
        "fields": ["res_id", "name", "module"]
    }
]

for search in xmlid_searches:
    print(f"\nMCP Tool Call: odoo_search_read")
    print(json.dumps(search, indent=2))

# Step 5: Example of fixing a user (user_id=2, remove portal group_id=13)
print("\n" + "="*80)
print("STEP 5: Example - Fix a conflicted user")
print("="*80)

fix_user_example = {
    "instance": "osusproperties",
    "model": "res.users",
    "ids": [2],  # Example user ID
    "values": {
        "groups_id": [
            [3, 13]  # Remove portal group (ID 13)
        ]
    }
}

print("\nMCP Tool Call: odoo_update")
print(json.dumps(fix_user_example, indent=2))

print("\n" + "="*80)
print("IMPLEMENTATION NOTES")
print("="*80)
print("""
To execute these fixes:

1. Use Claude Desktop with the Odoo MCP server
2. Ask Claude to execute each step above using the odoo_search_read and odoo_update tools
3. For each conflicted user found, run odoo_update with:
   - Remove command: [3, group_id] to unlink a group
   - For users with both internal and portal: remove portal/public
   - For users with portal only: keep portal, remove any internal

Example conversation with Claude:
"Using the osusproperties instance, search for users and identify which ones have 
multiple user type groups, then remove the conflicting groups keeping internal 
users as internal and portal users as portal."

4. After all fixes, restart the Odoo service on the server:
   sudo systemctl restart odoo-osusproperties

5. Monitor the logs to ensure registry loads without errors:
   sudo tail -f /var/odoo/osusproperties/logs/odoo-server.log
""")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("This script outputs the MCP commands needed.")
    print("Execute them via Claude Desktop with Odoo MCP server.")
    print("="*80)
