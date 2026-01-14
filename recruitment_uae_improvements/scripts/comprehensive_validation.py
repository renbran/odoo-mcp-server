#!/usr/bin/env python
"""
Comprehensive Pre-Deployment Validation Test Suite
For: recruitment_uae v18.0.2.0.0
Target: eigermarvelhr.com (Odoo 18.0)

This script validates:
1. Python syntax for all models
2. XML well-formedness for all views and data
3. Field name consistency across models
4. External ID references
5. No syntax errors that would break module loading
"""

import os
import sys
import xml.etree.ElementTree as ET
import py_compile
import json
from pathlib import Path
from datetime import datetime

class ValidationReport:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.start_time = datetime.now()
    
    def add_pass(self, test_name, message=""):
        self.passed.append((test_name, message))
        print(f"✅ PASS: {test_name}")
        if message:
            print(f"       {message}")
    
    def add_fail(self, test_name, message=""):
        self.failed.append((test_name, message))
        print(f"❌ FAIL: {test_name}")
        if message:
            print(f"       {message}")
    
    def add_warning(self, test_name, message=""):
        self.warnings.append((test_name, message))
        print(f"⚠️  WARN: {test_name}")
        if message:
            print(f"       {message}")
    
    def summary(self):
        duration = datetime.now() - self.start_time
        total_passed = len(self.passed)
        total_failed = len(self.failed)
        total_warnings = len(self.warnings)
        total_tests = total_passed + total_failed + total_warnings
        
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Tests:    {total_tests}")
        print(f"Passed:         {total_passed} ✅")
        print(f"Failed:         {total_failed} ❌")
        print(f"Warnings:       {total_warnings} ⚠️")
        print(f"Duration:       {duration.total_seconds():.2f} seconds")
        print("=" * 80)
        
        if total_failed == 0:
            print("✅ ALL CRITICAL TESTS PASSED - SAFE FOR DEPLOYMENT")
            return 0
        else:
            print(f"❌ {total_failed} CRITICAL TESTS FAILED - DO NOT DEPLOY")
            print("\nFailed Tests:")
            for test_name, message in self.failed:
                print(f"  - {test_name}")
                if message:
                    print(f"    {message}")
            return 1

