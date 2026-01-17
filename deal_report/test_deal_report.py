#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deal Report Module - Installation Test Suite
Tests module readiness for Odoo 17.0 installation

Run this after installing the module to verify functionality:
  python test_deal_report.py
"""

import subprocess
import sys
import json
from datetime import datetime

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.start_time = datetime.now()
    
    def add_pass(self, test_name, details=""):
        self.passed.append({"name": test_name, "details": details})
        print(f"[PASS] {test_name}")
        if details:
            print(f"  -> {details}")
    
    def add_fail(self, test_name, error):
        self.failed.append({"name": test_name, "error": str(error)})
        print(f"[FAIL] {test_name}")
        print(f"  -> {error}")
    
    def add_warning(self, test_name, warning):
        self.warnings.append({"name": test_name, "warning": warning})
        print(f"[WARNING] {test_name}")
        print(f"  -> {warning}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed)
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*60)
        print("TEST SUMMARY".center(60))
        print("="*60)
        print(f"Total Tests:  {total}")
        print(f"Passed:       {len(self.passed)} [OK]")
        print(f"Failed:       {len(self.failed)} [ERROR]")
        print(f"Warnings:     {len(self.warnings)} [WARN]")
        print(f"Success Rate: {(len(self.passed)/total*100 if total > 0 else 0):.1f}%")
        print(f"Time Elapsed: {elapsed:.2f}s")
        print("="*60 + "\n")
        
        return len(self.failed) == 0

# Pre-Installation Checks
def test_file_structure(results):
    """Test 1: Verify all required files exist"""
    print("\n>>> Test 1: File Structure Verification")
    
    import os
    
    required_files = {
        "Python": [
            "__init__.py",
            "__manifest__.py",
            "models/__init__.py",
            "models/deal_report.py",
            "models/deal_commission_line.py",
            "models/deal_bill_line.py",
            "models/deal_dashboard.py",
        ],
        "Security": [
            "security/ir.model.access.csv",
            "security/deal_report_security.xml",
        ],
        "Data": [
            "data/deal_sequence.xml",
            "data/commission_product.xml",
        ],
        "Views": [
            "views/deal_report_views.xml",
            "views/deal_menu.xml",
            "views/deal_report_search.xml",
            "views/deal_dashboard_views.xml",
            "views/deal_report_analytics.xml",
        ],
        "Reports": [
            "reports/deal_report_templates.xml",
        ],
    }
    
    module_dir = os.path.dirname(os.path.abspath(__file__))
    all_exist = True
    
    for category, files in required_files.items():
        for fname in files:
            fpath = os.path.join(module_dir, fname)
            if os.path.exists(fpath):
                results.add_pass(f"File exists: {fname}")
            else:
                results.add_fail(f"File missing: {fname}", f"Expected at {fpath}")
                all_exist = False
    
    if all_exist:
        results.add_pass("File Structure", "All required files present")
    
    return all_exist

def test_python_syntax(results):
    """Test 2: Verify Python syntax is valid"""
    print("\n>>> Test 2: Python Syntax Validation")
    
    import py_compile
    import os
    
    python_files = [
        "__init__.py",
        "__manifest__.py",
        "models/__init__.py",
        "models/deal_report.py",
        "models/deal_commission_line.py",
        "models/deal_bill_line.py",
        "models/deal_dashboard.py",
    ]
    
    module_dir = os.path.dirname(os.path.abspath(__file__))
    syntax_ok = True
    
    for fname in python_files:
        fpath = os.path.join(module_dir, fname)
        try:
            py_compile.compile(fpath, doraise=True)
            results.add_pass(f"Syntax valid: {fname}")
        except py_compile.PyCompileError as e:
            results.add_fail(f"Syntax error: {fname}", str(e))
            syntax_ok = False
    
    return syntax_ok

def test_manifest_structure(results):
    """Test 3: Verify manifest.py is properly structured"""
    print("\n>>> Test 3: Manifest Structure")
    
    import os
    import ast
    
    manifest_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "__manifest__.py"
    )
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        # Parse manifest
        parsed = ast.literal_eval(manifest_content)
        
        required_fields = ['name', 'version', 'summary', 'category', 'author', 'license', 'depends', 'data', 'installable']
        
        for field in required_fields:
            if field in parsed:
                if field == 'depends':
                    results.add_pass(f"Manifest field: {field}", f"Dependencies: {parsed[field]}")
                elif field == 'data':
                    results.add_pass(f"Manifest field: {field}", f"{len(parsed[field])} data files")
                else:
                    results.add_pass(f"Manifest field: {field}", f"Value: {parsed[field]}")
            else:
                results.add_fail(f"Manifest field missing: {field}", "Required field not found")
        
        if parsed.get('installable'):
            results.add_pass("Module", "Module is installable")
            return True
        else:
            results.add_fail("Module", "Module not marked as installable")
            return False
            
    except Exception as e:
        results.add_fail("Manifest parsing", str(e))
        return False

def test_model_definitions(results):
    """Test 4: Verify model definitions"""
    print("\n>>> Test 4: Model Definitions")
    
    import os
    import re
    
    models_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "models"
    )
    
    expected_models = {
        "deal_report.py": "DealReport",
        "deal_commission_line.py": "DealCommissionLine",
        "deal_bill_line.py": "DealBillLine",
        "deal_dashboard.py": "DealDashboard",
    }
    
    all_ok = True
    
    for fname, class_name in expected_models.items():
        fpath = os.path.join(models_dir, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if f"class {class_name}" in content:
                if "_name =" in content:
                    model_name = re.search(r"_name\s*=\s*['\"]([^'\"]+)['\"]", content)
                    if model_name:
                        results.add_pass(
                            f"Model: {class_name}",
                            f"Model name: {model_name.group(1)}"
                        )
                    else:
                        results.add_warning(
                            f"Model: {class_name}",
                            "Model name not found in file"
                        )
                else:
                    results.add_fail(
                        f"Model: {class_name}",
                        "Model name (_name) not defined"
                    )
                    all_ok = False
            else:
                results.add_fail(
                    f"Model: {class_name}",
                    f"Class {class_name} not found in {fname}"
                )
                all_ok = False
        except Exception as e:
            results.add_fail(f"Reading {fname}", str(e))
            all_ok = False
    
    return all_ok

def test_dependencies(results):
    """Test 5: Verify module dependencies"""
    print("\n>>> Test 5: Module Dependencies")
    
    import os
    import ast
    
    manifest_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "__manifest__.py"
    )
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        parsed = ast.literal_eval(manifest_content)
        dependencies = parsed.get('depends', [])
        
        required_deps = ['sale', 'account', 'mail']
        
        for dep in dependencies:
            if dep in required_deps:
                results.add_pass(f"Dependency: {dep}", "✓ Found")
            else:
                results.add_pass(f"Dependency: {dep}", "Additional dependency")
        
        missing = [d for d in required_deps if d not in dependencies]
        if missing:
            results.add_fail(
                "Missing dependencies",
                f"Required but not declared: {missing}"
            )
            return False
        
        return True
        
    except Exception as e:
        results.add_fail("Dependency check", str(e))
        return False

def test_views_and_menus(results):
    """Test 6: Verify XML views and menus"""
    print("\n>>> Test 6: Views and Menus")
    
    import os
    import xml.etree.ElementTree as ET
    
    view_files = {
        "views/deal_report_views.xml": ["action_deal_report", "view_deal_report_tree", "view_deal_report_form"],
        "views/deal_menu.xml": ["menu_deal_root", "menu_deal_report"],
        "views/deal_dashboard_views.xml": ["view_deal_dashboard_form", "action_deal_dashboard"],
    }
    
    module_dir = os.path.dirname(os.path.abspath(__file__))
    all_ok = True
    
    for fname, expected_ids in view_files.items():
        fpath = os.path.join(module_dir, fname)
        try:
            tree = ET.parse(fpath)
            root = tree.getroot()
            
            # Find all id attributes
            found_ids = set()
            for elem in root.iter():
                if 'id' in elem.attrib:
                    found_ids.add(elem.attrib['id'])
            
            for expected_id in expected_ids:
                if expected_id in found_ids:
                    results.add_pass(f"View ID: {expected_id}", f"Found in {fname}")
                else:
                    results.add_fail(f"View ID: {expected_id}", f"Not found in {fname}")
                    all_ok = False
            
        except ET.ParseError as e:
            results.add_fail(f"XML parsing: {fname}", str(e))
            all_ok = False
        except FileNotFoundError:
            results.add_fail(f"File not found: {fname}", "File does not exist")
            all_ok = False
    
    return all_ok

def test_security_rules(results):
    """Test 7: Verify security configuration"""
    print("\n>>> Test 7: Security Rules")
    
    import os
    import csv
    
    access_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "security/ir.model.access.csv"
    )
    
    try:
        with open(access_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            access_rules = list(reader)
        
        expected_models = [
            'deal.report',
            'deal.commission.line',
            'deal.bill.line',
            'deal.dashboard'
        ]
        
        found_models = set()
        for rule in access_rules:
            model_id = rule.get('model_id:id', '')
            if 'model_' in model_id:
                model_name = model_id.replace('model_', '').replace('_', '.')
                found_models.add(model_name)
                results.add_pass(
                    f"Access rule: {model_name}",
                    f"Permissions: R={rule.get('perm_read', '0')} W={rule.get('perm_write', '0')} C={rule.get('perm_create', '0')} D={rule.get('perm_unlink', '0')}"
                )
        
        missing = [m for m in expected_models if m not in found_models]
        if missing:
            results.add_fail(
                "Missing access rules",
                f"No rules for: {missing}"
            )
            return False
        
        return True
        
    except Exception as e:
        results.add_fail("Security configuration", str(e))
        return False

def test_data_files(results):
    """Test 8: Verify data initialization files"""
    print("\n>>> Test 8: Data Files")
    
    import os
    import xml.etree.ElementTree as ET
    
    data_files = {
        "data/deal_sequence.xml": ["seq_deal_report"],
        "data/commission_product.xml": ["product_commission_template", "product_commission"],
    }
    
    module_dir = os.path.dirname(os.path.abspath(__file__))
    all_ok = True
    
    for fname, expected_records in data_files.items():
        fpath = os.path.join(module_dir, fname)
        try:
            tree = ET.parse(fpath)
            root = tree.getroot()
            
            found_records = set()
            for record in root.findall('.//record'):
                record_id = record.get('id')
                if record_id:
                    found_records.add(record_id)
            
            for expected_id in expected_records:
                if expected_id in found_records:
                    results.add_pass(f"Data record: {expected_id}", f"Found in {fname}")
                else:
                    results.add_fail(f"Data record: {expected_id}", f"Not found in {fname}")
                    all_ok = False
            
        except ET.ParseError as e:
            results.add_fail(f"XML parsing: {fname}", str(e))
            all_ok = False
        except FileNotFoundError:
            results.add_warning(f"Data file: {fname}", "File not found (will be created on installation)")
    
    return all_ok

def test_assets(results):
    """Test 9: Verify static assets"""
    print("\n>>> Test 9: Static Assets")
    
    import os
    
    assets = [
        "static/src/scss/deal_report.scss",
    ]
    
    module_dir = os.path.dirname(os.path.abspath(__file__))
    all_ok = True
    
    for asset_path in assets:
        full_path = os.path.join(module_dir, asset_path)
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            results.add_pass(f"Asset: {asset_path}", f"Size: {file_size} bytes")
        else:
            results.add_warning(f"Asset: {asset_path}", "Not found (optional)")
    
    return all_ok

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DEAL REPORT MODULE - INSTALLATION TEST SUITE".center(60))
    print("="*60)
    print("Testing module readiness for Odoo 17.0 installation\n")
    
    results = TestResults()
    
    # Run all tests
    test_file_structure(results)
    test_python_syntax(results)
    test_manifest_structure(results)
    test_model_definitions(results)
    test_dependencies(results)
    test_views_and_menus(results)
    test_security_rules(results)
    test_data_files(results)
    test_assets(results)
    
    # Print summary
    success = results.summary()
    
    if success:
        print("\n[OK] ALL TESTS PASSED - Module is ready for installation!")
        print("\nNext steps:")
        print("1. Copy module to Odoo addons directory")
        print("2. Restart Odoo service")
        print("3. Go to Apps & Modules")
        print("4. Search for 'Deal Report'")
        print("5. Click 'Install'")
        return 0
    else:
        print("\n[ERROR] SOME TESTS FAILED - Please fix issues before installation")
        if results.failed:
            print(f"\nFailed tests: {len(results.failed)}")
            for test in results.failed:
                print(f"  - {test['name']}: {test['error']}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
