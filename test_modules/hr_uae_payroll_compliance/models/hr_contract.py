# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    """
    Extend hr.contract with UAE Labor Law compliant salary structure
    Enforces WPS requirement: Basic Salary must be ≥ 50% of total wage
    """
    _inherit = 'hr.contract'

    # ========== UAE SALARY STRUCTURE ==========
    # As per UAE Labor Law and WPS requirements, salary must be broken down into components
    
    x_basic_salary = fields.Monetary(
        string='Basic Salary',
        required=True,
        currency_field='currency_id',
        help='Basic salary component (must be ≥ 50% of total as per WPS requirement)',
        tracking=True,
    )
    
    x_housing_allowance = fields.Monetary(
        string='Housing Allowance',
        currency_field='currency_id',
        help='Housing allowance component (typically 25-50% of basic salary)',
        tracking=True,
        default=0.0,
    )
    
    x_transport_allowance = fields.Monetary(
        string='Transport Allowance',
        currency_field='currency_id',
        help='Transportation allowance',
        tracking=True,
        default=0.0,
    )
    
    x_other_allowances = fields.Monetary(
        string='Other Allowances',
        currency_field='currency_id',
        help='Other fixed allowances (food, phone, etc.)',
        tracking=True,
        default=0.0,
    )
    
    # ========== COMPUTED TOTAL SALARY ==========
    x_total_salary = fields.Monetary(
        string='Total Monthly Salary',
        compute='_compute_total_salary',
        store=True,
        currency_field='currency_id',
        help='Total of all salary components',
    )
    
    x_basic_salary_percentage = fields.Float(
        string='Basic Salary %',
        compute='_compute_basic_percentage',
        store=True,
        help='Basic salary as percentage of total (must be ≥ 50% for WPS)',
    )
    
    # ========== UAE CONTRACT TYPE ==========
    x_contract_type_uae = fields.Selection([
        ('unlimited', 'Unlimited Contract'),
        ('limited', 'Limited Contract'),
    ], string='UAE Contract Type',
        required=True,
        default='unlimited',
        help='Contract type as per UAE Labor Law:\n'
             '- Unlimited: No fixed end date (most common)\n'
             '- Limited: Fixed duration (max 3 years, renewable)',
        tracking=True,
    )
    
    # ========== WORKING HOURS ==========
    x_weekly_working_hours = fields.Float(
        string='Weekly Working Hours',
        default=48.0,
        help='Normal working hours per week (UAE standard: 48 hours)',
    )
    
    x_daily_working_hours = fields.Float(
        string='Daily Working Hours',
        default=8.0,
        help='Normal working hours per day (UAE standard: 8 hours)',
    )
    
    # ========== COMPLIANCE FLAGS ==========
    x_wps_compliant = fields.Boolean(
        string='WPS Compliant',
        compute='_compute_wps_compliant',
        store=True,
        help='Indicates if salary structure meets WPS requirements (basic ≥ 50%)',
    )
    
    x_contract_compliant = fields.Boolean(
        string='Contract Compliant',
        compute='_compute_contract_compliant',
        store=True,
        help='Overall contract compliance with UAE Labor Law',
    )
    
    # ========== GRATUITY CALCULATION BASE ==========
    x_gratuity_base_salary = fields.Monetary(
        string='Gratuity Base Salary',
        compute='_compute_gratuity_base',
        store=True,
        currency_field='currency_id',
        help='Salary base for end-of-service gratuity calculation (Basic salary only)',
    )
    
    # ========== GPSSA CONTRIBUTION BASE (UAE Nationals) ==========
    x_gpssa_base_salary = fields.Monetary(
        string='GPSSA Pensionable Salary',
        compute='_compute_gpssa_base',
        store=True,
        currency_field='currency_id',
        help='Pensionable salary for GPSSA calculation (Basic + Housing + Transport)',
    )
    
    x_gpssa_employee_contribution = fields.Monetary(
        string='GPSSA Employee (5%)',
        compute='_compute_gpssa_contributions',
        store=True,
        currency_field='currency_id',
        help='Employee GPSSA contribution (5% of pensionable salary)',
    )
    
    x_gpssa_employer_contribution = fields.Monetary(
        string='GPSSA Employer (12.5%)',
        compute='_compute_gpssa_contributions',
        store=True,
        currency_field='currency_id',
        help='Employer GPSSA contribution (12.5% of pensionable salary)',
    )
    
    # ========== COMPUTED FIELDS ==========
    
    @api.depends('x_basic_salary', 'x_housing_allowance', 'x_transport_allowance', 'x_other_allowances')
    def _compute_total_salary(self):
        """Calculate total monthly salary from all components"""
        for contract in self:
            contract.x_total_salary = (
                contract.x_basic_salary +
                contract.x_housing_allowance +
                contract.x_transport_allowance +
                contract.x_other_allowances
            )
    
    @api.depends('x_basic_salary', 'x_total_salary')
    def _compute_basic_percentage(self):
        """
        Calculate basic salary as percentage of total
        WPS Requirement: Must be ≥ 50%
        """
        for contract in self:
            if contract.x_total_salary > 0:
                contract.x_basic_salary_percentage = (
                    contract.x_basic_salary / contract.x_total_salary
                ) * 100
            else:
                contract.x_basic_salary_percentage = 0.0
    
    @api.depends('x_basic_salary_percentage')
    def _compute_wps_compliant(self):
        """
        Check WPS compliance
        UAE WPS Requirement: Basic salary must be at least 50% of total salary
        """
        for contract in self:
            contract.x_wps_compliant = contract.x_basic_salary_percentage >= 50.0
    
    @api.depends('x_wps_compliant', 'x_contract_type_uae', 'employee_id')
    def _compute_contract_compliant(self):
        """Check overall contract compliance with UAE Labor Law"""
        for contract in self:
            # Basic compliance checks
            has_contract_type = bool(contract.x_contract_type_uae)
            is_wps_compliant = contract.x_wps_compliant
            has_employee = bool(contract.employee_id)
            
            contract.x_contract_compliant = (
                has_contract_type and 
                is_wps_compliant and 
                has_employee
            )
    
    @api.depends('x_basic_salary')
    def _compute_gratuity_base(self):
        """
        Calculate gratuity base salary
        UAE Law: Gratuity is calculated on basic salary only
        Formula: (Basic Salary / 30) × Days of Service
        """
        for contract in self:
            contract.x_gratuity_base_salary = contract.x_basic_salary
    
    @api.depends('x_basic_salary', 'x_housing_allowance', 'x_transport_allowance')
    def _compute_gpssa_base(self):
        """
        Calculate GPSSA pensionable salary (UAE Nationals only)
        Pensionable Salary = Basic + Housing + Transport
        """
        for contract in self:
            contract.x_gpssa_base_salary = (
                contract.x_basic_salary +
                contract.x_housing_allowance +
                contract.x_transport_allowance
            )
    
    @api.depends('x_gpssa_base_salary', 'employee_id.x_gpssa_registered')
    def _compute_gpssa_contributions(self):
        """
        Calculate GPSSA contributions for UAE nationals
        Employee: 5% of pensionable salary
        Employer: 12.5% of pensionable salary
        """
        for contract in self:
            if contract.employee_id.x_gpssa_registered:
                contract.x_gpssa_employee_contribution = contract.x_gpssa_base_salary * 0.05
                contract.x_gpssa_employer_contribution = contract.x_gpssa_base_salary * 0.125
            else:
                contract.x_gpssa_employee_contribution = 0.0
                contract.x_gpssa_employer_contribution = 0.0
    
    # ========== VALIDATION CONSTRAINTS ==========
    
    @api.constrains('x_basic_salary', 'x_total_salary')
    def _check_basic_salary_percentage(self):
        """
        Enforce WPS requirement: Basic salary must be at least 50% of total
        UAE Central Bank WPS Specification
        """
        for contract in self:
            if contract.x_total_salary > 0:
                percentage = (contract.x_basic_salary / contract.x_total_salary) * 100
                
                if percentage < 50.0:
                    raise ValidationError(
                        'WPS Compliance Error: Basic salary must be at least 50%% of total salary.\n\n'
                        'Employee: %s\n'
                        'Basic Salary: %s AED\n'
                        'Total Salary: %s AED\n'
                        'Current Percentage: %.2f%%\n'
                        'Required: ≥ 50.00%%\n\n'
                        'UAE WPS Requirement: The basic salary component must constitute at least '
                        'half of the total monthly wage for WPS compliance.' % (
                            contract.employee_id.name if contract.employee_id else 'N/A',
                            contract.x_basic_salary,
                            contract.x_total_salary,
                            percentage
                        )
                    )
    
    @api.constrains('x_basic_salary', 'x_housing_allowance', 'x_transport_allowance', 'x_other_allowances')
    def _check_positive_amounts(self):
        """Ensure all salary components are positive"""
        for contract in self:
            if contract.x_basic_salary <= 0:
                raise ValidationError(
                    'Basic salary must be greater than zero.\n'
                    'Employee: %s' % (contract.employee_id.name if contract.employee_id else 'N/A')
                )
            
            if contract.x_housing_allowance < 0:
                raise ValidationError('Housing allowance cannot be negative.')
            if contract.x_transport_allowance < 0:
                raise ValidationError('Transport allowance cannot be negative.')
            if contract.x_other_allowances < 0:
                raise ValidationError('Other allowances cannot be negative.')
    
    @api.constrains('x_contract_type_uae', 'date_end')
    def _check_limited_contract_end_date(self):
        """
        Validate limited contract end date
        UAE Law: Limited contracts cannot exceed 3 years
        """
        for contract in self:
            if contract.x_contract_type_uae == 'limited':
                if not contract.date_end:
                    raise ValidationError(
                        'Limited contracts must have an end date.\n'
                        'Employee: %s\n\n'
                        'UAE Labor Law: Limited contracts require a specified end date '
                        '(maximum 3 years, renewable).' % (
                            contract.employee_id.name if contract.employee_id else 'N/A'
                        )
                    )
                
                # Check if duration exceeds 3 years
                if contract.date_start and contract.date_end:
                    duration = (contract.date_end - contract.date_start).days
                    max_days = 3 * 365  # 3 years
                    
                    if duration > max_days:
                        raise ValidationError(
                            'Limited contract duration cannot exceed 3 years.\n'
                            'Employee: %s\n'
                            'Contract Duration: %s days\n'
                            'Maximum Allowed: 1095 days (3 years)\n\n'
                            'UAE Labor Law: Limited contracts have a maximum duration of 3 years, '
                            'renewable by mutual agreement.' % (
                                contract.employee_id.name if contract.employee_id else 'N/A',
                                duration
                            )
                        )
    
    @api.constrains('x_weekly_working_hours', 'x_daily_working_hours')
    def _check_working_hours(self):
        """
        Validate working hours comply with UAE Labor Law
        Standard: 8 hours/day, 48 hours/week
        Ramadan: 6 hours/day (not enforced here, handled in attendance)
        """
        for contract in self:
            if contract.x_daily_working_hours > 8:
                raise ValidationError(
                    'Daily working hours cannot exceed 8 hours.\n'
                    'Employee: %s\n'
                    'Specified: %.2f hours\n\n'
                    'UAE Labor Law: Normal working hours are 8 hours per day or 48 hours per week.' % (
                        contract.employee_id.name if contract.employee_id else 'N/A',
                        contract.x_daily_working_hours
                    )
                )
            
            if contract.x_weekly_working_hours > 48:
                raise ValidationError(
                    'Weekly working hours cannot exceed 48 hours.\n'
                    'Employee: %s\n'
                    'Specified: %.2f hours\n\n'
                    'UAE Labor Law: Maximum working hours are 48 hours per week.' % (
                        contract.employee_id.name if contract.employee_id else 'N/A',
                        contract.x_weekly_working_hours
                    )
                )
    
    # ========== ONCHANGE METHODS ==========
    
    @api.onchange('x_basic_salary')
    def _onchange_basic_salary(self):
        """Auto-calculate suggested allowances based on basic salary"""
        if self.x_basic_salary and not self.x_housing_allowance:
            # Suggest housing allowance as 30% of basic (common UAE practice)
            suggested_housing = self.x_basic_salary * 0.30
            return {
                'warning': {
                    'title': 'Suggested Allowances',
                    'message': f'Typical UAE allowances:\n'
                              f'Housing: 25-50% of basic (suggested: {suggested_housing:.2f} AED)\n'
                              f'Transport: 10-20% of basic\n\n'
                              f'Remember: Basic salary must be ≥ 50% of total for WPS compliance.'
                }
            }
    
    @api.onchange('x_basic_salary', 'x_housing_allowance', 'x_transport_allowance', 'x_other_allowances')
    def _onchange_salary_components(self):
        """Warn if basic salary percentage is below 50%"""
        if self.x_total_salary > 0:
            percentage = (self.x_basic_salary / self.x_total_salary) * 100
            
            if percentage < 50.0:
                return {
                    'warning': {
                        'title': 'WPS Compliance Warning',
                        'message': f'Basic salary is {percentage:.2f}% of total salary.\n\n'
                                  f'WPS REQUIREMENT: Basic must be ≥ 50%\n\n'
                                  f'Current breakdown:\n'
                                  f'- Basic: {self.x_basic_salary:.2f} AED\n'
                                  f'- Housing: {self.x_housing_allowance:.2f} AED\n'
                                  f'- Transport: {self.x_transport_allowance:.2f} AED\n'
                                  f'- Other: {self.x_other_allowances:.2f} AED\n'
                                  f'- Total: {self.x_total_salary:.2f} AED\n\n'
                                  f'Please adjust allowances to ensure compliance.'
                    }
                }
    
    @api.onchange('x_contract_type_uae')
    def _onchange_contract_type(self):
        """Provide guidance on contract types"""
        if self.x_contract_type_uae == 'limited':
            return {
                'warning': {
                    'title': 'Limited Contract Requirements',
                    'message': 'Limited contracts require:\n'
                              '1. Specific end date (max 3 years)\n'
                              '2. Clear termination terms\n'
                              '3. Can be renewed by mutual agreement\n\n'
                              'Note: Most UAE employment contracts are unlimited.'
                }
            }
    
    # ========== HELPER METHODS ==========
    
    def calculate_daily_wage(self):
        """
        Calculate daily wage for leave deductions
        Formula: Total Monthly Salary / 30
        """
        self.ensure_one()
        return self.x_total_salary / 30
    
    def calculate_hourly_rate(self):
        """
        Calculate hourly rate for overtime calculations
        Formula: Basic Salary / (30 days × 8 hours) = Basic Salary / 240
        """
        self.ensure_one()
        return self.x_basic_salary / 240
    
    def get_overtime_rate(self, overtime_type='regular'):
        """
        Get overtime rate based on type
        Regular OT (day time): 125% of hourly rate
        Premium OT (night/weekend): 150% of hourly rate
        """
        self.ensure_one()
        hourly_rate = self.calculate_hourly_rate()
        
        rates = {
            'regular': hourly_rate * 1.25,  # 125%
            'premium': hourly_rate * 1.50,  # 150%
        }
        
        return rates.get(overtime_type, hourly_rate)
