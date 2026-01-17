#!/usr/bin/env python3
"""
Commission_AX Module Installer
Installs commission_ax and all dependencies via Odoo shell
"""

import subprocess
import sys
from pathlib import Path

# Configuration
ODOO_ROOT = Path("/var/odoo/scholarixv2")
ODOO_VENV = ODOO_ROOT / "venv"
ODOO_BIN = ODOO_ROOT / "src" / "odoo-bin"
ODOO_CONF = ODOO_ROOT / "odoo.conf"
PYTHON = ODOO_VENV / "bin" / "python3"

# Modules to install in order (dependencies first)
MODULES = [
    ("account", "Accounting - Required for commission calculations"),
    ("sale", "Sales - Required for sales commissions"),
    ("purchase", "Purchasing - Required for purchase commissions"),
    ("commission_ax", "Commission AX - Main commission management module")
]

def run_odoo_shell(python_code):
    """Execute Python code in Odoo shell"""
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
            timeout=300  # 5 minutes per module
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "ERROR: Timeout after 5 minutes", 1
    except Exception as e:
        return "", f"ERROR: {str(e)}", 1

def check_module_state(module_name):
    """Check if module is already installed"""
    code = f"""
import json
module = env['ir.module.module'].search([('name', '=', '{module_name}')], limit=1)
if module:
    print(json.dumps({{'name': module.name, 'state': module.state}}))
else:
    print(json.dumps({{'error': 'Module not found'}}))
"""
    stdout, stderr, code = run_odoo_shell(code)
    try:
        import json
        return json.loads(stdout.strip().split('\n')[-1])
    except:
        return {'error': 'Failed to parse'}

def install_module(module_name):
    """Install a single module"""
    code = f"""
import json
try:
    module = env['ir.module.module'].search([('name', '=', '{module_name}')], limit=1)
    if not module:
        print(json.dumps({{'error': 'Module not found'}}))
    elif module.state == 'installed':
        print(json.dumps({{'status': 'already_installed', 'name': '{module_name}'}}))
    else:
        module.button_immediate_install()
        env.cr.commit()
        print(json.dumps({{'status': 'installed', 'name': '{module_name}'}}))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
    return run_odoo_shell(code)

def main():
    print("\n" + "="*70)
    print("COMMISSION_AX MODULE INSTALLER")
    print("="*70 + "\n")
    
    print("This script will install the following modules in order:")
    for i, (module, desc) in enumerate(MODULES, 1):
        print(f"  {i}. {module:<15} - {desc}")
    
    print("\n" + "="*70)
    print("CHECKING CURRENT STATE")
    print("="*70 + "\n")
    
    # Check current state of all modules
    states = {}
    for module, desc in MODULES:
        print(f"Checking {module}...", end=" ")
        sys.stdout.flush()
        state = check_module_state(module)
        states[module] = state.get('state', 'unknown')
        
        if states[module] == 'installed':
            print(f"✅ Already installed")
        elif states[module] == 'uninstalled':
            print(f"❌ Not installed")
        else:
            print(f"⚠️  State: {states[module]}")
    
    # Determine what needs to be installed
    to_install = [m for m, d in MODULES if states.get(m) != 'installed']
    
    if not to_install:
        print("\n✅ All modules already installed!")
        return
    
    print("\n" + "="*70)
    print("INSTALLATION PLAN")
    print("="*70 + "\n")
    
    print(f"Modules to install: {len(to_install)}")
    for module in to_install:
        desc = next(d for m, d in MODULES if m == module)
        print(f"  • {module} - {desc}")
    
    print("\n⚠️  WARNING: This will modify the database!")
    print("    Installation may take 5-15 minutes depending on module size.")
    
    response = input("\nProceed with installation? (yes/no): ")
    if response.lower() != 'yes':
        print("\n❌ Installation cancelled")
        return
    
    print("\n" + "="*70)
    print("INSTALLING MODULES")
    print("="*70 + "\n")
    
    installed_count = 0
    failed_modules = []
    
    for module, desc in MODULES:
        if states.get(module) == 'installed':
            print(f"⏭️  Skipping {module} (already installed)")
            continue
        
        print(f"\n📦 Installing {module}...")
        print(f"   {desc}")
        print(f"   This may take several minutes...\n")
        
        stdout, stderr, returncode = install_module(module)
        
        if returncode == 0:
            try:
                import json
                result = json.loads(stdout.strip().split('\n')[-1])
                if 'error' in result:
                    print(f"❌ Failed: {result['error']}")
                    failed_modules.append(module)
                else:
                    print(f"✅ {module} installed successfully!")
                    installed_count += 1
            except:
                print(f"⚠️  Installation completed but couldn't parse result")
                print(f"   Check module state manually")
        else:
            print(f"❌ Failed to install {module}")
            print(f"   Error: {stderr[:200]}")
            failed_modules.append(module)
            
            # Ask if should continue
            if module != MODULES[-1][0]:
                cont = input("\nContinue with remaining modules? (yes/no): ")
                if cont.lower() != 'yes':
                    print("\n❌ Installation stopped")
                    break
    
    print("\n" + "="*70)
    print("INSTALLATION SUMMARY")
    print("="*70 + "\n")
    
    print(f"✅ Successfully installed: {installed_count} module(s)")
    if failed_modules:
        print(f"❌ Failed: {len(failed_modules)} module(s)")
        for m in failed_modules:
            print(f"   • {m}")
    
    if installed_count > 0:
        print("\n📝 Next Steps:")
        print("  1. Verify installations in Odoo web interface")
        print("  2. Configure module settings as needed")
        print("  3. Test commission workflow")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
