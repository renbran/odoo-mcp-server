#!/usr/bin/env python3
"""
Deals Management Module - Remote Server Inspection & Analysis
Connects to scholarixv2 and performs comprehensive module analysis
"""

import xmlrpc.client
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DealsModuleInspector:
    def __init__(self):
        self.url = os.getenv('ODOO_URL', 'https://erp.sgctech.ai')
        self.db = os.getenv('ODOO_DB', 'scholarixv2')
        self.username = os.getenv('ODOO_USERNAME', 'admin')
        self.password = os.getenv('ODOO_PASSWORD')
        
        self.uid = None
        self.models = None
        self.common = None
        
        self.analysis_results = {
            'module_info': {},
            'installed_modules': [],
            'missing_dependencies': [],
            'model_fields': {},
            'menu_items': [],
            'action_windows': [],
            'views': [],
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'production_readiness': {}
        }
    
    def connect(self):
        """Establish connection to Odoo server"""
        print(f"\n{'='*70}")
        print(f"CONNECTING TO SCHOLARIXV2 REMOTE SERVER")
        print(f"{'='*70}\n")
        
        try:
            # Connect to common endpoint
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            
            # Authenticate
            print(f"🔐 Authenticating to {self.url}...")
            print(f"📊 Database: {self.db}")
            print(f"👤 Username: {self.username}")
            
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            
            if self.uid:
                print(f"✅ Authentication successful! User ID: {self.uid}\n")
                
                # Connect to object endpoint
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
                return True
            else:
                print(f"❌ Authentication failed!")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            self.analysis_results['errors'].append(f"Connection failed: {str(e)}")
            return False
    
    def inspect_module(self):
        """Inspect deals_management module"""
        print(f"{'='*70}")
        print(f"INSPECTING DEALS_MANAGEMENT MODULE")
        print(f"{'='*70}\n")
        
        try:
            # Check if module exists
            module_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'search',
                [[('name', '=', 'deals_management')]]
            )
            
            if not module_ids:
                print("❌ Module 'deals_management' not found on server!")
                self.analysis_results['errors'].append("Module not found on server")
                return False
            
            # Get module details
            module = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'read',
                [module_ids],
                {'fields': ['name', 'state', 'latest_version', 'summary', 'author', 'installed_version', 'dependencies_id']}
            )[0]
            
            self.analysis_results['module_info'] = module
            
            print(f"📦 Module Name: {module['name']}")
            print(f"📊 State: {module['state']}")
            print(f"🔢 Version: {module.get('latest_version', 'N/A')}")
            print(f"👤 Author: {module.get('author', 'N/A')}")
            print(f"📝 Summary: {module.get('summary', 'N/A')}")
            print(f"✅ Installed Version: {module.get('installed_version', 'N/A')}\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Module inspection error: {str(e)}")
            self.analysis_results['errors'].append(f"Module inspection failed: {str(e)}")
            return False
    
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        print(f"{'='*70}")
        print(f"CHECKING MODULE DEPENDENCIES")
        print(f"{'='*70}\n")
        
        required_deps = ['sale', 'commission_ax', 'account', 'project']
        
        try:
            for dep in required_deps:
                module_ids = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'ir.module.module', 'search',
                    [[('name', '=', dep), ('state', '=', 'installed')]]
                )
                
                if module_ids:
                    print(f"✅ {dep} - Installed")
                    self.analysis_results['installed_modules'].append(dep)
                else:
                    print(f"❌ {dep} - NOT INSTALLED!")
                    self.analysis_results['missing_dependencies'].append(dep)
                    self.analysis_results['errors'].append(f"Required dependency '{dep}' not installed")
            
            print()
            return len(self.analysis_results['missing_dependencies']) == 0
            
        except Exception as e:
            print(f"❌ Dependency check error: {str(e)}")
            return False
    
    def inspect_model_fields(self):
        """Inspect sale.order model fields added by deals_management"""
        print(f"{'='*70}")
        print(f"INSPECTING MODEL FIELDS (sale.order)")
        print(f"{'='*70}\n")
        
        deals_fields = [
            'sales_type',
            'buyer_name', 'buyer_email', 'buyer_phone', 'buyer_address',
            'co_buyer_name', 'co_buyer_email',
            'reference_person_name',
            'primary_buyer_id', 'secondary_buyer_id',
            'project_id', 'unit_reference',
            'booking_date', 'estimated_invoice_date',
            'deal_sales_value', 'deal_commission_rate',
            'vat_amount', 'total_without_vat', 'total_with_vat',
            'commission_count', 'bill_count',
            'kyc_document_count', 'booking_form_count', 'passport_count'
        ]
        
        try:
            for field_name in deals_fields:
                try:
                    field_info = self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', 'sale.order'), ('name', '=', field_name)]],
                        {'fields': ['name', 'field_description', 'ttype', 'required', 'readonly']}
                    )
                    
                    if field_info:
                        field = field_info[0]
                        print(f"✅ {field_name} ({field['ttype']}) - {field['field_description']}")
                        self.analysis_results['model_fields'][field_name] = field
                    else:
                        print(f"❌ {field_name} - NOT FOUND!")
                        self.analysis_results['warnings'].append(f"Field '{field_name}' not found on sale.order model")
                        
                except Exception as e:
                    print(f"⚠️  {field_name} - Error checking: {str(e)}")
            
            print()
            return True
            
        except Exception as e:
            print(f"❌ Field inspection error: {str(e)}")
            return False
    
    def inspect_menus(self):
        """Inspect menu structure"""
        print(f"{'='*70}")
        print(f"INSPECTING MENU STRUCTURE")
        print(f"{'='*70}\n")
        
        try:
            # Find menus created by deals_management
            menu_data_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.model.data', 'search',
                [[('module', '=', 'deals_management'), ('model', '=', 'ir.ui.menu')]]
            )
            
            if menu_data_ids:
                menu_data = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'ir.model.data', 'read',
                    [menu_data_ids],
                    {'fields': ['name', 'res_id']}
                )
                
                print(f"📋 Found {len(menu_data)} menu items:\n")
                
                for data in menu_data:
                    menu = self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'ir.ui.menu', 'read',
                        [[data['res_id']]],
                        {'fields': ['name', 'parent_id', 'action', 'sequence']}
                    )
                    
                    if menu:
                        m = menu[0]
                        parent = m['parent_id'][1] if m['parent_id'] else 'Root'
                        action = m['action'] if m['action'] else 'No action'
                        print(f"  ✅ {m['name']} (Parent: {parent}, Action: {action})")
                        self.analysis_results['menu_items'].append(m)
                
                print()
            else:
                print("⚠️  No menu items found for deals_management module")
                self.analysis_results['warnings'].append("No menu items found")
            
            return True
            
        except Exception as e:
            print(f"❌ Menu inspection error: {str(e)}")
            return False
    
    def inspect_actions(self):
        """Inspect action windows"""
        print(f"{'='*70}")
        print(f"INSPECTING ACTION WINDOWS")
        print(f"{'='*70}\n")
        
        try:
            # Find actions created by deals_management
            action_data_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.model.data', 'search',
                [[('module', '=', 'deals_management'), ('model', '=', 'ir.actions.act_window')]]
            )
            
            if action_data_ids:
                action_data = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'ir.model.data', 'read',
                    [action_data_ids],
                    {'fields': ['name', 'res_id']}
                )
                
                print(f"🎬 Found {len(action_data)} action windows:\n")
                
                for data in action_data:
                    action = self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'ir.actions.act_window', 'read',
                        [[data['res_id']]],
                        {'fields': ['name', 'res_model', 'view_mode', 'domain', 'context']}
                    )
                    
                    if action:
                        a = action[0]
                        print(f"  ✅ {a['name']}")
                        print(f"     Model: {a['res_model']}")
                        print(f"     Views: {a['view_mode']}")
                        if a.get('domain'):
                            print(f"     Domain: {a['domain']}")
                        self.analysis_results['action_windows'].append(a)
                        print()
            else:
                print("⚠️  No action windows found for deals_management module")
                self.analysis_results['warnings'].append("No action windows found")
            
            return True
            
        except Exception as e:
            print(f"❌ Action inspection error: {str(e)}")
            return False
    
    def inspect_views(self):
        """Inspect views"""
        print(f"{'='*70}")
        print(f"INSPECTING VIEWS")
        print(f"{'='*70}\n")
        
        try:
            # Find views created by deals_management
            view_data_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.model.data', 'search',
                [[('module', '=', 'deals_management'), ('model', '=', 'ir.ui.view')]]
            )
            
            if view_data_ids:
                view_data = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'ir.model.data', 'read',
                    [view_data_ids],
                    {'fields': ['name', 'res_id']}
                )
                
                print(f"👁️  Found {len(view_data)} views:\n")
                
                for data in view_data:
                    view = self.models.execute_kw(
                        self.db, self.uid, self.password,
                        'ir.ui.view', 'read',
                        [[data['res_id']]],
                        {'fields': ['name', 'model', 'type', 'inherit_id', 'active']}
                    )
                    
                    if view:
                        v = view[0]
                        inheritance = f" (Inherits: {v['inherit_id'][1]})" if v['inherit_id'] else ""
                        status = "✅" if v['active'] else "❌"
                        print(f"  {status} {v['name']} - {v['type']}{inheritance}")
                        self.analysis_results['views'].append(v)
            else:
                print("⚠️  No views found for deals_management module")
                self.analysis_results['warnings'].append("No views found")
            
            print()
            return True
            
        except Exception as e:
            print(f"❌ View inspection error: {str(e)}")
            return False
    
    def analyze_production_readiness(self):
        """Analyze production readiness"""
        print(f"\n{'='*70}")
        print(f"PRODUCTION READINESS ANALYSIS")
        print(f"{'='*70}\n")
        
        score = 0
        max_score = 10
        
        # 1. Module installed
        if self.analysis_results['module_info'].get('state') == 'installed':
            print("✅ Module is installed")
            score += 1
        else:
            print(f"❌ Module state: {self.analysis_results['module_info'].get('state', 'unknown')}")
            self.analysis_results['recommendations'].append("Install the module")
        
        # 2. Dependencies met
        if len(self.analysis_results['missing_dependencies']) == 0:
            print("✅ All dependencies are installed")
            score += 1
        else:
            print(f"❌ Missing dependencies: {', '.join(self.analysis_results['missing_dependencies'])}")
            self.analysis_results['recommendations'].append("Install missing dependencies")
        
        # 3. Fields present
        expected_fields = 18
        found_fields = len(self.analysis_results['model_fields'])
        if found_fields >= expected_fields:
            print(f"✅ All model fields present ({found_fields}/{expected_fields})")
            score += 2
        else:
            print(f"⚠️  Some fields missing ({found_fields}/{expected_fields})")
            score += 1
            self.analysis_results['recommendations'].append("Verify all model fields are properly defined")
        
        # 4. Menus created
        if len(self.analysis_results['menu_items']) >= 10:
            print(f"✅ Menu structure complete ({len(self.analysis_results['menu_items'])} items)")
            score += 2
        else:
            print(f"⚠️  Limited menu items ({len(self.analysis_results['menu_items'])})")
            score += 1
            self.analysis_results['recommendations'].append("Verify all menu items are created")
        
        # 5. Actions defined
        if len(self.analysis_results['action_windows']) >= 10:
            print(f"✅ Action windows complete ({len(self.analysis_results['action_windows'])})")
            score += 2
        else:
            print(f"⚠️  Limited actions ({len(self.analysis_results['action_windows'])})")
            score += 1
            self.analysis_results['recommendations'].append("Verify all action windows are defined")
        
        # 6. Views created
        if len(self.analysis_results['views']) >= 3:
            print(f"✅ Views created ({len(self.analysis_results['views'])})")
            score += 1
        else:
            print(f"⚠️  Limited views ({len(self.analysis_results['views'])})")
            self.analysis_results['recommendations'].append("Create additional views if needed")
        
        # 7. No critical errors
        if len(self.analysis_results['errors']) == 0:
            print("✅ No critical errors detected")
            score += 1
        else:
            print(f"❌ {len(self.analysis_results['errors'])} error(s) found")
            self.analysis_results['recommendations'].append("Fix all critical errors")
        
        self.analysis_results['production_readiness'] = {
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'status': 'Production Ready' if score >= 8 else 'Needs Work' if score >= 5 else 'Not Ready'
        }
        
        print(f"\n📊 Production Readiness Score: {score}/{max_score} ({(score/max_score)*100:.0f}%)")
        print(f"🎯 Status: {self.analysis_results['production_readiness']['status']}\n")
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print(f"\n{'='*70}")
        print(f"COMPREHENSIVE ANALYSIS REPORT")
        print(f"{'='*70}\n")
        
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Module: deals_management")
        print(f"State: {self.analysis_results['module_info'].get('state', 'unknown')}")
        print(f"Version: {self.analysis_results['module_info'].get('latest_version', 'N/A')}")
        print(f"Dependencies Met: {len(self.analysis_results['installed_modules'])}/4")
        print(f"Fields Found: {len(self.analysis_results['model_fields'])}")
        print(f"Menus Created: {len(self.analysis_results['menu_items'])}")
        print(f"Actions Defined: {len(self.analysis_results['action_windows'])}")
        print(f"Views Created: {len(self.analysis_results['views'])}")
        print(f"Errors: {len(self.analysis_results['errors'])}")
        print(f"Warnings: {len(self.analysis_results['warnings'])}")
        
        if self.analysis_results['errors']:
            print(f"\n{'='*70}")
            print("CRITICAL ERRORS")
            print("=" * 70)
            for i, error in enumerate(self.analysis_results['errors'], 1):
                print(f"{i}. {error}")
        
        if self.analysis_results['warnings']:
            print(f"\n{'='*70}")
            print("WARNINGS")
            print("=" * 70)
            for i, warning in enumerate(self.analysis_results['warnings'], 1):
                print(f"{i}. {warning}")
        
        if self.analysis_results['recommendations']:
            print(f"\n{'='*70}")
            print("RECOMMENDATIONS")
            print("=" * 70)
            for i, rec in enumerate(self.analysis_results['recommendations'], 1):
                print(f"{i}. {rec}")
        
        print(f"\n{'='*70}")
        print("PRODUCTION READINESS")
        print("=" * 70)
        pr = self.analysis_results['production_readiness']
        print(f"Score: {pr['score']}/{pr['max_score']} ({pr['percentage']:.0f}%)")
        print(f"Status: {pr['status']}")
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"deals_module_analysis_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("DEALS MANAGEMENT MODULE - REMOTE ANALYSIS REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Server: {self.url}\n")
            f.write(f"Database: {self.db}\n\n")
            
            f.write("SUMMARY\n")
            f.write("=" * 70 + "\n")
            f.write(f"Module State: {self.analysis_results['module_info'].get('state', 'unknown')}\n")
            f.write(f"Version: {self.analysis_results['module_info'].get('latest_version', 'N/A')}\n")
            f.write(f"Dependencies: {len(self.analysis_results['installed_modules'])}/4 installed\n")
            f.write(f"Model Fields: {len(self.analysis_results['model_fields'])} found\n")
            f.write(f"Menu Items: {len(self.analysis_results['menu_items'])} created\n")
            f.write(f"Action Windows: {len(self.analysis_results['action_windows'])} defined\n")
            f.write(f"Views: {len(self.analysis_results['views'])} created\n\n")
            
            if self.analysis_results['errors']:
                f.write("\nCRITICAL ERRORS\n")
                f.write("=" * 70 + "\n")
                for error in self.analysis_results['errors']:
                    f.write(f"- {error}\n")
            
            if self.analysis_results['warnings']:
                f.write("\nWARNINGS\n")
                f.write("=" * 70 + "\n")
                for warning in self.analysis_results['warnings']:
                    f.write(f"- {warning}\n")
            
            if self.analysis_results['recommendations']:
                f.write("\nRECOMMENDATIONS\n")
                f.write("=" * 70 + "\n")
                for rec in self.analysis_results['recommendations']:
                    f.write(f"- {rec}\n")
            
            f.write(f"\nPRODUCTION READINESS\n")
            f.write("=" * 70 + "\n")
            f.write(f"Score: {pr['score']}/{pr['max_score']} ({pr['percentage']:.0f}%)\n")
            f.write(f"Status: {pr['status']}\n")
        
        print(f"\n📄 Report saved to: {report_file}")
        print("=" * 70)
    
    def run_analysis(self):
        """Run complete analysis"""
        if not self.connect():
            return False
        
        self.inspect_module()
        self.check_dependencies()
        self.inspect_model_fields()
        self.inspect_menus()
        self.inspect_actions()
        self.inspect_views()
        self.analyze_production_readiness()
        self.generate_report()
        
        return True


if __name__ == "__main__":
    inspector = DealsModuleInspector()
    inspector.run_analysis()