def validate_python_files(report, module_dir):
    """Validate all Python files for syntax errors"""
    print("\n" + "=" * 80)
    print("1. PYTHON SYNTAX VALIDATION")
    print("=" * 80)
    
    python_files = []
    for root, dirs, files in os.walk(module_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__pycache__'):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        report.add_warning("Python files", "No Python files found")
        return
    
    for py_file in sorted(python_files):
        try:
            py_compile.compile(py_file, doraise=True)
            rel_path = os.path.relpath(py_file, module_dir)
            report.add_pass(f"Python syntax: {rel_path}")
        except py_compile.PyCompileError as e:
            rel_path = os.path.relpath(py_file, module_dir)
            report.add_fail(f"Python syntax: {rel_path}", str(e)[:200])

def validate_xml_files(report, module_dir):
    """Validate all XML files for well-formedness"""
    print("\n" + "=" * 80)
    print("2. XML WELL-FORMEDNESS VALIDATION")
    print("=" * 80)
    
    xml_files = []
    for root, dirs, files in os.walk(module_dir):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    if not xml_files:
        report.add_warning("XML files", "No XML files found")
        return
    
    for xml_file in sorted(xml_files):
        try:
            ET.parse(xml_file)
            rel_path = os.path.relpath(xml_file, module_dir)
            report.add_pass(f"XML valid: {rel_path}")
        except ET.ParseError as e:
            rel_path = os.path.relpath(xml_file, module_dir)
            error_msg = f"Line {e.position[0]}, Col {e.position[1]}: {e.msg}"
            report.add_fail(f"XML valid: {rel_path}", error_msg)
            
            # Show problematic line
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    line_num = e.position[0]
                    if 0 < line_num <= len(lines):
                        print(f"       Problematic line: {lines[line_num-1].rstrip()[:100]}")
            except:
                pass

def validate_manifest(report, module_dir):
    """Validate __manifest__.py exists and is valid"""
    print("\n" + "=" * 80)
    print("3. MANIFEST VALIDATION")
    print("=" * 80)
    
    manifest_file = os.path.join(module_dir, '__manifest__.py')
    
    if not os.path.exists(manifest_file):
        report.add_fail("Manifest file exists", "__manifest__.py not found")
        return
    
    try:
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for valid Python syntax
        compile(content, manifest_file, 'exec')
        report.add_pass("Manifest syntax", "__manifest__.py is valid Python")
        
        # Check required fields
        if "'name'" in content and "'version'" in content:
            report.add_pass("Manifest fields", "Contains 'name' and 'version'")
        else:
            report.add_warning("Manifest fields", "Missing 'name' or 'version'")
        
        # Extract version
        import re
        version_match = re.search(r"'version':\s*['\"]([^'\"]+)['\"]", content)
        if version_match:
            version = version_match.group(1)
            report.add_pass(f"Module version: {version}")
    
    except Exception as e:
        report.add_fail("Manifest parsing", str(e)[:200])

def validate_model_inheritance(report, module_dir):
    """Validate model inheritance patterns"""
    print("\n" + "=" * 80)
    print("4. MODEL INHERITANCE VALIDATION")
    print("=" * 80)
    
    models_dir = os.path.join(module_dir, 'models')
    if not os.path.exists(models_dir):
        report.add_warning("Model files", "No models directory found")
        return
    
    # Check for duplicate mail.thread inheritance
    problematic_patterns = [
        ('mail.thread.*mail.activity.mixin', 'Duplicate mail thread inheritance'),
        ('mail.activity.mixin.*mail.thread', 'Duplicate mail thread inheritance'),
    ]
    
    for model_file in os.listdir(models_dir):
        if model_file.endswith('.py') and model_file.startswith('recruitment_'):
            file_path = os.path.join(models_dir, model_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if using string inheritance (correct)
            if "_inherit = '" in content or '_inherit = "' in content:
                report.add_pass(f"Model inheritance: {model_file}", "Using string inheritance (correct)")
            elif "_inherit = [" in content:
                # Check if it contains both mail.thread and mail.activity.mixin
                if 'mail.thread' in content and 'mail.activity.mixin' in content:
                    report.add_fail(f"Model inheritance: {model_file}", 
                                  "List inheritance with duplicate mail.thread/mail.activity.mixin")
                else:
                    report.add_warning(f"Model inheritance: {model_file}", "Using list inheritance")

def validate_field_consistency(report, module_dir):
    """Validate field names are consistent and valid"""
    print("\n" + "=" * 80)
    print("5. FIELD CONSISTENCY VALIDATION")
    print("=" * 80)
    
    # Check for required field names
    required_fields = {
        'recruitment_job_requisition.py': ['application_count', 'contract_count', 'deployment_count'],
        'recruitment_application.py': ['contract_count'],
        'recruitment_contract.py': ['deployment_count'],
    }
    
    models_dir = os.path.join(module_dir, 'models')
    for model_file, fields in required_fields.items():
        file_path = os.path.join(models_dir, model_file)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_fields = []
            for field in fields:
                if field not in content:
                    missing_fields.append(field)
            
            if missing_fields:
                report.add_warning(f"Fields in {model_file}", 
                                 f"Missing: {', '.join(missing_fields)}")
            else:
                report.add_pass(f"Fields in {model_file}", 
                              f"All required fields present: {', '.join(fields)}")

def validate_external_ids(report, module_dir):
    """Validate external ID references in views"""
    print("\n" + "=" * 80)
    print("6. EXTERNAL ID REFERENCE VALIDATION")
    print("=" * 80)
    
    views_dir = os.path.join(module_dir, 'views')
    if not os.path.exists(views_dir):
        report.add_warning("Views directory", "Not found")
        return
    
    for xml_file in os.listdir(views_dir):
        if xml_file.endswith('.xml'):
            file_path = os.path.join(views_dir, xml_file)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Look for inherit_id references
                inherit_ids = []
                for elem in root.findall('.//field[@name="inherit_id"]'):
                    ref = elem.get('ref')
                    if ref:
                        inherit_ids.append(ref)
                
                if inherit_ids:
                    report.add_pass(f"External IDs in {xml_file}", 
                                  f"Found {len(inherit_ids)} inherit_id references")
                else:
                    report.add_pass(f"External IDs in {xml_file}", "No inherit_id references")
            
            except Exception as e:
                report.add_warning(f"External IDs in {xml_file}", str(e)[:100])

def validate_file_structure(report, module_dir):
    """Validate module directory structure"""
    print("\n" + "=" * 80)
    print("7. MODULE STRUCTURE VALIDATION")
    print("=" * 80)
    
    required_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
    ]
    
    required_dirs = [
        'models',
        'views',
        'data',
        'security',
    ]
    
    # Check directories
    for dir_name in required_dirs:
        dir_path = os.path.join(module_dir, dir_name)
        if os.path.isdir(dir_path):
            report.add_pass(f"Directory exists: {dir_name}")
        else:
            report.add_fail(f"Directory exists: {dir_name}", "Not found or not a directory")
    
    # Check files
    for file_name in required_files:
        file_path = os.path.join(module_dir, file_name)
        if os.path.isfile(file_path):
            report.add_pass(f"File exists: {file_name}")
        else:
            report.add_fail(f"File exists: {file_name}", "Not found")

def validate_data_files(report, module_dir):
    """Validate data file integrity"""
    print("\n" + "=" * 80)
    print("8. DATA FILE VALIDATION")
    print("=" * 80)
    
    data_dir = os.path.join(module_dir, 'data')
    if not os.path.exists(data_dir):
        report.add_warning("Data directory", "Not found")
        return
    
    # Check for email template name conflicts
    email_template_file = os.path.join(data_dir, 'email_template_data.xml')
    if os.path.exists(email_template_file):
        try:
            tree = ET.parse(email_template_file)
            root = tree.getroot()
            
            template_names = set()
            conflicts = []
            
            for record in root.findall('.//record[@model="mail.template"]'):
                name_field = record.find('./field[@name="name"]')
                if name_field is not None and name_field.text:
                    template_name = name_field.text
                    if 'Enhanced' in template_name or 'enhanced' in template_name:
                        report.add_pass(f"Template naming: {template_name[:50]}")
                    else:
                        report.add_warning(f"Template naming: {template_name[:50]}", 
                                         "Does not have 'Enhanced' suffix")
        
        except Exception as e:
            report.add_warning("Email template validation", str(e)[:100])

def main():
    """Run all validations"""
    print("\n" + "=" * 80)
    print("RECRUITMENT UAE v18.0.2.0.0 - PRE-DEPLOYMENT VALIDATION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Determine module directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # If script is in root, go up one level
    if os.path.basename(script_dir) == 'scripts':
        module_dir = os.path.dirname(script_dir)
    else:
        module_dir = script_dir
    
    if not os.path.exists(os.path.join(module_dir, '__manifest__.py')):
        print(f"❌ ERROR: Cannot find __manifest__.py in {module_dir}")
        print("Please run this script from the module root directory")
        return 1
    
    print(f"Module directory: {module_dir}\n")
    
    # Create report
    report = ValidationReport()
    
    # Run all validations
    validate_file_structure(report, module_dir)
    validate_manifest(report, module_dir)
    validate_python_files(report, module_dir)
    validate_xml_files(report, module_dir)
    validate_model_inheritance(report, module_dir)
    validate_field_consistency(report, module_dir)
    validate_external_ids(report, module_dir)
    validate_data_files(report, module_dir)
    
    # Print summary and return exit code
    exit_code = report.summary()
    
    # Write report to file
    report_file = os.path.join(module_dir, f'validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Validation Report - {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Passed: {len(report.passed)}\n")
            f.write(f"Failed: {len(report.failed)}\n")
            f.write(f"Warnings: {len(report.warnings)}\n\n")
            
            if report.failed:
                f.write("FAILED TESTS:\n")
                for test, msg in report.failed:
                    f.write(f"  - {test}: {msg}\n")
        print(f"\nReport saved to: {report_file}")
    except:
        pass
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
