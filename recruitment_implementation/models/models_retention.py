# -*- coding: utf-8 -*-
"""
Odoo Recruitment Retention Model
Part of recruitment_uae module for Odoo 18
Manages placement retention and payment collection
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class RecruitmentRetention(models.Model):
    _name = 'recruitment.retention'
    _description = 'Placement Retention Management'
    _order = 'retention_release_date asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Sequences and naming
    name = fields.Char(
        string='Retention Reference',
        required=True,
        default=lambda self: _('New'),
        copy=False,
        tracking=True
    )
    
    # Links to related records
    deployment_id = fields.Many2one(
        'recruitment.deployment',
        string='Deployment',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    candidate_id = fields.Many2one(
        'recruitment.candidate',
        related='deployment_id.candidate_id',
        string='Candidate',
        store=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='deployment_id.partner_id',
        string='Client',
        store=True
    )
    invoice_id = fields.Many2one(
        'account.move',
        related='deployment_id.invoice_id',
        string='Placement Invoice',
        store=True
    )
    
    # Retention Financial Terms
    total_placement_fee = fields.Monetary(
        string='Total Placement Fee',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help='Total fee charged to client for placement'
    )
    
    upfront_percentage = fields.Float(
        string='Upfront Payment %',
        required=True,
        default=70.0,
        tracking=True,
        help='Percentage of total fee payable upfront (e.g., 70%)'
    )
    retention_percentage = fields.Float(
        string='Retention %',
        compute='_compute_retention_percentage',
        store=True,
        help='Automatically calculated as 100 - upfront %'
    )
    
    upfront_amount = fields.Monetary(
        string='Upfront Payment Amount',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id'
    )
    retention_amount = fields.Monetary(
        string='Retention Amount',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id',
        tracking=True,
        help='Amount held back until end of retention period'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Retention Period Configuration
    placement_date = fields.Date(
        string='Placement Date',
        related='deployment_id.deployment_date',
        store=True
    )
    retention_period_days = fields.Integer(
        string='Retention Period (Days)',
        required=True,
        default=90,
        tracking=True,
        help='Number of days retention amount is held (e.g., 90 days)'
    )
    retention_release_date = fields.Date(
        string='Retention Release Date',
        compute='_compute_release_date',
        store=True,
        tracking=True,
        help='Date when retention amount becomes due (placement_date + period)'
    )
    
    # Upfront Payment Tracking
    upfront_paid = fields.Boolean(
        string='Upfront Payment Received',
        tracking=True
    )
    upfront_payment_date = fields.Date(
        string='Upfront Payment Date'
    )
    
    # Retention Payment Status
    retention_status = fields.Selection([
        ('pending', 'Pending Release'),
        ('released', 'Released for Payment'),
        ('paid', 'Fully Paid'),
        ('forfeited', 'Forfeited'),
        ('partial', 'Partial Payment'),
    ], string='Retention Payment Status', default='pending', tracking=True)
    
    retention_paid = fields.Boolean(
        string='Retention Payment Received',
        tracking=True
    )
    retention_payment_date = fields.Date(
        string='Retention Payment Date'
    )
    retention_paid_amount = fields.Monetary(
        string='Retention Amount Paid',
        currency_field='currency_id'
    )
    
    # Candidate Stability During Retention
    candidate_status = fields.Selection([
        ('working', 'Working Normally'),
        ('issue_minor', 'Minor Issues'),
        ('issue_major', 'Major Issues'),
        ('absconded', 'Absconded/Missing'),
        ('resigned', 'Resigned from Job'),
        ('terminated', 'Terminated by Client'),
    ], string='Candidate Status', default='working', tracking=True)
    
    candidate_working_days = fields.Integer(
        string='Days Working',
        compute='_compute_working_days'
    )
    days_until_release = fields.Integer(
        string='Days Until Release',
        compute='_compute_days_until_release'
    )
    
    # Risk Assessment
    risk_level = fields.Selection([
        ('low', '🟢 Low Risk'),
        ('medium', '🟡 Medium Risk'),
        ('high', '🔴 High Risk'),
        ('critical', '⚫ Critical - Forfeit Imminent'),
    ], string='Risk Level', compute='_compute_risk_level', store=True, tracking=True)
    
    risk_notes = fields.Text(
        string='Risk Notes',
        help='Notes about any issues or concerns'
    )
    
    # Forfeiture Details
    forfeiture_reason = fields.Selection([
        ('absconded', 'Candidate Absconded/Missing'),
        ('early_resignation', 'Resigned Before Retention Period'),
        ('poor_performance', 'Poor Performance - Client Terminated'),
        ('misconduct', 'Misconduct/Violation'),
        ('mutual_agreement', 'Mutual Agreement'),
        ('other', 'Other'),
    ], string='Forfeiture Reason')
    
    forfeiture_date = fields.Date(
        string='Forfeiture Date',
        help='Date when forfeiture was applied'
    )
    forfeiture_notes = fields.Text(
        string='Forfeiture Notes'
    )
    
    # Guarantees and Replacement
    has_replacement_guarantee = fields.Boolean(
        string='Replacement Guarantee Offered',
        tracking=True,
        help='If yes, must provide free replacement if candidate leaves'
    )
    replacement_count = fields.Integer(
        string='Replacement Count',
        default=0,
        tracking=True,
        help='Number of times replacement was required'
    )
    
    # State Machine
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active - Monitoring'),
        ('released', 'Released - Awaiting Payment'),
        ('completed', 'Completed - Fully Collected'),
        ('forfeited', 'Forfeited - Loss Applied'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    # Computed field dependencies
    @api.depends('upfront_percentage')
    def _compute_retention_percentage(self):
        """Retention % = 100 - Upfront %"""
        for rec in self:
            rec.retention_percentage = 100.0 - rec.upfront_percentage
    
    @api.depends('total_placement_fee', 'upfront_percentage')
    def _compute_amounts(self):
        """Calculate upfront and retention amounts"""
        for rec in self:
            rec.upfront_amount = rec.total_placement_fee * (rec.upfront_percentage / 100.0)
            rec.retention_amount = rec.total_placement_fee - rec.upfront_amount
    
    @api.depends('placement_date', 'retention_period_days')
    def _compute_release_date(self):
        """Calculate retention release date"""
        for rec in self:
            if rec.placement_date and rec.retention_period_days:
                rec.retention_release_date = rec.placement_date + timedelta(
                    days=rec.retention_period_days
                )
            else:
                rec.retention_release_date = False
    
    @api.depends('placement_date')
    def _compute_working_days(self):
        """Calculate days candidate has been working"""
        from datetime import datetime
        today = datetime.now().date()
        
        for rec in self:
            if rec.placement_date:
                rec.candidate_working_days = (today - rec.placement_date).days
            else:
                rec.candidate_working_days = 0
    
    @api.depends('retention_release_date')
    def _compute_days_until_release(self):
        """Calculate days until retention is released"""
        from datetime import datetime
        today = datetime.now().date()
        
        for rec in self:
            if rec.retention_release_date:
                days = (rec.retention_release_date - today).days
                rec.days_until_release = max(0, days)
            else:
                rec.days_until_release = 0
    
    @api.depends('candidate_status', 'days_until_release', 'retention_paid')
    def _compute_risk_level(self):
        """Assess risk level of retention"""
        for rec in self:
            if rec.retention_paid or rec.state == 'completed':
                rec.risk_level = 'low'
            elif rec.state == 'forfeited':
                rec.risk_level = 'critical'
            elif rec.candidate_status == 'absconded':
                rec.risk_level = 'critical'
            elif rec.candidate_status in ('resigned', 'terminated'):
                rec.risk_level = 'high'
            elif rec.candidate_status == 'issue_major':
                rec.risk_level = 'high'
            elif rec.candidate_status == 'issue_minor':
                rec.risk_level = 'medium'
            elif rec.days_until_release < 7:
                rec.risk_level = 'medium'  # Releasing soon
            else:
                rec.risk_level = 'low'
    
    @api.model
    def create(self, vals):
        """Create retention record with auto-generated sequence"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'recruitment.retention'
            ) or _('New')
        return super().create(vals)
    
    def action_activate(self):
        """Activate retention tracking"""
        self.write({'state': 'active'})
        return True
    
    def action_mark_upfront_paid(self):
        """Mark upfront payment as received"""
        self.write({
            'upfront_paid': True,
            'upfront_payment_date': fields.Date.today(),
        })
        return True
    
    def action_release_retention(self):
        """Release retention for payment (usually automatic on release date)"""
        self.write({
            'state': 'released',
            'retention_status': 'released',
        })
        # Create activity to follow up on payment
        self._create_payment_activity()
        return True
    
    def action_mark_retention_paid(self):
        """Mark retention payment as received"""
        self.write({
            'retention_paid': True,
            'retention_payment_date': fields.Date.today(),
            'retention_paid_amount': self.retention_amount,
            'retention_status': 'paid',
            'state': 'completed',
        })
        return True
    
    def action_forfeit_retention(self):
        """Open forfeit wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'retention.forfeit.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_retention_id': self.id},
        }
    
    def action_cancel(self):
        """Cancel retention record"""
        self.write({'state': 'cancelled'})
        return True
    
    def _create_payment_activity(self):
        """Create activity for retention payment follow-up"""
        self.activity_schedule(
            activity_type_xmlid='mail.mail_activity_data_todo',
            summary=_('Follow up on Retention Payment for %s') % self.candidate_id.name,
            note=_('Retention of %s %s is due for payment') % (
                self.retention_amount,
                self.currency_id.symbol
            ),
            user_id=self.deployment_id.partner_id.user_id.id or self.env.user.id,
        )
    
    @api.model
    def cron_release_due_retentions(self):
        """Cron: Daily check for retentions that should be released"""
        today = fields.Date.today()
        
        retentions_to_release = self.search([
            ('state', '=', 'active'),
            ('retention_release_date', '<=', today),
            ('retention_status', '!=', 'released'),
        ])
        
        for retention in retentions_to_release:
            retention.action_release_retention()
    
    def _get_overdue_retentions(self):
        """Get retentions that are overdue for payment"""
        today = fields.Date.today()
        return self.search([
            ('state', '=', 'released'),
            ('retention_paid', '=', False),
            ('retention_release_date', '<', today),
        ])
