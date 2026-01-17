#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final verification script to ensure all module files are correct
and ready for the upgrade.
"""

import os
import re
import sys
from xml.etree import ElementTree as ET

def verify_menu_parent_reference():
    """Verify the menu parent reference is correct."""
    print("\n" + "="*60)
    print("CHECKING: Menu Parent Reference")
    print("="*60)
    
    try:
        with open('views/deal_menu.xml', 'r') as f:
            content = f.read()
        
        # Check for correct parent
        if 'parent="sale.menu_sale_root"' in content:
            print("✓ Correct parent reference: sale.menu_sale_root")
            return True
        elif 'parent="sales_team.menu_sale_root"' in content:
            print("✗ INCORRECT parent reference: sales_team.menu_sale_root")
            print("  (This is the problem causing menus to not appear)")
            return False
        else:
            print("✗ Could not find parent reference")
            return False
    except Exception as e:
        print(f"✗ Error checking menu: {e}")
        return False

def verify_action_definitions():
    """Verify all action definitions exist."""
    print("\n" + "="*60)
    print("CHECKING: Action Definitions")
    print("="*60)
    
    required_actions = {
        'action_deal_report': 'views/deal_report_views.xml',
        'action_deal_dashboard': 'views/deal_dashboard_views.xml',
        'action_deal_report_analytics': 'views/deal_report_analytics.xml',
        'action_deal_report_trends': 'views/deal_report_analytics.xml',
        'action_deal_report_distribution': 'views/deal_report_analytics.xml',
    }
    
    all_found = True
    for action_id, filepath in required_actions.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            if f'id="{action_id}"' in content:
                print(f"✓ {action_id}: Found in {filepath}")
            else:
                print(f"✗ {action_id}: NOT found in {filepath}")
                all_found = False
        else:
            print(f"✗ {filepath}: File not found")
            all_found = False
    
    return all_found

def verify_view_definitions():
    """Verify all view definitions exist."""
    print("\n" + "="*60)
    print("CHECKING: View Definitions")
    print("="*60)
    
    required_views = {
        'view_deal_report_tree': 'views/deal_report_views.xml',
        'view_deal_report_form': 'views/deal_report_views.xml',
        'view_deal_report_search': 'views/deal_report_search.xml',
        'view_deal_dashboard_form': 'views/deal_dashboard_views.xml',
        'view_deal_report_graph': 'views/deal_report_analytics.xml',
        'view_deal_report_graph_line': 'views/deal_report_analytics.xml',
        'view_deal_report_graph_pie': 'views/deal_report_analytics.xml',
        'view_deal_report_pivot': 'views/deal_report_analytics.xml',
        'view_deal_report_kanban': 'views/deal_report_analytics.xml',
    }
    
    all_found = True
    for view_id, filepath in required_views.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            if f'id="{view_id}"' in content:
                print(f"✓ {view_id}: Found in {filepath}")
            else:
                print(f"✗ {view_id}: NOT found in {filepath}")
                all_found = False
        else:
            print(f"✗ {filepath}: File not found")
            all_found = False
    
    return all_found

def verify_xml_structure():
    """Verify all XML files have valid structure."""
    print("\n" + "="*60)
    print("CHECKING: XML File Structure")
    print("="*60)
    
    xml_files = [
        'views/deal_report_views.xml',
        'views/deal_dashboard_views.xml',
        'views/deal_report_analytics.xml',
        'views/deal_report_search.xml',
        'views/deal_menu.xml',
        'data/deal_sequence.xml',
        'data/commission_product.xml',
        'security/deal_report_security.xml',
        'reports/deal_report_templates.xml',
    ]
    
    all_valid = True
    for filepath in xml_files:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            if root.tag == 'odoo':
                print(f"✓ {filepath}: Valid XML structure")
            else:
                print(f"✗ {filepath}: Root tag is '{root.tag}', expected 'odoo'")
                all_valid = False
        except Exception as e:
            print(f"✗ {filepath}: {e}")
            all_valid = False
    
    return all_valid

def verify_model_definitions():
    """Verify all model definitions exist."""
    print("\n" + "="*60)
    print("CHECKING: Python Model Definitions")
    print("="*60)
    
    required_models = {
        'DealReport': ('models/deal_report.py', '_name = \'deal.report\''),
        'DealCommissionLine': ('models/deal_commission_line.py', '_name = \'deal.commission.line\''),
        'DealBillLine': ('models/deal_bill_line.py', '_name = \'deal.bill.line\''),
        'DealDashboard': ('models/deal_dashboard.py', '_name = \'deal.dashboard\''),
    }
    
    all_found = True
    for class_name, (filepath, model_name) in required_models.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            if f'class {class_name}' in content and model_name in content:
                print(f"✓ {class_name}: Found in {filepath}")
            else:
                print(f"✗ {class_name}: NOT properly defined in {filepath}")
                all_found = False
        else:
            print(f"✗ {filepath}: File not found")
            all_found = False
    
    return all_found

def main():
    """Run all verification checks."""
    print("\n" + "="*70)
    print("DEAL REPORT MODULE - FINAL VERIFICATION")
    print("="*70)
    
    checks = [
        ("Menu Parent Reference", verify_menu_parent_reference),
        ("Action Definitions", verify_action_definitions),
        ("View Definitions", verify_view_definitions),
        ("XML Structure", verify_xml_structure),
        ("Model Definitions", verify_model_definitions),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n✗ CRITICAL ERROR in {check_name}: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    print("\n" + "="*70)
    if passed == total:
        print(f"✓ ALL CHECKS PASSED ({passed}/{total})")
        print("\nModule is ready! Upgrade using one of these methods:")
        print("1. Manual: Go to Apps → Deal Report & Commissions → Upgrade")
        print("2. Command: docker exec odoo17_app odoo -d odoo -u deal_report")
        print("3. Script: python upgrade_via_rpc.py")
        return True
    else:
        print(f"✗ SOME CHECKS FAILED ({passed}/{total})")
        print("\nPlease fix the issues above before upgrading.")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success = main()
    sys.exit(0 if success else 1)
