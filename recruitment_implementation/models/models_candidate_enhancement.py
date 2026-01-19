# -*- coding: utf-8 -*-
"""
Enhanced Recruitment Candidate Model
Adds placement readiness, visa status, and NOC tracking
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class RecruitmentCandidate(models.Model):
    _inherit = 'recruitment.candidate'
    
    # ============================================================================
    # PLACEMENT READINESS SECTION
    # ============================================================================
    
    placement_ready = fields.Boolean(
        string='Ready for Placement',
        compute='_compute_placement_ready',
        store=True,
        tracking=True,
        help='Automatically checks if candidate can be placed'
    )
    
    placement_blockers = fields.Text(
        string='Placement Blockers',
        compute='_compute_placement_ready',
        help='Reasons why candidate cannot be placed'
    )
    
    # ============================================================================
    # VISA STATUS SECTION
    # ============================================================================
    
    visa_status = fields.Selection([
        ('no_visa', 'No UAE Visa'),
        ('visit_visa', 'Visit/Tourist Visa'),
        ('employment_active', 'Employment Visa - Active'),
        ('employment_cancelled', 'Employment Visa - Cancelled'),
        ('free_zone', 'Free Zone Visa'),
        ('family_visa', 'Family Sponsorship Visa'),
        ('new_entry', 'New Entry (Not Yet in UAE)'),
    ], string='Current Visa Status', tracking=True,
       help='Current visa status in UAE')
    
    visa_sponsor = fields.Char(
        string='Current Visa Sponsor',
        tracking=True,
        help='Company/Person currently sponsoring the visa'
    )
    
    visa_expiry = fields.Date(
        string='Visa Expiry Date',
        tracking=True,
        help='Date when current visa expires'
    )
    
    visa_validity_days = fields.Integer(
        string='Days Until Visa Expires',
        compute='_compute_visa_validity_days'
    )
    
    visa_valid_for_placement = fields.Boolean(
        string='Visa Valid for Placement',
        compute='_compute_visa_valid_for_placement',
        store=True,
        help='True if visa is still valid (not expired or about to expire)'
    )
    
    # ============================================================================
    # NOC (NO OBJECTION CERTIFICATE) SECTION
    # ============================================================================
    
    noc_required = fields.Boolean(
        string='NOC Required from Current Sponsor',
        compute='_compute_noc_required',
        store=True,
        tracking=True,
        help='True if candidate needs NOC to change sponsorship'
    )
    
    noc_status = fields.Selection([
        ('not_required', 'Not Required'),
        ('pending', 'Pending - Awaiting NOC'),
        ('obtained', 'NOC Obtained'),
        ('refused', 'NOC Refused by Sponsor'),
        ('expired', 'NOC Expired'),
    ], string='NOC Status', default='not_required', tracking=True,
       help='Status of No Objection Certificate from current sponsor')
    
    noc_received_date = fields.Date(
        string='NOC Received Date',
        tracking=True
    )
    
    noc_expiry_date = fields.Date(
        string='NOC Expiry Date',
        tracking=True
    )
    
    noc_document = fields.Binary(
        string='NOC Document',
        attachment=True,
        help='PDF or image of NOC certificate'
    )
    
    noc_document_filename = fields.Char(
        string='NOC Document Filename'
    )
    
    # ============================================================================
    # DOCUMENT VERIFICATION SECTION
    # ============================================================================
    
    passport_verified = fields.Boolean(
        string='Passport Verified',
        tracking=True
    )
    
    passport_number = fields.Char(
        string='Passport Number',
        tracking=True
    )
    
    passport_expiry = fields.Date(
        string='Passport Expiry Date',
        tracking=True
    )
    
    passport_expiry_valid = fields.Boolean(
        string='Passport Valid (6+ Months)',
        compute='_compute_passport_validity',
        store=True,
        help='Passport must be valid for at least 6 months from now'
    )
    
    certificates_verified = fields.Boolean(
        string='Qualifications Verified',
        tracking=True,
        help='Educational and professional certificates verified'
    )
    
    police_clearance_verified = fields.Boolean(
        string='Police Clearance Verified',
        tracking=True
    )
    
    police_clearance_expiry = fields.Date(
        string='Police Clearance Expiry',
        tracking=True
    )
    
    medical_fitness_certificate = fields.Boolean(
        string='Medical Fitness Confirmed',
        tracking=True,
        help='Medical fitness for employment confirmed'
    )
    
    # ============================================================================
    # AVAILABILITY SECTION
    # ============================================================================
    
    availability_status = fields.Selection([
        ('available', 'Available'),
        ('in_interview', 'In Interview Process'),
        ('selected', 'Selected - Awaiting Deployment'),
        ('deployed', 'Deployed/Placed'),
        ('unavailable', 'Unavailable'),
        ('inactive', 'Inactive'),
    ], string='Availability Status', default='available', tracking=True)
    
    earliest_available_date = fields.Date(
        string='Earliest Available Date',
        help='Date when candidate can start work'
    )
    
    notice_period_days = fields.Integer(
        string='Notice Period (Days)',
        default=30,
        help='Notice period if currently employed elsewhere'
    )
    
    # ============================================================================
    # PLACEMENT HISTORY SECTION
    # ============================================================================
    
    placement_count = fields.Integer(
        string='Placements Count',
        compute='_compute_placement_count',
        store=True,
        help='Total number of successful placements'
    )
    
    last_placement_date = fields.Date(
        string='Last Placement Date',
        help='Date of last placement'
    )
    
    placement_success_rate = fields.Float(
        string='Placement Success Rate %',
        compute='_compute_placement_success_rate',
        help='% of placements that completed successfully'
    )
    
    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    
    @api.depends(
        'visa_status', 'noc_status', 'passport_verified',
        'passport_expiry_valid', 'police_clearance_verified',
        'certificates_verified', 'visa_valid_for_placement'
    )
    def _compute_placement_ready(self):
        """
        Check if candidate is ready for placement.
        Sets placement_ready=True only if all requirements met.
        """
        for rec in self:
            blockers = []
            ready = True
            
            # Check visa eligibility
            if not rec.visa_valid_for_placement:
                blockers.append('❌ Visa not valid for placement (expired or invalid)')
                ready = False
            
            # Check NOC if required
            if rec.noc_required and rec.noc_status != 'obtained':
                blockers.append('❌ NOC required but not obtained')
                ready = False
            
            # Check passport verification
            if not rec.passport_verified:
                blockers.append('❌ Passport not verified')
                ready = False
            
            # Check passport validity
            if not rec.passport_expiry_valid:
                blockers.append('❌ Passport expiring in < 6 months')
                ready = False
            
            # Check certificates
            if not rec.certificates_verified:
                blockers.append('⚠️ Qualifications not yet verified')
                ready = False
            
            # Check police clearance
            if not rec.police_clearance_verified:
                blockers.append('⚠️ Police clearance not verified')
                ready = False
            
            # Check medical fitness
            if not rec.medical_fitness_certificate:
                blockers.append('⚠️ Medical fitness not confirmed')
                ready = False
            
            rec.placement_ready = ready
            rec.placement_blockers = '\n'.join(blockers) if blockers else False
    
    @api.depends('visa_status')
    def _compute_noc_required(self):
        """
        NOC is required only if candidate has active employment visa
        that must be cancelled to move to new employer
        """
        for rec in self:
            rec.noc_required = rec.visa_status == 'employment_active'
    
    @api.depends('visa_expiry')
    def _compute_visa_validity_days(self):
        """Calculate days until visa expires"""
        today = datetime.now().date()
        for rec in self:
            if rec.visa_expiry:
                days = (rec.visa_expiry - today).days
                rec.visa_validity_days = max(0, days)
            else:
                rec.visa_validity_days = 0
    
    @api.depends('visa_status', 'visa_expiry', 'visa_validity_days')
    def _compute_visa_valid_for_placement(self):
        """Check if visa is valid and not about to expire"""
        for rec in self:
            # Valid visa statuses
            valid_statuses = ['visit_visa', 'employment_active', 'free_zone', 'family_visa']
            
            # Must have valid status and not be expired
            if rec.visa_status in valid_statuses:
                if rec.visa_expiry:
                    # Visa must have at least 6 months validity
                    rec.visa_valid_for_placement = rec.visa_validity_days >= 180
                else:
                    rec.visa_valid_for_placement = False
            else:
                rec.visa_valid_for_placement = False
    
    @api.depends('passport_expiry')
    def _compute_passport_validity(self):
        """Check if passport is valid for at least 6 months"""
        today = datetime.now().date()
        min_expiry = today + timedelta(days=180)  # 6 months
        
        for rec in self:
            if rec.passport_expiry:
                rec.passport_expiry_valid = rec.passport_expiry >= min_expiry
            else:
                rec.passport_expiry_valid = False
    
    @api.depends('candidate_id')
    def _compute_placement_count(self):
        """Count successful placements for this candidate"""
        for rec in self:
            applications = self.env['recruitment.application'].search([
                ('candidate_id', '=', rec.id),
                ('state', 'in', ['deployed', 'contract']),
            ])
            rec.placement_count = len(applications)
    
    @api.depends('placement_count')
    def _compute_placement_success_rate(self):
        """Calculate placement success rate"""
        for rec in self:
            if rec.placement_count > 0:
                # Get total applications for this candidate
                total_apps = self.env['recruitment.application'].search_count([
                    ('candidate_id', '=', rec.id),
                ])
                if total_apps > 0:
                    rec.placement_success_rate = (rec.placement_count / total_apps) * 100
                else:
                    rec.placement_success_rate = 0.0
            else:
                rec.placement_success_rate = 0.0
    
    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_verify_passport(self):
        """Mark passport as verified"""
        self.write({'passport_verified': True})
    
    def action_verify_certificates(self):
        """Mark certificates as verified"""
        self.write({'certificates_verified': True})
    
    def action_verify_police_clearance(self):
        """Mark police clearance as verified"""
        self.write({
            'police_clearance_verified': True,
            'police_clearance_expiry': fields.Date.today() + timedelta(days=365),
        })
    
    def action_confirm_medical_fitness(self):
        """Confirm medical fitness"""
        self.write({'medical_fitness_certificate': True})
    
    def action_request_noc(self):
        """Create an activity to request NOC from current sponsor"""
        if self.noc_status not in ('pending', 'obtained'):
            self.write({'noc_status': 'pending'})
            
            # Create activity
            self.activity_schedule(
                activity_type_xmlid='mail.mail_activity_data_todo',
                summary=_('Request NOC from Current Sponsor'),
                note=_('Request No Objection Certificate from %s') % (self.visa_sponsor or 'sponsor'),
                user_id=self.env.user.id,
            )
    
    def action_mark_noc_obtained(self):
        """Mark NOC as obtained"""
        self.write({
            'noc_status': 'obtained',
            'noc_received_date': fields.Date.today(),
            'noc_expiry_date': fields.Date.today() + timedelta(days=180),
        })
    
    def action_set_available(self):
        """Mark candidate as available for placement"""
        self.write({
            'availability_status': 'available',
            'earliest_available_date': fields.Date.today(),
        })
    
    def action_check_placement_readiness(self):
        """Return a summary of placement readiness"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Placement Readiness Check'),
            'res_model': 'recruitment.candidate',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
