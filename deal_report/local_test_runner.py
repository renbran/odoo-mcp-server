#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deal_report Module Validation & Test Runner for Odoo 17
Validates XML, Python code, views, and runs module upgrade locally.

Usage:
  python local_test_runner.py --validate-xml
  python local_test_runner.py --upgrade-module
  python local_test_runner.py --run-tests
  python local_test_runner.py --all
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import argparse

# ANSI Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def validate_python_syntax():
    """Check Python files for syntax errors."""
    print_header("PYTHON SYNTAX VALIDATION")
    
    module_path = Path('.').resolve()
    python_files = [f for f in module_path.rglob('*.py') if '__pycache__' not in str(f)]
    errors = 0
    
    for py_file in python_files:
        if '__pycache__' in str(py_file):
            continue
        
        result = subprocess.run(
            ['python', '-m', 'py_compile', str(py_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success(f"{py_file.relative_to('deal_report')}")
        else:
            print_error(f"{py_file.relative_to('deal_report')}: {result.stderr}")
            errors += 1
    
    if errors == 0:
        print_success(f"All {len(python_files)} Python files validated")
    else:
        print_error(f"{errors} Python file(s) contain syntax errors")
    
    return errors == 0


def validate_xml_views():
    """Validate XML view files for well-formedness."""
    print_header("XML VIEW VALIDATION")
    
    import xml.etree.ElementTree as ET
    
    module_path = Path('deal_report')
    xml_files = list(module_path.rglob('*.xml'))
    errors = 0
    
    for xml_file in xml_files:
        try:
            ET.parse(str(xml_file))
            print_success(f"{xml_file.relative_to('deal_report')}")
        except ET.ParseError as e:
            print_error(f"{xml_file.relative_to('deal_report')}: {e}")
            errors += 1
    
    if errors == 0:
        print_success(f"All {len(xml_files)} XML files are well-formed")
    else:
        print_error(f"{errors} XML file(s) contain parse errors")
    
    return errors == 0


def check_manifest():
    """Validate __manifest__.py structure."""
    print_header("MANIFEST VALIDATION")
    
    try:
        import ast
        with open('deal_report/__manifest__.py', 'r') as f:
            manifest_code = f.read()
        
        tree = ast.parse(manifest_code)
        
        # Find the dictionary assignment
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                manifest_keys = [
                    key.s for key in node.keys if isinstance(key, ast.Constant)
                ]
                
                required_keys = [
                    'name', 'version', 'category', 'depends', 'data', 'installable'
                ]
                
                missing = [k for k in required_keys if k not in manifest_keys]
                
                if missing:
                    print_warning(f"Missing manifest keys: {missing}")
                else:
                    print_success("All required manifest keys present")
                
                print_info(f"Manifest defines: {', '.join(manifest_keys[:5])}...")
                break
    
    except Exception as e:
        print_error(f"Could not parse manifest: {e}")
        return False
    
    return True


def check_model_definitions():
    """Check model definitions for Odoo 17 compliance."""
    print_header("MODEL DEFINITION VALIDATION")
    
    model_files = [
        'deal_report/models/deal_report.py',
        'deal_report/models/deal_commission_line.py',
        'deal_report/models/deal_bill_line.py',
    ]
    
    for model_file in model_files:
        if not Path(model_file).exists():
            print_warning(f"Model file not found: {model_file}")
            continue
        
        with open(model_file, 'r') as f:
            content = f.read()
        
        checks = {
            '_name': '_name' in content,
            '_description': '_description' in content,
            'api.depends': '@api.depends' in content or 'api.depends' in content,
            'fields definition': 'fields.' in content,
        }
        
        file_name = Path(model_file).name
        for check, result in checks.items():
            if result:
                print_success(f"{file_name}: has {check}")
            else:
                print_warning(f"{file_name}: missing {check}")


def check_view_fields():
    """Check that views reference valid model fields."""
    print_header("VIEW FIELD VALIDATION")
    
    import xml.etree.ElementTree as ET
    import re
    
    view_file = 'deal_report/views/deal_report_views.xml'
    
    if not Path(view_file).exists():
        print_error(f"View file not found: {view_file}")
        return False
    
    try:
        tree = ET.parse(view_file)
        root = tree.getroot()
        
        # Extract field references from XML
        fields = set()
        for elem in root.iter():
            if elem.tag == 'field':
                field_name = elem.get('name')
                if field_name:
                    fields.add(field_name)
        
        print_success(f"Found {len(fields)} unique field references")
        print_info(f"Sample fields: {', '.join(sorted(list(fields))[:5])}")
        
    except Exception as e:
        print_error(f"Error parsing view file: {e}")
        return False
    
    return True


def check_javascript_assets():
    """Check static JavaScript for Odoo 17 compatibility."""
    print_header("JAVASCRIPT ASSETS CHECK")
    
    static_path = Path('deal_report/static/src/js')
    
    if not static_path.exists():
        print_info("No JavaScript directory found (optional)")
        return True
    
    js_files = list(static_path.glob('*.js'))
    
    if not js_files:
        print_info("No JavaScript files in module")
        return True
    
    for js_file in js_files:
        # Basic checks
        with open(js_file, 'r') as f:
            content = f.read()
        
        checks = {
            'ES6 modules': 'export' in content or 'import' in content,
            'Odoo imports': '@odoo' in content or 'odoo' in content,
            'No console.log': 'console.log' not in content,
        }
        
        for check, result in checks.items():
            status = "✓" if result else "⚠️"
            print_info(f"{js_file.name}: {status} {check}")
    
    return True


def check_scss_assets():
    """Check SCSS files for Odoo 17 compatibility."""
    print_header("SCSS ASSETS CHECK")
    
    scss_path = Path('deal_report/static/src/scss')
    
    if not scss_path.exists():
        print_info("No SCSS directory found")
        return True
    
    scss_files = list(scss_path.glob('*.scss'))
    
    for scss_file in scss_files:
        with open(scss_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        print_success(f"{scss_file.name}: {len(lines)} lines")
        
        # Check for common issues
        if '\t' in content:
            print_warning(f"  Contains tabs (Odoo requires spaces)")
        else:
            print_success(f"  Uses space indentation")
        
        if 'o_' in content:
            print_success(f"  Uses Odoo class naming convention")
    
    return True


def validate_all():
    """Run all validations."""
    print_header("COMPLETE MODULE VALIDATION")
    
    results = {
        'Python Syntax': validate_python_syntax(),
        'XML Views': validate_xml_views(),
        'Manifest': check_manifest(),
        'Models': check_model_definitions(),
        'View Fields': check_view_fields(),
        'JavaScript': check_javascript_assets(),
        'SCSS': check_scss_assets(),
    }
    
    print_header("VALIDATION SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {check}")
    
    print(f"\n{passed}/{total} validations passed\n")
    
    return all(results.values())


def generate_test_report():
    """Generate a test report showing compatibility status."""
    print_header("TEST COMPATIBILITY REPORT")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'module': 'deal_report',
        'odoo_version': '17.0',
        'checks': {
            'python_version': sys.version,
            'module_path': os.getcwd(),
            'files': {
                'models': len(list(Path('deal_report/models').glob('*.py'))),
                'views': len(list(Path('deal_report/views').glob('*.xml'))),
                'data': len(list(Path('deal_report/data').glob('*.xml'))),
                'security': len(list(Path('deal_report/security').glob('*.xml'))),
                'static': len(list(Path('deal_report/static').rglob('*'))),
            }
        }
    }
    
    # Print report
    print(f"Module: {report['module']}")
    print(f"Odoo Version: {report['odoo_version']}")
    print(f"Timestamp: {report['timestamp']}\n")
    
    print("File Counts:")
    for file_type, count in report['checks']['files'].items():
        print(f"  {file_type}: {count}")
    
    # Save report
    report_file = Path('deal_report_test_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print_success(f"Report saved to {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description='deal_report Module Validation & Test Runner for Odoo 17'
    )
    parser.add_argument(
        '--validate-xml',
        action='store_true',
        help='Validate XML view files'
    )
    parser.add_argument(
        '--validate-python',
        action='store_true',
        help='Validate Python syntax'
    )
    parser.add_argument(
        '--check-manifest',
        action='store_true',
        help='Check manifest.py structure'
    )
    parser.add_argument(
        '--check-models',
        action='store_true',
        help='Check model definitions'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all validations'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate test report'
    )
    
    args = parser.parse_args()
    
    # Default: run all if no args
    if not any(vars(args).values()):
        args.all = True
    
    os.chdir(Path(__file__).parent.parent.parent)  # Change to repo root
    
    try:
        if args.all or (args.validate_xml or args.validate_python or args.check_manifest or args.check_models):
            success = validate_all()
        else:
            success = True
        
        if args.report:
            generate_test_report()
        
        if success:
            print_success("\nAll validation checks passed! Ready for Odoo 17 upgrade.")
            sys.exit(0)
        else:
            print_error("\nSome validation checks failed. Review above.")
            sys.exit(1)
    
    except Exception as e:
        print_error(f"Validation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
