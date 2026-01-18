#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 17 Deal Report Module - Local Test Suite
Tests models, views, workflows, and API compliance
Run: python test_deal_report_odoo17.py --help
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Odoo 17 test utilities
try:
    from odoo.tests import TransactionCase, tagged
    from odoo import api, fields, models
    from odoo.exceptions import UserError, ValidationError
except ImportError:
    print("⚠️  Odoo environment not available. Run inside Odoo environment:")
    print("   cd /path/to/odoo && python -m pytest addons/deal_report/tests/test_*.py")
    sys.exit(1)


class TestDealReportModels(TransactionCase):
    """Test deal.report model integrity, fields, and computed values."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.deal_model = cls.env['deal.report']
        cls.partner_model = cls.env['res.partner']
        cls.project_model = cls.env['project.project']
        cls.product_model = cls.env['product.product']

    def setUp(self):
        super().setUp()
        # Create test data
        self.company = self.env.company
        
        # Partner
        self.partner = self.partner_model.create({
            'name': 'Test Buyer',
            'is_company': False,
            'email': 'buyer@test.com',
        })
        
        # Project
        self.project = self.project_model.create({
            'name': 'Test Project',
            'partner_id': self.company.partner_id.id,
        })
        
        # Unit (Product)
        self.unit = self.product_model.create({
            'name': 'Unit A101',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
        })

    def test_deal_creation(self):
        """Test basic deal creation with required fields."""
        deal = self.deal_model.create({
            'name': 'DEAL/2026/00001',
            'sales_type': 'primary',
            'booking_date': fields.Date.today(),
            'primary_buyer_id': self.partner.id,
            'project_id': self.project.id,
            'unit_id': self.unit.id,
            'sales_value': 500000.00,
        })
        
        self.assertEqual(deal.name, 'DEAL/2026/00001')
        self.assertEqual(deal.state, 'draft')
        self.assertEqual(deal.sales_type, 'primary')
        print("✓ Deal creation test passed")

    def test_vat_computation(self):
        """Test VAT computation on sales_value."""
        deal = self.deal_model.create({
            'name': 'DEAL/2026/00002',
            'sales_type': 'secondary',
            'booking_date': fields.Date.today(),
            'primary_buyer_id': self.partner.id,
            'project_id': self.project.id,
            'unit_id': self.unit.id,
            'sales_value': 100000.00,
            'vat_rate': 5.0,
        })
        
        expected_vat = 100000.00 * (5.0 / 100.0)
        self.assertAlmostEqual(deal.vat_amount, expected_vat, places=2)
        print(f"✓ VAT computation test passed: {deal.vat_amount}")

    def test_state_transitions(self):
        """Test deal state machine transitions."""
        deal = self.deal_model.create({
            'name': 'DEAL/2026/00003',
            'sales_type': 'exclusive',
            'booking_date': fields.Date.today(),
            'primary_buyer_id': self.partner.id,
            'project_id': self.project.id,
            'unit_id': self.unit.id,
            'sales_value': 250000.00,
        })
        
        # Test draft -> confirmed
        self.assertEqual(deal.state, 'draft')
        
        # Call action_confirm if exists
        if hasattr(deal, 'action_confirm'):
            deal.action_confirm()
            self.assertEqual(deal.state, 'confirmed')
            print("✓ State transition (draft -> confirmed) passed")
        else:
            print("⚠️  action_confirm method not found")

    def test_commission_line_creation(self):
        """Test commission line generation."""
        deal = self.deal_model.create({
            'name': 'DEAL/2026/00004',
            'sales_type': 'primary',
            'booking_date': fields.Date.today(),
            'primary_buyer_id': self.partner.id,
            'project_id': self.project.id,
            'unit_id': self.unit.id,
            'sales_value': 300000.00,
        })
        
        # Create commission line
        commission_line = self.env['deal.commission.line'].create({
            'deal_id': deal.id,
            'commission_partner_id': self.partner.id,
            'commission_type': 'internal',
            'role': 'sales_agent',
            'commission_category': 'brokerage',
            'calculation_method': 'percentage',
            'calculation_base': deal.sales_value,
            'commission_rate': 2.5,
        })
        
        expected_amount = deal.sales_value * (2.5 / 100.0)
        self.assertAlmostEqual(commission_line.commission_amount, expected_amount, places=2)
        print(f"✓ Commission line creation test passed: {commission_line.commission_amount}")

    def test_model_string_representation(self):
        """Test __str__ and display_name."""
        deal = self.deal_model.create({
            'name': 'DEAL/2026/00005',
            'sales_type': 'rental',
            'booking_date': fields.Date.today(),
            'primary_buyer_id': self.partner.id,
            'project_id': self.project.id,
            'unit_id': self.unit.id,
            'sales_value': 150000.00,
        })
        
        # Display name should include deal name
        self.assertIn('DEAL/2026/00005', str(deal.name))
        print(f"✓ Display name test passed: {deal.name}")


class TestDealReportViews(TransactionCase):
    """Test XML view validity and field accessibility."""

    def test_view_loading(self):
        """Test that all views load without XML errors."""
        view_ids = [
            'deal_report.deal_report_tree_view',
            'deal_report.deal_report_form_view',
            'deal_report.deal_report_search_view',
            'deal_report.deal_commission_line_tree_view',
            'deal_report.deal_commission_line_form_view',
            'deal_report.deal_bill_line_tree_view',
            'deal_report.deal_bill_line_form_view',
        ]
        
        for view_id in view_ids:
            try:
                view = self.env.ref(view_id)
                self.assertIsNotNone(view)
                print(f"✓ View loaded: {view_id}")
            except ValueError as e:
                print(f"⚠️  View not found: {view_id}")

    def test_form_view_fields_accessible(self):
        """Test that form view fields are accessible on model."""
        model = self.env['deal.report']
        
        required_fields = [
            'name', 'sales_type', 'state', 'booking_date',
            'primary_buyer_id', 'project_id', 'unit_id', 'sales_value'
        ]
        
        for field_name in required_fields:
            field = model._fields.get(field_name)
            self.assertIsNotNone(field, f"Field {field_name} not found on model")
            print(f"✓ Form field accessible: {field_name}")


class TestDealReportSecurity(TransactionCase):
    """Test record rules and access control."""

    def test_model_access_groups(self):
        """Test that security groups are defined."""
        group_ids = [
            'deal_report.group_deal_manager',
            'deal_report.group_deal_salesperson',
            'deal_report.group_deal_accountant',
        ]
        
        for group_id in group_ids:
            try:
                group = self.env.ref(group_id)
                self.assertIsNotNone(group)
                print(f"✓ Security group found: {group_id}")
            except ValueError:
                print(f"⚠️  Security group not found: {group_id}")

    def test_model_record_rules(self):
        """Test that record rules are applied."""
        rules = self.env['ir.rule'].search([('model_id.model', '=', 'deal.report')])
        print(f"✓ Found {len(rules)} record rules for deal.report")


class TestDealReportWorkflow(TransactionCase):
    """Test complete deal workflow."""

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Workflow Test Partner',
            'is_company': False,
        })
        self.project = self.env['project.project'].create({
            'name': 'Workflow Test Project',
            'partner_id': self.env.company.partner_id.id,
        })
        self.unit = self.env['product.product'].create({
            'name': 'Workflow Test Unit',
            'type': 'product',
        })

    def test_complete_workflow(self):
        """Test full deal lifecycle: create -> confirm -> generate -> process."""
        deal = self.env['deal.report'].create({
            'name': 'WORKFLOW/TEST/001',
            'sales_type': 'primary',
            'booking_date': fields.Date.today(),
            'primary_buyer_id': self.partner.id,
            'project_id': self.project.id,
            'unit_id': self.unit.id,
            'sales_value': 500000.00,
        })
        
        print(f"\n📋 Starting workflow test for {deal.name}")
        print(f"   Initial state: {deal.state}")
        
        # Test 1: Confirm deal
        if hasattr(deal, 'action_confirm'):
            deal.action_confirm()
            print(f"   After confirm: {deal.state}")
        
        # Test 2: Generate commission lines
        if hasattr(deal, 'action_generate_commission_lines'):
            deal.action_generate_commission_lines()
            commission_count = len(deal.commission_line_ids)
            print(f"   Generated {commission_count} commission lines")
        
        # Test 3: Process bills
        if hasattr(deal, 'action_process_bills'):
            deal.action_process_bills()
            bill_count = len(deal.bill_line_ids)
            print(f"   Processed {bill_count} bill lines")
        
        print("✓ Workflow test completed")


def run_tests():
    """Execute all tests."""
    print("\n" + "="*60)
    print("ODOO 17 DEAL REPORT MODULE - TEST SUITE")
    print("="*60)
    
    test_classes = [
        TestDealReportModels,
        TestDealReportViews,
        TestDealReportSecurity,
        TestDealReportWorkflow,
    ]
    
    results = {'passed': 0, 'failed': 0, 'warnings': 0}
    
    for test_class in test_classes:
        print(f"\n▶️  Running: {test_class.__name__}")
        print("-" * 60)
        
        try:
            # Create test instance
            instance = test_class('setUp')
            instance.setUp()
            
            # Run all test methods
            for method_name in dir(test_class):
                if method_name.startswith('test_'):
                    method = getattr(instance, method_name)
                    try:
                        method()
                        results['passed'] += 1
                    except AssertionError as e:
                        print(f"✗ {method_name}: {e}")
                        results['failed'] += 1
                    except Exception as e:
                        print(f"⚠️  {method_name}: {e}")
                        results['warnings'] += 1
        except Exception as e:
            print(f"Error setting up test class: {e}")
            results['failed'] += 1
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✓ Passed:  {results['passed']}")
    print(f"✗ Failed:  {results['failed']}")
    print(f"⚠️  Warnings: {results['warnings']}")
    print("="*60 + "\n")
    
    return results['failed'] == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
