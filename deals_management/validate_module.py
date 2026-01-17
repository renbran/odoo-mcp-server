#!/usr/bin/env python3
"""
Validate deals_management module structure and configuration
Run this before deploying to ensure module integrity
"""

import os
import sys
import re
from pathlib import Path

class ModuleValidator:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.info = []
        
    def log_error(self, msg):
        self.errors.append(f"❌ ERROR: {msg}")
        
    def log_warning(self, msg):
        self.warnings.append(f"⚠️  WARNING: {msg}")
        
    def log_info(self, msg):
        self.info.append(f"✅ {msg}")
    
    def validate_file_structure(self):
        """Check that all required files exist"""
        print("\n🔍 Validating file structure...")
        
        required_files = [
            '__init__.py',
            '__manifest__.py',
            'models/__init__.py',
            'models/sale_order_deals.py',
            'views/deals_views.xml',
            'views/deals_menu.xml',
            'views/commission_views.xml',
            'views/commission_line_views.xml',
            'views/project_unit_views.xml',
            'security/ir.model.access.csv',
        ]
        
        for file_path in required_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                self.log_info(f"Found {file_path}")
            else:
                self.log_error(f"Missing required file: {file_path}")
    
    def validate_manifest(self):
        """Validate __manifest__.py"""
        print("\n🔍 Validating manifest...")
        
        manifest_path = self.module_path / '__manifest__.py'
        if not manifest_path.exists():
            self.log_error("__manifest__.py not found")
            return
            
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check required keys
        required_keys = ['name', 'version', 'depends', 'data']
        for key in required_keys:
            if f"'{key}'" in content or f'"{key}"' in content:
                self.log_info(f"Manifest has '{key}' key")
            else:
                self.log_error(f"Manifest missing '{key}' key")
        
        # Check dependencies
        if 'commission_ax' in content:
            self.log_info("Dependency on commission_ax found")
        else:
            self.log_warning("commission_ax dependency not found - commission features may not work")
            
        if 'sale' in content:
            self.log_info("Dependency on sale module found")
        else:
            self.log_error("sale module dependency missing - critical!")
    
    def validate_menu_actions(self):
        """Validate that all menu action references include module namespace"""
        print("\n🔍 Validating menu action references...")
        
        menu_path = self.module_path / 'views/deals_menu.xml'
        if not menu_path.exists():
            self.log_error("deals_menu.xml not found")
            return
            
        with open(menu_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all action references in menuitem tags
        action_pattern = r'<menuitem[^>]+action="([^"]+)"'
        matches = re.findall(action_pattern, content)
        
        for action_ref in matches:
            if '.' in action_ref:
                # Has module namespace
                if action_ref.startswith('deals_management.'):
                    self.log_info(f"Action reference OK: {action_ref}")
                else:
                    self.log_warning(f"Action reference to external module: {action_ref}")
            else:
                # No module namespace - this is the bug!
                self.log_error(f"Action reference missing module namespace: {action_ref}")
                self.log_error(f"  Should be: deals_management.{action_ref}")
    
    def validate_action_definitions(self):
        """Validate that all referenced actions are defined"""
        print("\n🔍 Validating action definitions...")
        
        # Get actions from menu
        menu_path = self.module_path / 'views/deals_menu.xml'
        views_path = self.module_path / 'views/deals_views.xml'
        
        if not menu_path.exists() or not views_path.exists():
            self.log_error("Required XML files not found")
            return
            
        with open(menu_path, 'r', encoding='utf-8') as f:
            menu_content = f.read()
        
        with open(views_path, 'r', encoding='utf-8') as f:
            views_content = f.read()
            
        # Find all action references
        action_refs = re.findall(r'action="deals_management\.([^"]+)"', menu_content)
        
        # Check if each action is defined
        for action_id in action_refs:
            if f'id="{action_id}"' in views_content:
                self.log_info(f"Action defined: {action_id}")
            else:
                self.log_error(f"Action not defined: {action_id}")
    
    def validate_python_syntax(self):
        """Check Python files for syntax errors"""
        print("\n🔍 Validating Python syntax...")
        
        python_files = [
            'models/sale_order_deals.py',
        ]
        
        for py_file in python_files:
            full_path = self.module_path / py_file
            if not full_path.exists():
                self.log_error(f"Python file not found: {py_file}")
                continue
                
            try:
                import ast
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content, py_file)
                self.log_info(f"Python syntax OK: {py_file}")
            except SyntaxError as e:
                self.log_error(f"Syntax error in {py_file}: {e}")
    
    def validate_xml_basic(self):
        """Basic XML validation (well-formedness check)"""
        print("\n🔍 Validating XML structure...")
        
        xml_files = [
            'views/deals_views.xml',
            'views/deals_menu.xml',
            'views/commission_views.xml',
            'views/commission_line_views.xml',
            'views/project_unit_views.xml',
        ]
        
        for xml_file in xml_files:
            full_path = self.module_path / xml_file
            if not full_path.exists():
                self.log_warning(f"XML file not found: {xml_file}")
                continue
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic checks
            if content.count('<odoo>') != content.count('</odoo>'):
                self.log_error(f"Unbalanced <odoo> tags in {xml_file}")
            elif content.count('<record') != content.count('</record>'):
                self.log_error(f"Unbalanced <record> tags in {xml_file}")
            else:
                self.log_info(f"XML structure looks OK: {xml_file}")
    
    def run_validation(self):
        """Run all validation checks"""
        print("=" * 60)
        print("🚀 Deals Management Module Validator")
        print("=" * 60)
        
        self.validate_file_structure()
        self.validate_manifest()
        self.validate_menu_actions()
        self.validate_action_definitions()
        self.validate_python_syntax()
        self.validate_xml_basic()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Validation Summary")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.info:
            print(f"\n✅ PASSED CHECKS ({len(self.info)}):")
            for info in self.info[:5]:  # Show first 5
                print(f"  {info}")
            if len(self.info) > 5:
                print(f"  ... and {len(self.info) - 5} more")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print("❌ VALIDATION FAILED - Fix errors before deployment")
            return False
        elif self.warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            return True
        else:
            print("✅ VALIDATION PASSED - Module is ready for deployment")
            return True


if __name__ == "__main__":
    # Get module path
    if len(sys.argv) > 1:
        module_path = sys.argv[1]
    else:
        module_path = os.path.dirname(os.path.abspath(__file__))
    
    validator = ModuleValidator(module_path)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)
