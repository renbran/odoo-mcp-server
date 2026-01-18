# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestDealManagement(TransactionCase):
    """Test cases for Deal Management module"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create test partner
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@partner.com',
        })

        # Create test product
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'standard_price': 100.0,
            'list_price': 150.0,
        })

    def test_deal_creation(self):
        """Test creating a deal"""
        deal = self.env['deal.management'].create({
            'name': 'Test Deal',
            'code': 'TEST-001',
            'partner_id': self.partner.id,
            'amount_total': 10000.0,
        })
        self.assertEqual(deal.state, 'draft')
        self.assertTrue(deal.reference.startswith('DEAL/'))

    def test_deal_workflow(self):
        """Test deal workflow transitions"""
        deal = self.env['deal.management'].create({
            'name': 'Test Deal',
            'code': 'TEST-002',
            'partner_id': self.partner.id,
            'amount_total': 10000.0,
        })

        # Test state transitions
        deal.action_confirm()
        self.assertEqual(deal.state, 'qualification')

        deal.action_move_proposal()
        self.assertEqual(deal.state, 'proposal')

        deal.action_move_negotiation()
        self.assertEqual(deal.state, 'negotiation')

        deal.action_won()
        self.assertEqual(deal.state, 'won')
        self.assertIsNotNone(deal.date_won)

    def test_deal_commission(self):
        """Test commission calculation"""
        deal = self.env['deal.management'].create({
            'name': 'Test Deal',
            'code': 'TEST-003',
            'partner_id': self.partner.id,
            'amount_total': 10000.0,
            'commission_rate': 10.0,
        })
        expected_commission = 10000.0 * 10.0 / 100
        self.assertEqual(deal.commission_amount, expected_commission)

    def test_deal_validation(self):
        """Test deal validation"""
        # Test negative amount
        with self.assertRaises(ValidationError):
            self.env['deal.management'].create({
                'name': 'Invalid Deal',
                'code': 'TEST-004',
                'partner_id': self.partner.id,
                'amount_total': -1000.0,
            })

        # Test invalid commission rate
        with self.assertRaises(ValidationError):
            self.env['deal.management'].create({
                'name': 'Invalid Deal',
                'code': 'TEST-005',
                'partner_id': self.partner.id,
                'amount_total': 10000.0,
                'commission_rate': 150.0,
            })

    def test_deal_line_creation(self):
        """Test creating deal lines"""
        deal = self.env['deal.management'].create({
            'name': 'Test Deal',
            'code': 'TEST-006',
            'partner_id': self.partner.id,
            'amount_total': 10000.0,
        })

        line = self.env['deal.line'].create({
            'deal_id': deal.id,
            'product_id': self.product.id,
            'quantity': 5,
            'unit_price': 2000.0,
        })

        self.assertEqual(line.amount_total, 10000.0)
        self.assertEqual(line.deal_id, deal)
