#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Testing Script for Property Portal Syndication Module
Simulates customer personas and tests all workflows
"""

import requests
import json
import time
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class PortalSyndicationTester:
    def __init__(self, base_url, db_name, username, password):
        self.base_url = base_url.rstrip('/')
        self.db_name = db_name
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.uid = None
        self.test_results = []
        
    def print_header(self, text):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")
    
    def print_test(self, name, status, message=""):
        icons = {
            "PASS": f"{Colors.GREEN}✓{Colors.END}",
            "FAIL": f"{Colors.RED}✗{Colors.END}",
            "WARN": f"{Colors.YELLOW}⚠{Colors.END}",
            "INFO": f"{Colors.BLUE}ℹ{Colors.END}"
        }
        icon = icons.get(status, "")
        color = getattr(Colors, status.split('_')[0] if '_' in status else 'END', Colors.END)
        print(f"{icon} {color}{name}{Colors.END}")
        if message:
            print(f"   {message}")
        
        self.test_results.append({
            "name": name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate(self):
        """Authenticate with Odoo XML-RPC"""
        self.print_header("AUTHENTICATION TEST")
        
        try:
            import xmlrpc.client
            
            common = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db_name, self.username, self.password, {})
            
            if self.uid:
                self.print_test("Authentication", "PASS", f"Logged in as UID: {self.uid}")
                return True
            else:
                self.print_test("Authentication", "FAIL", "Invalid credentials")
                return False
                
        except Exception as e:
            self.print_test("Authentication", "FAIL", str(e))
            return False
    
    def test_module_installed(self):
        """Check if module is installed"""
        self.print_header("MODULE INSTALLATION TEST")
        
        try:
            import xmlrpc.client
            models = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
            
            module_id = models.execute_kw(
                self.db_name, self.uid, self.password,
                'ir.module.module', 'search',
                [[['name', '=', 'rental_portal_syndication']]]
            )
            
            if module_id:
                module_data = models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'ir.module.module', 'read',
                    [module_id], {'fields': ['state', 'latest_version']}
                )
                
                if module_data and module_data[0]['state'] == 'installed':
                    self.print_test("Module Installation", "PASS", 
                                  f"Version: {module_data[0].get('latest_version', 'unknown')}")
                    return True
                else:
                    self.print_test("Module Installation", "FAIL", 
                                  f"State: {module_data[0].get('state', 'unknown')}")
                    return False
            else:
                self.print_test("Module Installation", "FAIL", "Module not found")
                return False
                
        except Exception as e:
            self.print_test("Module Installation", "FAIL", str(e))
            return False
    
    def test_models_exist(self):
        """Verify all models are created"""
        self.print_header("MODEL EXISTENCE TEST")
        
        models_to_check = [
            'portal.connector',
            'portal.lead',
            'portal.sync.log',
            'property.portal.line',
            'xml.feed.config'
        ]
        
        try:
            import xmlrpc.client
            models = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
            
            all_passed = True
            for model_name in models_to_check:
                try:
                    # Try to search the model (returns empty list if exists)
                    models.execute_kw(
                        self.db_name, self.uid, self.password,
                        model_name, 'search',
                        [[]], {'limit': 1}
                    )
                    self.print_test(f"Model: {model_name}", "PASS")
                except Exception as e:
                    self.print_test(f"Model: {model_name}", "FAIL", str(e))
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.print_test("Model Check", "FAIL", str(e))
            return False
    
    def test_security_groups(self):
        """Test security groups are created"""
        self.print_header("SECURITY GROUPS TEST")
        
        groups_to_check = [
            'rental_portal_syndication.group_portal_user',
            'rental_portal_syndication.group_portal_manager',
            'rental_portal_syndication.group_portal_admin'
        ]
        
        try:
            import xmlrpc.client
            models = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
            
            all_passed = True
            for group_xml_id in groups_to_check:
                try:
                    group_id = models.execute_kw(
                        self.db_name, self.uid, self.password,
                        'ir.model.data', 'xmlid_to_res_id',
                        [group_xml_id]
                    )
                    if group_id:
                        self.print_test(f"Group: {group_xml_id.split('.')[-1]}", "PASS")
                    else:
                        self.print_test(f"Group: {group_xml_id.split('.')[-1]}", "FAIL", "Not found")
                        all_passed = False
                except Exception as e:
                    self.print_test(f"Group: {group_xml_id.split('.')[-1]}", "FAIL", str(e))
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.print_test("Security Groups", "FAIL", str(e))
            return False
    
    def test_sarah_workflow(self):
        """Test Persona: Sarah the Property Manager"""
        self.print_header("PERSONA TEST: SARAH (Property Manager)")
        
        print(f"{Colors.BLUE}Scenario: Sarah wants to list properties on Bayut{Colors.END}\n")
        
        try:
            import xmlrpc.client
            models = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
            
            # Step 1: Create portal connector
            try:
                connector_id = models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.connector', 'create',
                    [{
                        'name': 'Test Bayut Connector',
                        'code': 'bayut',
                        'sync_frequency': 'manual',
                    }]
                )
                self.print_test("Step 1: Create Bayut connector", "PASS", f"ID: {connector_id}")
            except Exception as e:
                self.print_test("Step 1: Create Bayut connector", "FAIL", str(e))
                return False
            
            # Step 2: Verify token generation
            try:
                connector_data = models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.connector', 'read',
                    [connector_id], {'fields': ['xml_feed_token', 'xml_feed_url']}
                )
                
                token = connector_data[0].get('xml_feed_token')
                feed_url = connector_data[0].get('xml_feed_url')
                
                if token and len(token) >= 32:
                    self.print_test("Step 2: Token generation", "PASS", f"Length: {len(token)}")
                else:
                    self.print_test("Step 2: Token generation", "FAIL", "Token too short")
                
                if feed_url:
                    self.print_test("Step 3: Feed URL generation", "PASS", feed_url[:50] + "...")
                else:
                    self.print_test("Step 3: Feed URL generation", "FAIL", "No URL generated")
                    
            except Exception as e:
                self.print_test("Step 2-3: Token/URL check", "FAIL", str(e))
            
            # Step 4: Test feed URL access (HTTP)
            try:
                response = requests.get(feed_url, timeout=5)
                if response.status_code == 200:
                    if 'not_implemented' in response.text:
                        self.print_test("Step 4: Feed URL access", "WARN", 
                                      "Accessible but returns 'not_implemented' (expected)")
                    else:
                        self.print_test("Step 4: Feed URL access", "PASS", "Returns valid XML")
                else:
                    self.print_test("Step 4: Feed URL access", "FAIL", 
                                  f"HTTP {response.status_code}")
            except Exception as e:
                self.print_test("Step 4: Feed URL access", "FAIL", str(e))
            
            # Step 5: Find a property to list
            try:
                property_ids = models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'property.details', 'search',
                    [[]], {'limit': 1}
                )
                
                if property_ids:
                    property_id = property_ids[0]
                    self.print_test("Step 5: Find property", "PASS", f"Property ID: {property_id}")
                    
                    # Step 6: Add property to portal
                    try:
                        line_id = models.execute_kw(
                            self.db_name, self.uid, self.password,
                            'property.portal.line', 'create',
                            [{
                                'property_id': property_id,
                                'portal_id': connector_id,
                                'status': 'published',
                            }]
                        )
                        self.print_test("Step 6: Add property to portal", "PASS", f"Line ID: {line_id}")
                        
                        # Cleanup
                        models.execute_kw(
                            self.db_name, self.uid, self.password,
                            'property.portal.line', 'unlink',
                            [[line_id]]
                        )
                        
                    except Exception as e:
                        self.print_test("Step 6: Add property to portal", "FAIL", str(e))
                        
                else:
                    self.print_test("Step 5: Find property", "WARN", "No properties in database")
                    self.print_test("Step 6: Add property to portal", "WARN", "Skipped - no properties")
                    
            except Exception as e:
                self.print_test("Step 5-6: Property listing", "FAIL", str(e))
            
            # Cleanup connector
            try:
                models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.connector', 'unlink',
                    [[connector_id]]
                )
            except:
                pass
            
            return True
            
        except Exception as e:
            self.print_test("Sarah's workflow", "FAIL", str(e))
            return False
    
    def test_mike_workflow(self):
        """Test Persona: Mike the Sales Agent"""
        self.print_header("PERSONA TEST: MIKE (Sales Agent)")
        
        print(f"{Colors.BLUE}Scenario: Mike manages leads from portals{Colors.END}\n")
        
        try:
            import xmlrpc.client
            models = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
            
            # Setup: Create connector
            connector_id = models.execute_kw(
                self.db_name, self.uid, self.password,
                'portal.connector', 'create',
                [{'name': 'Test Connector', 'code': 'dubizzle', 'sync_frequency': 'manual'}]
            )
            
            # Step 1: Create a lead manually
            try:
                lead_id = models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.lead', 'create',
                    [{
                        'name': 'John Smith',
                        'email': 'john@example.com',
                        'phone': '+971501234567',
                        'portal_id': connector_id,
                        'state': 'new',
                    }]
                )
                self.print_test("Step 1: Create lead", "PASS", f"Lead ID: {lead_id}")
            except Exception as e:
                self.print_test("Step 1: Create lead", "FAIL", str(e))
                return False
            
            # Step 2: Mark as contacted
            try:
                models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.lead', 'action_mark_contacted',
                    [[lead_id]]
                )
                
                lead_data = models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.lead', 'read',
                    [lead_id], {'fields': ['state']}
                )
                
                if lead_data[0]['state'] == 'contacted':
                    self.print_test("Step 2: Mark contacted", "PASS")
                else:
                    self.print_test("Step 2: Mark contacted", "FAIL", 
                                  f"State: {lead_data[0]['state']}")
            except Exception as e:
                self.print_test("Step 2: Mark contacted", "FAIL", str(e))
            
            # Step 3: Mark as qualified
            try:
                models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.lead', 'action_mark_qualified',
                    [[lead_id]]
                )
                
                lead_data = models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.lead', 'read',
                    [lead_id], {'fields': ['state']}
                )
                
                if lead_data[0]['state'] == 'qualified':
                    self.print_test("Step 3: Mark qualified", "PASS")
                else:
                    self.print_test("Step 3: Mark qualified", "FAIL", 
                                  f"State: {lead_data[0]['state']}")
            except Exception as e:
                self.print_test("Step 3: Mark qualified", "FAIL", str(e))
            
            # Step 4: Mark as won
            try:
                models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.lead', 'action_mark_won',
                    [[lead_id]]
                )
                
                lead_data = models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.lead', 'read',
                    [lead_id], {'fields': ['state']}
                )
                
                if lead_data[0]['state'] == 'won':
                    self.print_test("Step 4: Mark won", "PASS")
                else:
                    self.print_test("Step 4: Mark won", "FAIL", 
                                  f"State: {lead_data[0]['state']}")
            except Exception as e:
                self.print_test("Step 4: Mark won", "FAIL", str(e))
            
            # Cleanup
            try:
                models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.lead', 'unlink',
                    [[lead_id]]
                )
                models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.connector', 'unlink',
                    [[connector_id]]
                )
            except:
                pass
            
            return True
            
        except Exception as e:
            self.print_test("Mike's workflow", "FAIL", str(e))
            return False
    
    def test_security_vulnerabilities(self):
        """Test for known security vulnerabilities"""
        self.print_header("SECURITY VULNERABILITY TEST")
        
        try:
            import xmlrpc.client
            models = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
            
            # Create a test connector
            connector_id = models.execute_kw(
                self.db_name, self.uid, self.password,
                'portal.connector', 'create',
                [{'name': 'Security Test', 'code': 'bayut', 'sync_frequency': 'manual'}]
            )
            
            connector_data = models.execute_kw(
                self.db_name, self.uid, self.password,
                'portal.connector', 'read',
                [connector_id], {'fields': ['xml_feed_token', 'xml_feed_url']}
            )
            
            token = connector_data[0]['xml_feed_token']
            feed_url = connector_data[0]['xml_feed_url']
            
            # Test 1: Access without token
            try:
                url_without_token = feed_url.split('?')[0]
                response = requests.get(url_without_token, timeout=5)
                if response.status_code == 401:
                    self.print_test("Test 1: Unauthorized access blocked", "PASS")
                else:
                    self.print_test("Test 1: Unauthorized access blocked", "FAIL", 
                                  f"Got HTTP {response.status_code} instead of 401")
            except Exception as e:
                self.print_test("Test 1: Unauthorized access", "FAIL", str(e))
            
            # Test 2: Access with wrong token
            try:
                url_wrong_token = f"{url_without_token}?token=wrongtoken123456"
                response = requests.get(url_wrong_token, timeout=5)
                if response.status_code == 401:
                    self.print_test("Test 2: Wrong token rejected", "PASS")
                else:
                    self.print_test("Test 2: Wrong token rejected", "FAIL", 
                                  f"Got HTTP {response.status_code} instead of 401")
            except Exception as e:
                self.print_test("Test 2: Wrong token check", "FAIL", str(e))
            
            # Test 3: Check if token is in message_ids (CRITICAL SECURITY FLAW)
            try:
                messages = models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'mail.message', 'search_read',
                    [[['model', '=', 'portal.connector'], ['res_id', '=', connector_id]]],
                    {'fields': ['body'], 'limit': 10}
                )
                
                token_in_messages = any(token in msg.get('body', '') for msg in messages if msg.get('body'))
                
                if token_in_messages:
                    self.print_test("Test 3: Token exposure in chatter", "FAIL", 
                                  "🔴 CRITICAL: Token visible in activity log!")
                else:
                    self.print_test("Test 3: Token exposure in chatter", "PASS", 
                                  "Token not found in messages")
            except Exception as e:
                self.print_test("Test 3: Token exposure check", "WARN", str(e))
            
            # Cleanup
            try:
                models.execute_kw(
                    self.db_name, self.uid, self.password,
                    'portal.connector', 'unlink',
                    [[connector_id]]
                )
            except:
                pass
            
        except Exception as e:
            self.print_test("Security tests", "FAIL", str(e))
    
    def generate_report(self):
        """Generate final test report"""
        self.print_header("FINAL TEST REPORT")
        
        total = len(self.test_results)
        passed = sum(1 for t in self.test_results if t['status'] == 'PASS')
        failed = sum(1 for t in self.test_results if t['status'] == 'FAIL')
        warned = sum(1 for t in self.test_results if t['status'] == 'WARN')
        
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {warned}{Colors.END}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.END}")
        
        if success_rate >= 80:
            print(f"\n{Colors.GREEN}✓ Module is working well!{Colors.END}")
        elif success_rate >= 60:
            print(f"\n{Colors.YELLOW}⚠ Module has some issues{Colors.END}")
        else:
            print(f"\n{Colors.RED}✗ Module has significant problems{Colors.END}")
        
        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                    'warned': warned,
                    'success_rate': success_rate
                },
                'tests': self.test_results
            }, f, indent=2)
        
        print(f"\n{Colors.BLUE}Report saved to: {report_file}{Colors.END}")
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                  PROPERTY PORTAL SYNDICATION TEST SUITE                     ║")
        print("║                          Comprehensive Testing                               ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        if not self.authenticate():
            print(f"\n{Colors.RED}Authentication failed. Cannot proceed with tests.{Colors.END}")
            return
        
        self.test_module_installed()
        self.test_models_exist()
        self.test_security_groups()
        self.test_sarah_workflow()
        self.test_mike_workflow()
        self.test_security_vulnerabilities()
        
        self.generate_report()


if __name__ == "__main__":
    import sys
    
    # Configuration
    BASE_URL = "http://localhost:8069"  # Change this
    DB_NAME = "scholarixv2"             # Change this
    USERNAME = "admin"                  # Change this
    PASSWORD = "admin"                  # Change this
    
    # Allow overrides from command line
    if len(sys.argv) >= 5:
        BASE_URL = sys.argv[1]
        DB_NAME = sys.argv[2]
        USERNAME = sys.argv[3]
        PASSWORD = sys.argv[4]
    
    print(f"\n{Colors.BLUE}Configuration:{Colors.END}")
    print(f"  URL: {BASE_URL}")
    print(f"  Database: {DB_NAME}")
    print(f"  User: {USERNAME}")
    
    tester = PortalSyndicationTester(BASE_URL, DB_NAME, USERNAME, PASSWORD)
    tester.run_all_tests()
