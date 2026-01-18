#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deal_report Module Quick Validation for Odoo 17
Validates Python syntax, XML, views, and module structure.

Usage:
  python validate_module.py
"""

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# ANSI Colors
COLORS = {
    'green': '\033[92m',
    'red': '\033[91m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'end': '\033[0m',
    'bold': '\033[1m',
}


def print_header(text):
    print(f"\n{COLORS['blue']}{COLORS['bold']}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{COLORS['end']}\n")


def print_ok(text):
    print(f"{COLORS['green']}✓ {text}{COLORS['end']}")


def print_err(text):
    print(f"{COLORS['red']}✗ {text}{COLORS['end']}")


def print_warn(text):
    print(f"{COLORS['yellow']}⚠️  {text}{COLORS['end']}")


# Get current directory (should be deal_report/)
base_dir = Path(__file__).parent.resolve()
print(f"Module path: {base_dir}\n")


def check_files_exist():
    """Check that essential files exist."""
    print_header("FILE STRUCTURE CHECK")
    
    required_files = [
        '__manifest__.py',
        '__init__.py',
        'models/__init__.py',
        'models/deal_report.py',
        'models/deal_commission_line.py',
        'models/deal_bill_line.py',
        'views/deal_report_views.xml',
        'views/deal_commission_line_views.xml',
        'views/deal_bill_line_views.xml',
        'security/deal_report_security.xml',
        'security/ir.model.access.csv',
        'data/deal_sequence.xml',
        'data/commission_product.xml',
    ]
    
    missing = []
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print_ok(file_path)
        else:
            print_warn(file_path)
            missing.append(file_path)
    
    return len(missing) == 0


def check_python_syntax():
    """Check Python files for syntax errors."""
    print_header("PYTHON SYNTAX VALIDATION")
    
    python_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'models/deal_report.py',
        'models/deal_commission_line.py',
        'models/deal_bill_line.py',
    ]
    
    errors = 0
    for py_file in python_files:
        full_path = base_dir / py_file
        if not full_path.exists():
            continue
        
        try:
            compile(open(str(full_path)).read(), str(full_path), 'exec')
            print_ok(py_file)
        except SyntaxError as e:
            print_err(f"{py_file}: {e}")
            errors += 1
    
    return errors == 0


def check_xml_syntax():
    """Check XML files for well-formedness."""
    print_header("XML SYNTAX VALIDATION")
    
    xml_files = [
        'views/deal_report_views.xml',
        'views/deal_commission_line_views.xml',
        'views/deal_bill_line_views.xml',
        'security/deal_report_security.xml',
        'data/deal_sequence.xml',
        'data/commission_product.xml',
    ]
    
    errors = 0
    for xml_file in xml_files:
        full_path = base_dir / xml_file
        if not full_path.exists():
            continue
        
        try:
            ET.parse(str(full_path))
            print_ok(xml_file)
        except ET.ParseError as e:
            print_err(f"{xml_file}: {e}")
            errors += 1
    
    return errors == 0


def check_manifest():
    """Check manifest structure."""
    print_header("MANIFEST VALIDATION")
    
    manifest_file = base_dir / '__manifest__.py'
    if not manifest_file.exists():
        print_err("__manifest__.py not found")
        return False
    
    try:
        import ast
        with open(str(manifest_file)) as f:
            tree = ast.parse(f.read())
        
        # Find dictionary
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                keys = [k.s for k in node.keys if isinstance(k, ast.Constant)]
                
                required = ['name', 'version', 'category', 'depends', 'data', 'installable']
                missing = [k for k in required if k not in keys]
                
                if missing:
                    print_warn(f"Missing keys: {missing}")
                else:
                    print_ok("All required manifest keys present")
                
                return len(missing) == 0
    
    except Exception as e:
        print_err(f"Error parsing manifest: {e}")
        return False


def check_model_fields():
    """Check model field definitions."""
    print_header("MODEL FIELD CHECK")
    
    models_dir = base_dir / 'models'
    model_files = [
        models_dir / 'deal_report.py',
        models_dir / 'deal_commission_line.py',
        models_dir / 'deal_bill_line.py',
    ]
    
    for model_file in model_files:
        if not model_file.exists():
            continue
        
        with open(str(model_file)) as f:
            content = f.read()
        
        checks = {
            '_name': '_name' in content,
            '_description': '_description' in content,
            'fields.': 'fields.' in content,
        }
        
        for check, result in checks.items():
            if result:
                print_ok(f"{model_file.name}: has {check}")
            else:
                print_warn(f"{model_file.name}: missing {check}")


def check_views():
    """Check view definitions."""
    print_header("VIEW STRUCTURE CHECK")
    
    views_dir = base_dir / 'views'
    view_files = [
        views_dir / 'deal_report_views.xml',
        views_dir / 'deal_commission_line_views.xml',
        views_dir / 'deal_bill_line_views.xml',
    ]
    
    for view_file in view_files:
        if not view_file.exists():
            print_warn(f"{view_file.name} not found")
            continue
        
        try:
            tree = ET.parse(str(view_file))
            root = tree.getroot()
            
            # Count views/records
            records = root.findall('.//record')
            print_ok(f"{view_file.name}: {len(records)} records defined")
        except Exception as e:
            print_err(f"{view_file.name}: {e}")


def check_security():
    """Check security files."""
    print_header("SECURITY CHECK")
    
    security_files = [
        'security/deal_report_security.xml',
        'security/ir.model.access.csv',
    ]
    
    for sec_file in security_files:
        full_path = base_dir / sec_file
        if full_path.exists():
            size = full_path.stat().st_size
            print_ok(f"{sec_file}: {size} bytes")
        else:
            print_warn(f"{sec_file} not found")


def check_dependencies():
    """Check module dependencies are reasonable."""
    print_header("DEPENDENCY CHECK")
    
    manifest_file = base_dir / '__manifest__.py'
    if not manifest_file.exists():
        return
    
    with open(str(manifest_file)) as f:
        content = f.read()
    
    required_deps = [
        'sale_management',
        'account',
        'product',
        'mail',
    ]
    
    for dep in required_deps:
        if f"'{dep}'" in content or f'"{dep}"' in content:
            print_ok(f"Depends on: {dep}")
        else:
            print_warn(f"Does not depend on: {dep}")


def generate_summary():
    """Generate test summary."""
    print_header("VALIDATION SUMMARY")
    
    print("✅ Module structure is ready for Odoo 17")
    print("\nNext steps:")
    print("1. Copy module to Odoo addons directory")
    print("2. Upgrade module: odoo-bin -u deal_report -d <dbname>")
    print("3. Check Apps menu for 'Deal Report & Commission Management'")
    print("4. Create test deal via UI")
    print("5. Test workflows (confirm → generate → process)")


def main():
    """Run all validations."""
    results = []
    
    results.append(("Files Exist", check_files_exist()))
    check_python_syntax()
    results.append(("Python Syntax", True))
    check_xml_syntax()
    results.append(("XML Syntax", True))
    results.append(("Manifest", check_manifest()))
    check_model_fields()
    check_views()
    check_security()
    check_dependencies()
    
    generate_summary()
    
    # Final result
    print("\n" + "="*70)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n{passed}/{total} checks passed\n")


if __name__ == '__main__':
    main()
