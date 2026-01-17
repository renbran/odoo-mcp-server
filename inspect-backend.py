#!/usr/bin/env python3
"""
Commission_AX Module Inspector & Installer
Direct Odoo backend access for module management
Uses Odoo shell for safe, server-side operations
"""

import subprocess
import sys
import json
from pathlib import Path

# Configuration
ODOO_ROOT = Path("/var/odoo/scholarixv2")
ODOO_VENV = ODOO_ROOT / "venv"
ODOO_BIN = ODOO_ROOT / "src" / "odoo-bin"
ODOO_CONF = ODOO_ROOT / "odoo.conf"
PYTHON = ODOO_VENV / "bin" / "python3"

def run_odoo_command(python_code: str) -> str:
    """Execute Python code directly in Odoo environment using odoo shell"""
    cmd = [
        "sudo", "-u", "odoo",
        str(PYTHON),
        str(ODOO_BIN),
        "shell",
        "-c", str(ODOO_CONF),
        "-d", "commission_ax",
        "--no-http"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            input=python_code,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Return stdout and stderr for debugging
        output = result.stdout
        if result.stderr and 'ERROR' in result.stderr.upper():
            output += f"\nSTDERR: {result.stderr}"
            
        return output
    except subprocess.TimeoutExpired:
        return "ERROR: Command timeout after 120 seconds"
    except Exception as e:
        return f"ERROR: {str(e)}"

def list_modules(state=None):
    """List modules by state"""
    print("\n[INFO] Fetching modules from commission_ax...\n")
    
    filter_code = f"[('state', '=', '{state}')]" if state else "[]"
    
    code = f"""
import json
modules = env['ir.module.module'].search_read({filter_code}, fields=['name', 'state', 'installed_version', 'latest_version', 'description', 'category_id', 'dependencies_id', 'installable'])
for m in modules:
    m['category'] = m.get('category_id', [0, 'Uncategorized'])[1] if m.get('category_id') else 'Uncategorized'
    m['deps'] = len(m.get('dependencies_id', []))
print(json.dumps(modules, indent=2))
"""
    
    output = run_odoo_command(code)
    try:
        modules = json.loads(output.strip())
        print(f"[INFO] Found {len(modules)} modules:\n")
        for m in modules:
            status = '[OK]' if m['state'] == 'installed' else '[INFO]' if m['state'] == 'uninstalled' else '[ERROR]'
            version = m.get('installed_version') or m.get('latest_version', 'unknown')
            print(f"{status} {m['name']:30} v{version:10} [{m['state']:12}]")
            if m.get('description'):
                print(f"    {m['description'][:60]}")
            if m.get('deps', 0) > 0:
                print(f"    Dependencies: {m['deps']}")
            print()
    except:
        print(output)

def show_module_info(module_name: str):
    """Show detailed module information"""
    print(f"\n[INFO] Getting details for: {module_name}\n")
    
    code = f"""
import json
modules = env['ir.module.module'].search_read([('name', '=', '{module_name}')], limit=1)
if not modules:
    print(json.dumps({{'error': 'Module not found'}}))
else:
    m = modules[0]
    result = {{
        'name': m['name'],
        'display_name': m.get('shortdesc', ''),
        'state': m['state'],
        'version': m.get('installed_version') or m.get('latest_version'),
        'author': m.get('author', 'Unknown'),
        'category': m.get('category_id', [0, 'Uncategorized'])[1],
        'installable': m.get('installable', False),
        'auto_install': m.get('auto_install', False),
        'description': m.get('description', ''),
        'dependencies': [d[1] for d in m.get('dependencies_id', [])]
    }}
    print(json.dumps(result, indent=2))
"""
    
    output = run_odoo_command(code)
    try:
        info = json.loads(output.strip())
        if 'error' in info:
            print(f"[ERROR] {info['error']}")
            return
        print(f"[INFO] Module: {info['display_name']}")
        print(f"   Name: {info['name']}")
        print(f"   State: {info['state']}")
        print(f"   Version: {info['version']}")
        print(f"   Author: {info['author']}")
        print(f"   Category: {info['category']}")
        print(f"   Installable: {info['installable']}")
        print(f"   Auto Install: {info['auto_install']}")
        if info['dependencies']:
            print(f"   Dependencies: {', '.join(info['dependencies'])}")
        if info['description']:
            print(f"\n   Description:\n   {info['description']}")
    except Exception as e:
        print(f"[ERROR] {e}\n{output}")

def install_module(module_name: str):
    """Install a module safely"""
    print(f"\n[INFO] Installing: {module_name}...\n")
    
    code = f"""
try:
    module = env['ir.module.module'].search([('name', '=', '{module_name}')], limit=1)
    if not module:
        print("[ERROR] Module not found")
    elif module.state == 'installed':
        print("[INFO] Already installed")
    elif not module.installable:
        print("[ERROR] Module is not installable")
    else:
        print("[WAIT] Installing...")
        module.button_install()
        env.cr.commit()
        print("[OK] Installation complete")
except Exception as e:
    print(f"[ERROR] {{str(e)}}")
"""
    
    output = run_odoo_command(code)
    print(output)

def main():
    """CLI interface"""
    print("\n" + "="*70)
    print("COMMISSION_AX BACKEND MODULE INSPECTOR")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 inspect-backend.py list [state]")
        print("  python3 inspect-backend.py info <module_name>")
        print("  python3 inspect-backend.py install <module_name>")
        print("\nExamples:")
        print("  python3 inspect-backend.py list")
        print("  python3 inspect-backend.py list uninstalled")
        print("  python3 inspect-backend.py info account")
        print("  python3 inspect-backend.py install account_reports\n")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        state = sys.argv[2] if len(sys.argv) > 2 else None
        list_modules(state)
    elif command == "info":
        if len(sys.argv) < 3:
            print("[ERROR] Module name required")
            return
        show_module_info(sys.argv[2])
    elif command == "install":
        if len(sys.argv) < 3:
            print("[ERROR] Module name required")
            return
        install_module(sys.argv[2])
    else:
        print(f"[ERROR] Unknown command: {command}")

if __name__ == "__main__":
    main()

