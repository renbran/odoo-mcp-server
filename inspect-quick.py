#!/usr/bin/env python3
"""
Quick Commission_AX Module Inspector - Direct DB Access
Faster alternative using psql instead of Odoo shell
"""

import subprocess
import sys
import json

# Configuration
DB_NAME = "commission_ax"
DB_USER = "odoo"

def run_psql(query):
    """Run PostgreSQL query directly"""
    cmd = [
        "sudo", "-u", "postgres",
        "psql", DB_NAME,
        "-t",  # Tuples only
        "-A",  # Unaligned output
        "-F", "|",  # Field separator
        "-c", query
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: {result.stderr}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def list_modules(state=None):
    """List modules from database"""
    print("\n" + "="*70)
    print("COMMISSION_AX MODULE INSPECTOR - DIRECT DB ACCESS")
    print("="*70 + "\n")
    
    where_clause = f"WHERE state = '{state}'" if state else ""
    
    query = f"""
        SELECT name, state, COALESCE(summary::text, '') as summary, 
               latest_version, author
        FROM ir_module_module
        {where_clause}
        ORDER BY state, name
        LIMIT 100;
    """
    
    print(f"[INFO] Querying modules{' with state=' + state if state else ''}...\n")
    output = run_psql(query)
    
    if output.startswith("ERROR"):
        print(output)
        return
    
    lines = output.split('\n')
    print(f"[INFO] Found {len(lines)} modules:\n")
    print(f"{'NAME':<35} {'STATE':<15} {'VERSION':<10} {'SUMMARY':<40}")
    print("-" * 105)
    
    for line in lines:
        if not line.strip():
            continue
        parts = line.split('|')
        if len(parts) >= 4:
            name = parts[0][:34]
            state = parts[1][:14]
            summary = parts[2][:39] if parts[2] else "No description"
            version = parts[3][:9] if parts[3] else "-"
            print(f"{name:<35} {state:<15} {version:<10} {summary:<40}")

def show_module_info(module_name):
    """Show detailed module information"""
    print("\n" + "="*70)
    print(f"MODULE INFO: {module_name}")
    print("="*70 + "\n")
    
    query = f"""
        SELECT 
            name, state, COALESCE(summary::text, '') as summary,
            COALESCE(description::text, '') as description,
            latest_version, published_version, author,
            website, license, category_id, application, maintainer
        FROM ir_module_module
        WHERE name = '{module_name}';
    """
    
    output = run_psql(query)
    
    if output.startswith("ERROR"):
        print(output)
        return
    
    if not output.strip():
        print(f"❌ Module '{module_name}' not found!")
        return
    
    parts = output.split('|')
    if len(parts) >= 10:
        print(f"Name:             {parts[0]}")
        print(f"State:            {parts[1]}")
        print(f"Summary:          {parts[2] or 'N/A'}")
        print(f"Latest Version:   {parts[4] or 'N/A'}")
        print(f"Published:        {parts[5] or 'N/A'}")
        print(f"Author:           {parts[6] or 'Unknown'}")
        print(f"Website:          {parts[7] or 'N/A'}")
        print(f"License:          {parts[8] or 'N/A'}")
        print(f"Category:         {parts[9] or 'Uncategorized'}")
        print(f"Application:      {parts[10] or 'false'}")
        print(f"Maintainer:       {parts[11] or 'N/A'}")
        
        if parts[3]:
            print(f"\nDescription:")
            desc = parts[3].replace('{', '').replace('}', '').replace('"en_US":', '').strip()
            print(desc[:500])
        
        # Get dependencies
        deps_query = f"""
            SELECT d.name
            FROM ir_module_module_dependency dep
            JOIN ir_module_module d ON d.id = dep.depend_id
            JOIN ir_module_module m ON m.id = dep.module_id
            WHERE m.name = '{module_name}';
        """
        deps = run_psql(deps_query)
        if deps and not deps.startswith("ERROR"):
            dep_list = [d for d in deps.split('\n') if d.strip()]
            if dep_list:
                print(f"\nDependencies ({len(dep_list)}):")
                for dep in dep_list[:15]:
                    print(f"  • {dep}")
                if len(dep_list) > 15:
                    print(f"  ... and {len(dep_list) - 15} more")
            else:
                print(f"\nDependencies: None")
        else:
            print(f"\nDependencies: Unable to fetch")

def search_modules(keyword):
    """Search modules by keyword"""
    print("\n" + "="*70)
    print(f"SEARCHING FOR: {keyword}")
    print("="*70 + "\n")
    
    query = f"""
        SELECT name, state, COALESCE(summary::text, '') as summary
        FROM ir_module_module
        WHERE name ILIKE '%{keyword}%' 
           OR COALESCE(summary::text, '') ILIKE '%{keyword}%'
        ORDER BY state, name
        LIMIT 50;
    """
    
    output = run_psql(query)
    
    if output.startswith("ERROR"):
        print(output)
        return
    
    lines = output.split('\n')
    print(f"[INFO] Found {len([l for l in lines if l.strip()])} matches:\n")
    print(f"{'NAME':<40} {'STATE':<15} {'SUMMARY':<30}")
    print("-" * 85)
    
    for line in lines:
        if not line.strip():
            continue
        parts = line.split('|')
        if len(parts) >= 3:
            name = parts[0][:39]
            state = parts[1][:14]
            summary = parts[2][:29] if parts[2] else "No description"
            print(f"{name:<40} {state:<15} {summary:<30}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 inspect-quick.py list [state]")
        print("  python3 inspect-quick.py info <module_name>")
        print("  python3 inspect-quick.py search <keyword>")
        print("\nExamples:")
        print("  python3 inspect-quick.py list")
        print("  python3 inspect-quick.py list installed")
        print("  python3 inspect-quick.py info commission_ax")
        print("  python3 inspect-quick.py search commission")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        state = sys.argv[2] if len(sys.argv) > 2 else None
        list_modules(state)
    elif command == "info":
        if len(sys.argv) < 3:
            print("❌ Please specify module name")
            return
        show_module_info(sys.argv[2])
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Please specify search keyword")
            return
        search_modules(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command}")
        print("Use: list, info, or search")

if __name__ == "__main__":
    main()
