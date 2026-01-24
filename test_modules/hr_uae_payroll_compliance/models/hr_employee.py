# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
from datetime import date, timedelta


class HrEmployee(models.Model):
    """
    Extend hr.employee with UAE Labor Law compliance fields
    Includes WPS integration requirements and document tracking
    """
    _inherit = 'hr.employee'

    # ========== WPS COMPLIANCE FIELDS ==========
    # MOHRE Person ID - Required for WPS submission
    x_mohre_person_id = fields.Char(
        string='MOHRE Person ID',
        size=14,
        help='14-digit MOHRE Person ID required for WPS (Wage Protection System) compliance',
        tracking=True,
    )
    
    # ========== EMIRATES ID TRACKING ==========
    x_emirates_id = fields.Char(
        string='Emirates ID',
        size=18,  # Format: 784-YYYY-NNNNNNN-N (with dashes)
        help='15-digit Emirates ID (format: 784-YYYY-NNNNNNN-N)',
        tracking=True,
    )
    
    x_emirates_id_expiry = fields.Date(
        string='Emirates ID Expiry',
        help='Emirates ID expiration date. System will alert 60 days before expiry',
        tracking=True,
    )
    
    x_days_to_emirates_expiry = fields.Integer(
        string='Days to Emirates ID Expiry',
        compute='_compute_days_to_emirates_expiry',
        store=True,
        help='Calculated days remaining until Emirates ID expires',
    )
    
    x_emirates_id_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring_soon', 'Expiring Soon (< 60 days)'),
        ('expired', 'Expired'),
        ('not_set', 'Not Set'),
    ], string='Emirates ID Status', compute='_compute_emirates_id_status', store=True)
    
    # ========== VISA AND IMMIGRATION TRACKING ==========
    x_visa_number = fields.Char(
        string='Visa Number',
        help='UAE Residence Visa number',
        tracking=True,
    )
    
    x_visa_expiry = fields.Date(
        string='Visa Expiry Date',
        help='Residence visa expiration date',
        tracking=True,
    )
    
    x_days_to_visa_expiry = fields.Integer(
        string='Days to Visa Expiry',
        compute='_compute_days_to_visa_expiry',
        store=True,
    )
    
    x_visa_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring_soon', 'Expiring Soon (< 60 days)'),
        ('expired', 'Expired'),
        ('not_set', 'Not Set'),
    ], string='Visa Status', compute='_compute_visa_status', store=True)
    
    # ========== PASSPORT TRACKING ==========
    x_passport_expiry = fields.Date(
        string='Passport Expiry Date',
        help='Passport expiration date',
        tracking=True,
    )
    
    x_days_to_passport_expiry = fields.Integer(
        string='Days to Passport Expiry',
        compute='_compute_days_to_passport_expiry',
        store=True,
    )
    
    # ========== LABOR CARD TRACKING ==========
    x_labor_card_number = fields.Char(
        string='Labor Card Number',
        help='UAE Labor Card number issued by MOHRE',
        tracking=True,
    )
    
    x_labor_card_expiry = fields.Date(
        string='Labor Card Expiry',
        help='Labor card expiration date',
        tracking=True,
    )
    
    x_days_to_labor_card_expiry = fields.Integer(
        string='Days to Labor Card Expiry',
        compute='_compute_days_to_labor_card_expiry',
        store=True,
    )
    
    # ========== WPS BANKING FIELDS ==========
    x_bank_routing_code = fields.Char(
        string='Bank Routing Code',
        help='UAE Central Bank routing code (9 digits)',
        size=9,
        tracking=True,
    )
    
    x_wps_agent_id = fields.Char(
        string='WPS Exchange House Agent ID',
        help='Exchange house agent ID for WPS payments (if applicable)',
        tracking=True,
    )
    
    x_payment_method = fields.Selection([
        ('bank_transfer', 'Bank Transfer'),
        ('exchange_house', 'Exchange House'),
        ('salary_card', 'Salary Card'),
    ], string='Salary Payment Method',
        default='bank_transfer',
        required=True,
        help='Method of salary payment as per WPS requirements',
        tracking=True,
    )
    
    x_iban_number = fields.Char(
        string='IBAN Number',
        help='International Bank Account Number (UAE format: AE + 21 digits)',
        size=23,
        tracking=True,
    )
    
    # ========== GPSSA FIELDS (UAE NATIONALS) ==========
    x_gpssa_registered = fields.Boolean(
        string='GPSSA Registered',
        default=False,
        help='Check if employee is registered with General Pension and Social Security Authority (UAE Nationals only)',
        tracking=True,
    )
    
    x_gpssa_number = fields.Char(
        string='GPSSA Number',
        help='General Pension and Social Security Authority registration number',
        tracking=True,
    )
    
    x_is_uae_national = fields.Boolean(
        string='UAE National',
        default=False,
        help='Indicate if employee is a UAE national (required for GPSSA)',
        tracking=True,
    )
    
    # ========== COMPLIANCE OVERVIEW ==========
    x_wps_ready = fields.Boolean(
        string='WPS Ready',
        compute='_compute_wps_ready',
        store=True,
        help='Indicates if employee has all required fields for WPS submission',
    )
    
    x_compliance_score = fields.Integer(
        string='Compliance Score',
        compute='_compute_compliance_score',
        store=True,
        help='Overall compliance score (0-100) based on required fields completion',
    )
    
    # ========== COMPUTED FIELDS ==========
    
    @api.depends('x_emirates_id_expiry')
    def _compute_days_to_emirates_expiry(self):
        """Calculate days remaining until Emirates ID expires"""
        for employee in self:
            if employee.x_emirates_id_expiry:
                delta = employee.x_emirates_id_expiry - date.today()
                employee.x_days_to_emirates_expiry = delta.days
            else:
                employee.x_days_to_emirates_expiry = 0
    
    @api.depends('x_emirates_id_expiry', 'x_days_to_emirates_expiry')
    def _compute_emirates_id_status(self):
        """Determine Emirates ID status based on expiry date"""
        for employee in self:
            if not employee.x_emirates_id_expiry:
                employee.x_emirates_id_status = 'not_set'
            elif employee.x_days_to_emirates_expiry < 0:
                employee.x_emirates_id_status = 'expired'
            elif employee.x_days_to_emirates_expiry <= 60:
                employee.x_emirates_id_status = 'expiring_soon'
            else:
                employee.x_emirates_id_status = 'valid'
    
    @api.depends('x_visa_expiry')
    def _compute_days_to_visa_expiry(self):
        """Calculate days remaining until visa expires"""
        for employee in self:
            if employee.x_visa_expiry:
                delta = employee.x_visa_expiry - date.today()
                employee.x_days_to_visa_expiry = delta.days
            else:
                employee.x_days_to_visa_expiry = 0
    
    @api.depends('x_visa_expiry', 'x_days_to_visa_expiry')
    def _compute_visa_status(self):
        """Determine visa status based on expiry date"""
        for employee in self:
            if not employee.x_visa_expiry:
                employee.x_visa_status = 'not_set'
            elif employee.x_days_to_visa_expiry < 0:
                employee.x_visa_status = 'expired'
            elif employee.x_days_to_visa_expiry <= 60:
                employee.x_visa_status = 'expiring_soon'
            else:
                employee.x_visa_status = 'valid'
    
    @api.depends('x_passport_expiry')
    def _compute_days_to_passport_expiry(self):
        """Calculate days remaining until passport expires"""
        for employee in self:
            if employee.x_passport_expiry:
                delta = employee.x_passport_expiry - date.today()
                employee.x_days_to_passport_expiry = delta.days
            else:
                employee.x_days_to_passport_expiry = 0
    
    @api.depends('x_labor_card_expiry')
    def _compute_days_to_labor_card_expiry(self):
        """Calculate days remaining until labor card expires"""
        for employee in self:
            if employee.x_labor_card_expiry:
                delta = employee.x_labor_card_expiry - date.today()
                employee.x_days_to_labor_card_expiry = delta.days
            else:
                employee.x_days_to_labor_card_expiry = 0
    
    @api.depends('x_mohre_person_id', 'x_emirates_id', 'x_iban_number', 
                 'x_bank_routing_code', 'x_payment_method')
    def _compute_wps_ready(self):
        """
        Check if employee has all required fields for WPS submission
        WPS Requirements:
        - MOHRE Person ID (14 digits)
        - Valid payment method
        - Banking details (IBAN or Exchange House Agent ID)
        """
        for employee in self:
            has_mohre_id = bool(employee.x_mohre_person_id and len(employee.x_mohre_person_id) == 14)
            has_payment_method = bool(employee.x_payment_method)
            
            # Check banking details based on payment method
            if employee.x_payment_method == 'bank_transfer':
                has_banking = bool(employee.x_iban_number and employee.x_bank_routing_code)
            elif employee.x_payment_method == 'exchange_house':
                has_banking = bool(employee.x_wps_agent_id)
            else:
                has_banking = bool(employee.x_iban_number)
            
            employee.x_wps_ready = has_mohre_id and has_payment_method and has_banking
    
    @api.depends('x_mohre_person_id', 'x_emirates_id', 'x_emirates_id_expiry',
                 'x_visa_number', 'x_visa_expiry', 'x_iban_number', 
                 'x_labor_card_number', 'x_labor_card_expiry')
    def _compute_compliance_score(self):
        """
        Calculate overall compliance score (0-100)
        Based on completion of required UAE compliance fields
        """
        for employee in self:
            score = 0
            total_fields = 8
            
            # MOHRE Person ID (critical for WPS) - 20 points
            if employee.x_mohre_person_id and len(employee.x_mohre_person_id) == 14:
                score += 20
            
            # Emirates ID - 15 points
            if employee.x_emirates_id:
                score += 10
                if employee.x_emirates_id_expiry and employee.x_emirates_id_status == 'valid':
                    score += 5
            
            # Visa - 15 points
            if employee.x_visa_number:
                score += 10
                if employee.x_visa_expiry and employee.x_visa_status == 'valid':
                    score += 5
            
            # Labor Card - 15 points
            if employee.x_labor_card_number:
                score += 10
                if employee.x_labor_card_expiry:
                    score += 5
            
            # Banking Details - 20 points
            if employee.x_iban_number:
                score += 15
                if employee.x_bank_routing_code:
                    score += 5
            
            # Payment Method - 15 points
            if employee.x_payment_method:
                score += 15
            
            employee.x_compliance_score = min(score, 100)
    
    # ========== VALIDATION CONSTRAINTS ==========
    
    @api.constrains('x_mohre_person_id')
    def _check_mohre_person_id(self):
        """
        Validate MOHRE Person ID format
        Must be exactly 14 digits as per WPS requirements
        """
        for employee in self:
            if employee.x_mohre_person_id:
                # Remove any spaces or dashes
                mohre_id = employee.x_mohre_person_id.replace('-', '').replace(' ', '')
                
                if len(mohre_id) != 14:
                    raise ValidationError(
                        'MOHRE Person ID must be exactly 14 digits.\n'
                        'Current length: %s\n'
                        'WPS Requirement: 14-digit numeric identifier issued by MOHRE.' % len(mohre_id)
                    )
                
                if not mohre_id.isdigit():
                    raise ValidationError(
                        'MOHRE Person ID must contain only digits.\n'
                        'Invalid characters found in: %s' % employee.x_mohre_person_id
                    )
    
    @api.constrains('x_emirates_id')
    def _check_emirates_id(self):
        """
        Validate Emirates ID format
        Format: 784-YYYY-NNNNNNN-N (15 digits without dashes)
        """
        for employee in self:
            if employee.x_emirates_id:
                # Remove dashes and spaces for validation
                eid = employee.x_emirates_id.replace('-', '').replace(' ', '')
                
                if len(eid) != 15:
                    raise ValidationError(
                        'Emirates ID must be exactly 15 digits.\n'
                        'Format: 784-YYYY-NNNNNNN-N\n'
                        'Current: %s (length: %s)' % (employee.x_emirates_id, len(eid))
                    )
                
                if not eid.isdigit():
                    raise ValidationError(
                        'Emirates ID must contain only digits.\n'
                        'Invalid ID: %s' % employee.x_emirates_id
                    )
                
                # Check if starts with 784 (UAE country code)
                if not eid.startswith('784'):
                    raise ValidationError(
                        'Emirates ID must start with 784 (UAE country code).\n'
                        'Current ID: %s' % employee.x_emirates_id
                    )
    
    @api.constrains('x_iban_number')
    def _check_iban_format(self):
        """
        Validate UAE IBAN format
        Format: AE + 2 check digits + 19 digits = 23 characters
        """
        for employee in self:
            if employee.x_iban_number:
                iban = employee.x_iban_number.replace(' ', '').upper()
                
                if not iban.startswith('AE'):
                    raise ValidationError(
                        'UAE IBAN must start with "AE".\n'
                        'Current IBAN: %s' % employee.x_iban_number
                    )
                
                if len(iban) != 23:
                    raise ValidationError(
                        'UAE IBAN must be exactly 23 characters (AE + 21 digits).\n'
                        'Current length: %s\n'
                        'Format: AE + 2 check digits + 19 account digits' % len(iban)
                    )
                
                # Check if characters after AE are digits
                if not iban[2:].isdigit():
                    raise ValidationError(
                        'IBAN must contain only digits after "AE".\n'
                        'Invalid IBAN: %s' % employee.x_iban_number
                    )
    
    @api.constrains('x_bank_routing_code')
    def _check_bank_routing_code(self):
        """
        Validate UAE Bank Routing Code
        Must be exactly 9 digits as per Central Bank specifications
        """
        for employee in self:
            if employee.x_bank_routing_code:
                routing = employee.x_bank_routing_code.replace(' ', '')
                
                if len(routing) != 9:
                    raise ValidationError(
                        'Bank Routing Code must be exactly 9 digits.\n'
                        'Current length: %s\n'
                        'UAE Central Bank requirement: 9-digit routing code' % len(routing)
                    )
                
                if not routing.isdigit():
                    raise ValidationError(
                        'Bank Routing Code must contain only digits.\n'
                        'Invalid code: %s' % employee.x_bank_routing_code
                    )
    
    @api.constrains('x_gpssa_registered', 'x_is_uae_national', 'x_gpssa_number')
    def _check_gpssa_requirements(self):
        """
        Validate GPSSA registration requirements
        GPSSA is mandatory for UAE nationals only
        """
        for employee in self:
            if employee.x_gpssa_registered and not employee.x_is_uae_national:
                raise ValidationError(
                    'GPSSA registration is only applicable for UAE nationals.\n'
                    'Employee: %s\n'
                    'Please mark as UAE National to register with GPSSA.' % employee.name
                )
            
            if employee.x_gpssa_registered and not employee.x_gpssa_number:
                raise ValidationError(
                    'GPSSA Number is required when employee is registered with GPSSA.\n'
                    'Employee: %s\n'
                    'Please provide the GPSSA registration number.' % employee.name
                )
    
    # ========== ONCHANGE METHODS ==========
    
    @api.onchange('x_is_uae_national')
    def _onchange_uae_national(self):
        """Auto-clear GPSSA fields if not UAE national"""
        if not self.x_is_uae_national:
            self.x_gpssa_registered = False
            self.x_gpssa_number = False
    
    @api.onchange('x_payment_method')
    def _onchange_payment_method(self):
        """Clear irrelevant banking fields based on payment method"""
        if self.x_payment_method == 'exchange_house':
            # Exchange house doesn't need IBAN/routing code
            return {
                'warning': {
                    'title': 'Payment Method Changed',
                    'message': 'Exchange house payment selected. '
                              'Please provide WPS Exchange House Agent ID.'
                }
            }
        elif self.x_payment_method in ['bank_transfer', 'salary_card']:
            # Bank transfer needs IBAN and routing code
            self.x_wps_agent_id = False
            return {
                'warning': {
                    'title': 'Payment Method Changed',
                    'message': 'Bank payment selected. '
                              'Please provide IBAN and Bank Routing Code.'
                }
            }
    
    @api.onchange('x_emirates_id_expiry', 'x_visa_expiry', 'x_labor_card_expiry')
    def _onchange_expiry_dates(self):
        """Warn if any document is expiring soon"""
        warnings = []
        
        if self.x_emirates_id_expiry:
            days = (self.x_emirates_id_expiry - date.today()).days
            if 0 <= days <= 60:
                warnings.append(f'Emirates ID expires in {days} days!')
        
        if self.x_visa_expiry:
            days = (self.x_visa_expiry - date.today()).days
            if 0 <= days <= 60:
                warnings.append(f'Visa expires in {days} days!')
        
        if self.x_labor_card_expiry:
            days = (self.x_labor_card_expiry - date.today()).days
            if 0 <= days <= 60:
                warnings.append(f'Labor Card expires in {days} days!')
        
        if warnings:
            return {
                'warning': {
                    'title': 'Document Expiry Alert',
                    'message': '\n'.join(warnings)
                }
            }
