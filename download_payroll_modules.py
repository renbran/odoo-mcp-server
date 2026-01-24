#!/usr/bin/env python3
"""
Download Odoo Community Payroll Modules from GitHub
For Odoo 17 - UAE Payroll Compliance Project
"""

import os
import subprocess
import shutil
from pathlib import Path

# Module repositories (Odoo Community Edition)
PAYROLL_REPOS = {
    'hr_payroll_community': {
        'repo': 'https://github.com/CybroOdoo/CybroAddons.git',
        'branch': '17.0',
        'module_path': 'hr_payroll_community'
    },
    'hr_payroll_account_community': {
        'repo': 'https://github.com/CybroOdoo/CybroAddons.git',
        'branch': '17.0',
        'module_path': 'hr_payroll_account_community'
    }
}

# Alternative: OCA (Odoo Community Association) repositories
OCA_REPOS = {
    'hr_payroll': {
        'repo': 'https://github.com/OCA/payroll.git',
        'branch': '17.0',
        'modules': ['hr_payroll', 'hr_payroll_account']
    }
}

TARGET_DIR = Path('test_modules')

def clone_and_extract_module(repo_url, branch, module_path, target_name):
    """Clone repository and extract specific module"""
    print(f"\n{'='*80}")
    print(f"Downloading {target_name}")
    print(f"{'='*80}")
    
    temp_dir = Path(f'temp_{target_name}')
    
    try:
        # Clone repository
        print(f"Cloning from {repo_url} (branch: {branch})...")
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', '--branch', branch, repo_url, str(temp_dir)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"✗ Git clone failed: {result.stderr}")
            return False
        
        print(f"✓ Repository cloned successfully")
        
        # Check if module exists
        module_source = temp_dir / module_path
        if not module_source.exists():
            print(f"✗ Module not found at {module_source}")
            print(f"  Checking repository structure...")
            # List available modules
            for item in temp_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    print(f"    - {item.name}")
            return False
        
        # Copy module to test_modules
        TARGET_DIR.mkdir(exist_ok=True)
        target_path = TARGET_DIR / target_name
        
        if target_path.exists():
            print(f"⚠ Module already exists at {target_path}, removing...")
            shutil.rmtree(target_path)
        
        print(f"Copying module to {target_path}...")
        shutil.copytree(module_source, target_path)
        
        print(f"✓ Module {target_name} installed successfully!")
        print(f"  Location: {target_path}")
        
        # Verify __manifest__.py exists
        manifest = target_path / '__manifest__.py'
        if manifest.exists():
            print(f"✓ Module manifest verified")
        else:
            print(f"⚠ Warning: __manifest__.py not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
    
    finally:
        # Cleanup temporary directory
        if temp_dir.exists():
            print(f"Cleaning up temporary files...")
            shutil.rmtree(temp_dir)

def download_all_modules():
    """Download all required payroll modules"""
    print("\n" + "="*80)
    print("ODOO 17 PAYROLL MODULES DOWNLOADER")
    print("="*80)
    
    success_count = 0
    total_count = len(PAYROLL_REPOS)
    
    for module_name, config in PAYROLL_REPOS.items():
        success = clone_and_extract_module(
            config['repo'],
            config['branch'],
            config['module_path'],
            module_name
        )
        if success:
            success_count += 1
    
    print("\n" + "="*80)
    print("DOWNLOAD SUMMARY")
    print("="*80)
    print(f"Successfully downloaded: {success_count}/{total_count} modules")
    
    if success_count == total_count:
        print("\n✓ All modules downloaded successfully!")
        print("\nNext steps:")
        print("1. Verify modules in test_modules/ directory")
        print("2. Copy to Docker container addon path")
        print("3. Restart Odoo container")
        print("4. Install via Apps menu")
    else:
        print("\n⚠ Some modules failed to download")
        print("\nAlternative: Download manually from:")
        print("- https://apps.odoo.com/")
        print("- https://github.com/OCA/payroll")
        print("- Or copy from OSUSPROPERTIES server")

def main():
    """Main execution"""
    # Check if git is available
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Error: Git is not installed or not in PATH")
        print("  Please install Git from: https://git-scm.com/downloads")
        return
    
    download_all_modules()

if __name__ == '__main__':
    main()
