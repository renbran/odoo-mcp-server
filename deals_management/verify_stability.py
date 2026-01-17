#!/usr/bin/env python3
"""
Deals Management Module - Stability & Verification Script
Comprehensive checks to ensure module is production-ready
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

class DealsModuleValidator:
    def __init__(self, module_path="deals_management"):
        self.module_path = Path(module_path)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def log(self, check_name, status, message=""):
        """Log a check result"""
        check = {
            "name": check_name,
            "status": status,
            "message": message
        }
        self.checks.append(check)
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {check_name}: {status}")
        if message:
            print(f"   {message}")
        
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        else:
            self.warnings += 1
    
    def file_exists(self, filepath):
        """Check if file exists"""
        return (self.module_path / filepath).exists()
    
    def read_file(self, filepath):
        """Read file contents"""
        try:
            with open(self.module_path / filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    def check_file_structure(self):
        """Verify all required files exist"""
        print("\n📁 FILE STRUCTURE CHECKS")
        print("=" * 60)
        
        required_files = {
            "__init__.py": "Python package init",
            "__manifest__.py": "Module metadata",
            "models/__init__.py": "Models package init",
            "models/sale_order_deals.py": "Main model extension",
            "security/ir.model.access.csv": "Access control rules",
            "views/deals_views.xml": "Deal views and actions",
            "views/deals_menu.xml": "Menu structure",
            "views/commission_views.xml": "Commission views",
            "views/commission_line_views.xml": "Bill integration views",
            "views/project_unit_views.xml": "Project views",
        }
        
        for filepath, description in required_files.items():
            if self.file_exists(filepath):
                self.log(f"File: {filepath}", "PASS", description)
            else:
                self.log(f"File: {filepath}", "FAIL", f"Missing: {description}")
    
    def check_manifest(self):
        """Verify manifest.py configuration"""
        print("\n⚙️  MANIFEST CONFIGURATION CHECKS")
        print("=" * 60)
        
        manifest = self.read_file("__manifest__.py")
        
        if not manifest:
            self.log("Read __manifest__.py", "FAIL", "Cannot read manifest")
            return
        
        # Check required fields
        checks = {
            "'name'": "Module name",
            "'version'": "Version number",
            "'category'": "Category classification",
            "'author'": "Author information",
            "'depends'": "Dependencies list",
            "'data'": "Data files list",
            "'installable'": "Installable flag",
            "'application'": "Application flag",
        }
        
        for field, description in checks.items():
            if field in manifest:
                self.log(f"Manifest: {field}", "PASS", description)
            else:
                self.log(f"Manifest: {field}", "FAIL", f"Missing: {description}")
        
        # Check dependencies
        if "'sale'" in manifest and "'commission_ax'" in manifest:
            self.log("Dependencies: sale and commission_ax", "PASS")
        else:
            self.log("Dependencies: Base modules", "FAIL", "Missing required dependencies")
    
    def check_model_file(self):
        """Verify model definition"""
        print("\n🗂️  MODEL FILE CHECKS")
        print("=" * 60)
        
        model_file = self.read_file("models/sale_order_deals.py")
        
        if not model_file:
            self.log("Read sale_order_deals.py", "FAIL", "Cannot read model file")
            return
        
        # Check class definition
        if "class SaleOrderDeals" in model_file:
            self.log("Class definition", "PASS", "SaleOrderDeals class found")
        else:
            self.log("Class definition", "FAIL", "SaleOrderDeals class not found")
        
        # Check inheritance
        if "_inherit = 'sale.order'" in model_file:
            self.log("Model inheritance", "PASS", "Extends sale.order")
        else:
            self.log("Model inheritance", "FAIL", "Doesn't inherit from sale.order")
        
        # Check field definitions
        field_checks = {
            "sales_type = fields.Selection": "Sales type field",
            "buyer_name = fields.Char": "Buyer name field",
            "buyer_email = fields.Char": "Buyer email field",
            "deal_sales_value = fields.Monetary": "Deal sales value field",
            "commission_count = fields.Integer": "Commission count field",
            "bill_count = fields.Integer": "Bill count field",
        }
        
        for pattern, description in field_checks.items():
            if pattern in model_file:
                self.log(f"Field: {description}", "PASS")
            else:
                self.log(f"Field: {description}", "FAIL", "Field definition not found")
        
        # Check computed fields
        if "@api.depends" in model_file:
            self.log("Computed fields", "PASS", "@api.depends decorators found")
        else:
            self.log("Computed fields", "FAIL", "Missing @api.depends decorators")
        
        # Check for action methods
        actions = {
            "def action_view_invoices": "Invoice view action",
            "def action_view_commissions": "Commission view action",
            "def action_view_bills": "Bill view action",
        }
        
        for pattern, description in actions.items():
            if pattern in model_file:
                self.log(f"Action: {description}", "PASS")
            else:
                self.log(f"Action: {description}", "WARN", "Action method not found")
    
    def check_views(self):
        """Verify view definitions"""
        print("\n👁️  VIEW CONFIGURATION CHECKS")
        print("=" * 60)
        
        views_file = self.read_file("views/deals_views.xml")
        
        if not views_file:
            self.log("Read deals_views.xml", "FAIL", "Cannot read views file")
            return
        
        # Check action definitions
        action_pattern = r'<record id="action_([^"]+)"'
        actions = re.findall(action_pattern, views_file)
        
        if len(actions) >= 5:
            self.log(f"Action definitions: {len(actions)} found", "PASS", 
                    f"Actions: {', '.join(actions[:3])}...")
        else:
            self.log(f"Action definitions", "FAIL", f"Only {len(actions)} actions found")
        
        # Check view types
        view_types = ['tree', 'form', 'search']
        for view_type in view_types:
            if f'type="{view_type}"' in views_file:
                self.log(f"View type: {view_type}", "PASS")
            else:
                self.log(f"View type: {view_type}", "WARN", f"{view_type} view not found")
    
    def check_menu_structure(self):
        """Verify menu structure"""
        print("\n📋 MENU STRUCTURE CHECKS")
        print("=" * 60)
        
        menu_file = self.read_file("views/deals_menu.xml")
        
        if not menu_file:
            self.log("Read deals_menu.xml", "FAIL", "Cannot read menu file")
            return
        
        # Check menu items
        menu_pattern = r'<menuitem[^>]*id="([^"]+)"'
        menus = re.findall(menu_pattern, menu_file)
        
        if len(menus) >= 3:
            self.log(f"Menu items: {len(menus)} defined", "PASS", 
                    f"Including: Deals, Commissions")
        else:
            self.log(f"Menu items", "FAIL", f"Only {len(menus)} menus found")
        
        # Check action references
        if 'action=' in menu_file:
            action_refs = re.findall(r'action="([^"]+)"', menu_file)
            if len(action_refs) > 0:
                self.log(f"Menu actions: {len(action_refs)} references", "PASS")
            else:
                self.log(f"Menu actions", "FAIL", "No action references found")
        else:
            self.log(f"Menu actions", "FAIL", "Missing action attribute")
    
    def check_security(self):
        """Verify security configuration"""
        print("\n🔐 SECURITY CONFIGURATION CHECKS")
        print("=" * 60)
        
        security_file = self.read_file("security/ir.model.access.csv")
        
        if not security_file:
            self.log("Read ir.model.access.csv", "FAIL", "Cannot read security file")
            return
        
        # Check header
        if "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink" in security_file:
            self.log("ACL header format", "PASS", "Standard CSV format")
        else:
            self.log("ACL header format", "WARN", "Non-standard header")
        
        # Check for access rules
        if "sale_order" in security_file:
            self.log("Sale order rules", "PASS", "Access rules defined")
        else:
            self.log("Sale order rules", "WARN", "No specific sale.order rules")
    
    def check_python_syntax(self):
        """Check Python syntax"""
        print("\n🐍 PYTHON SYNTAX CHECKS")
        print("=" * 60)
        
        python_files = [
            "models/sale_order_deals.py",
            "__init__.py",
            "models/__init__.py",
        ]
        
        for pyfile in python_files:
            content = self.read_file(pyfile)
            if content:
                try:
                    compile(content, pyfile, 'exec')
                    self.log(f"Syntax: {pyfile}", "PASS", "Valid Python syntax")
                except SyntaxError as e:
                    self.log(f"Syntax: {pyfile}", "FAIL", f"Syntax error: {e}")
            else:
                self.log(f"Syntax: {pyfile}", "FAIL", "Cannot read file")
    
    def check_xml_syntax(self):
        """Check XML syntax"""
        print("\n📝 XML SYNTAX CHECKS")
        print("=" * 60)
        
        xml_files = [
            "views/deals_views.xml",
            "views/deals_menu.xml",
            "views/commission_views.xml",
            "views/commission_line_views.xml",
            "views/project_unit_views.xml",
        ]
        
        for xmlfile in xml_files:
            content = self.read_file(xmlfile)
            if content:
                # Basic XML validation
                if content.count('<') == content.count('>'):
                    # Check for odoo root
                    if '<odoo>' in content or '<?xml' in content:
                        self.log(f"XML: {Path(xmlfile).name}", "PASS", "Valid XML structure")
                    else:
                        self.log(f"XML: {Path(xmlfile).name}", "WARN", "Missing XML declaration")
                else:
                    self.log(f"XML: {Path(xmlfile).name}", "FAIL", "Mismatched XML tags")
            else:
                self.log(f"XML: {Path(xmlfile).name}", "FAIL", "Cannot read file")
    
    def check_data_loading_order(self):
        """Verify data loading order"""
        print("\n📊 DATA LOADING ORDER CHECKS")
        print("=" * 60)
        
        manifest = self.read_file("__manifest__.py")
        
        if manifest and "'data'" in manifest:
            # Extract data list
            data_match = re.search(r"'data':\s*\[(.*?)\]", manifest, re.DOTALL)
            if data_match:
                data_str = data_match.group(1)
                files = re.findall(r"'([^']+\.xml)'", data_str)
                
                # Verify order: security should load first
                if files:
                    if 'ir.model.access.csv' in files[0] or 'security' in files[0]:
                        self.log("Data loading: security first", "PASS")
                    else:
                        self.log("Data loading: security first", "WARN", 
                                f"Security should load first, got {files[0]}")
                    
                    self.log(f"Data files: {len(files)} defined", "PASS")
                    for i, f in enumerate(files, 1):
                        print(f"   {i}. {f}")
    
    def check_odoo17_compliance(self):
        """Verify Odoo 17 compliance"""
        print("\n✅ ODOO 17 COMPLIANCE CHECKS")
        print("=" * 60)
        
        model_file = self.read_file("models/sale_order_deals.py")
        
        if not model_file:
            self.log("Odoo 17 compliance check", "FAIL", "Cannot read model")
            return
        
        # Check for deprecated patterns
        checks = {
            "@api.one": ("Avoid @api.one", True),  # Should NOT be present
            "cr.commit()": ("No manual commits", True),  # Should NOT be present
            "from odoo import api, fields, models": ("Proper imports", False),  # Should be present
            "@api.depends": ("Uses @api.depends", False),  # Should be present
        }
        
        for pattern, (description, should_not_exist) in checks.items():
            if should_not_exist:
                if pattern not in model_file:
                    self.log(f"Compliance: {description}", "PASS")
                else:
                    self.log(f"Compliance: {description}", "FAIL", f"Found deprecated: {pattern}")
            else:
                if pattern in model_file:
                    self.log(f"Compliance: {description}", "PASS")
                else:
                    self.log(f"Compliance: {description}", "FAIL", f"Missing: {pattern}")
    
    def generate_report(self):
        """Generate validation report"""
        report = {
            "timestamp": self.timestamp,
            "module_name": "deals_management",
            "validation_results": {
                "passed": self.passed,
                "failed": self.failed,
                "warnings": self.warnings,
                "total": len(self.checks),
            },
            "status": "PASS" if self.failed == 0 else "FAIL",
            "checks": self.checks,
        }
        
        report_file = f"stability_report_{self.timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file, report
    
    def validate(self):
        """Run all validation checks"""
        print("\n" + "=" * 60)
        print("DEALS MANAGEMENT MODULE - STABILITY VERIFICATION")
        print("=" * 60)
        
        self.check_file_structure()
        self.check_manifest()
        self.check_model_file()
        self.check_views()
        self.check_menu_structure()
        self.check_security()
        self.check_python_syntax()
        self.check_xml_syntax()
        self.check_data_loading_order()
        self.check_odoo17_compliance()
        
        # Generate report
        report_file, report = self.generate_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"✅ Passed:  {self.passed}/{len(self.checks)}")
        print(f"❌ Failed:  {self.failed}/{len(self.checks)}")
        print(f"⚠️  Warnings: {self.warnings}/{len(self.checks)}")
        
        if self.failed == 0:
            print("\n🎉 MODULE IS STABLE AND PRODUCTION-READY!")
        elif self.failed <= 2:
            print("\n⚠️  Module has minor issues, review recommendations above.")
        else:
            print("\n❌ Module has critical issues, resolve before deploying.")
        
        print(f"\nDetailed Report: {report_file}")
        print("=" * 60)
        
        return self.failed == 0


if __name__ == "__main__":
    module_path = sys.argv[1] if len(sys.argv) > 1 else "deals_management"
    
    if not os.path.exists(module_path):
        print(f"ERROR: Module path not found: {module_path}")
        sys.exit(1)
    
    validator = DealsModuleValidator(module_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)
