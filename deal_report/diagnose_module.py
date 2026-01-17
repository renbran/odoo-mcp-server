#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnose the module issue by checking for syntax errors
in all Python and XML files.
"""

import os
import sys
import ast
from xml.etree import ElementTree as ET

def check_python_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_xml_syntax(filepath):
    """Check if an XML file has valid syntax."""
    try:
        ET.parse(filepath)
        return True, None
    except ET.ParseError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_models():
    """Verify all models can be parsed."""
    print("\n" + "="*70)
    print("CHECKING MODEL FILES")
    print("="*70)
    
    model_files = [
        'models/__init__.py',
        'models/deal_report.py',
        'models/deal_commission_line.py',
        'models/deal_bill_line.py',
        'models/deal_dashboard.py',
    ]
    
    all_ok = True
    for filepath in model_files:
        if os.path.exists(filepath):
            ok, error = check_python_syntax(filepath)
            if ok:
                print(f"✓ {filepath}")
            else:
                print(f"✗ {filepath}")
                print(f"  Error: {error}")
                all_ok = False
        else:
            print(f"✗ {filepath} - NOT FOUND")
            all_ok = False
    
    return all_ok

def check_xml_files():
    """Verify all XML files are valid."""
    print("\n" + "="*70)
    print("CHECKING XML VIEW FILES")
    print("="*70)
    
    xml_files = [
        'views/deal_report_views.xml',
        'views/deal_menu.xml',
        'views/deal_report_search.xml',
        'views/deal_dashboard_views.xml',
        'views/deal_report_analytics.xml',
        'data/deal_sequence.xml',
        'data/commission_product.xml',
        'security/deal_report_security.xml',
        'reports/deal_report_templates.xml',
    ]
    
    all_ok = True
    for filepath in xml_files:
        if os.path.exists(filepath):
            ok, error = check_xml_syntax(filepath)
            if ok:
                print(f"✓ {filepath}")
            else:
                print(f"✗ {filepath}")
                print(f"  Error: {error}")
                all_ok = False
        else:
            print(f"✗ {filepath} - NOT FOUND")
            all_ok = False
    
    return all_ok

def check_manifest():
    """Verify manifest is valid Python."""
    print("\n" + "="*70)
    print("CHECKING MANIFEST")
    print("="*70)
    
    ok, error = check_python_syntax('__manifest__.py')
    if ok:
        print(f"✓ __manifest__.py is valid")
        return True
    else:
        print(f"✗ __manifest__.py has errors:")
        print(f"  {error}")
        return False

def check_imports():
    """Try to import the module components."""
    print("\n" + "="*70)
    print("CHECKING IMPORTS")
    print("="*70)
    
    # Add to path
    sys.path.insert(0, os.getcwd())
    
    try:
        from models import deal_report
        print("✓ deal_report module can be imported")
    except Exception as e:
        print(f"✗ deal_report module import failed: {e}")
    
    try:
        from models import deal_commission_line
        print("✓ deal_commission_line module can be imported")
    except Exception as e:
        print(f"✗ deal_commission_line module import failed: {e}")
    
    try:
        from models import deal_bill_line
        print("✓ deal_bill_line module can be imported")
    except Exception as e:
        print(f"✗ deal_bill_line module import failed: {e}")
    
    try:
        from models import deal_dashboard
        print("✓ deal_dashboard module can be imported")
    except Exception as e:
        print(f"✗ deal_dashboard module import failed: {e}")

def main():
    """Run all diagnostics."""
    print("\n" + "="*70)
    print("DEAL REPORT MODULE - DIAGNOSTIC CHECK")
    print("="*70)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    results = []
    results.append(("Manifest", check_manifest()))
    results.append(("Models", check_python_syntax('models/__init__.py')[0]))
    results.append(("XML Files", check_xml_files()))
    results.append(("Python Models", check_models()))
    
    check_imports()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    all_ok = all(r[1] for r in results)
    
    for name, ok in results:
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"{status}: {name}")
    
    if all_ok:
        print("\n✓ All checks passed!")
        print("\nThe module files are syntactically correct.")
        print("The internal server error might be due to:")
        print("1. Database/registry corruption during installation")
        print("2. A module in the database being in an error state")
        print("\nTry these solutions:")
        print("A. Clear Odoo cache and restart:")
        print("   docker exec odoo17_app rm -rf /var/lib/odoo/.cache /var/lib/odoo/sessions/*")
        print("   docker restart odoo17_app")
        print("\nB. Uninstall and reinstall the module:")
        print("   Go to Apps > deal_report > Uninstall > Remove")
        print("   Then reinstall from Apps")
        return True
    else:
        print("\n✗ Some checks failed!")
        print("Please fix the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
