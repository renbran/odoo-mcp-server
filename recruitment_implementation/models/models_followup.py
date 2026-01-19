# -*- coding: utf-8 -*-
"""
Recruitment Follow-up Model
Tracks post-placement follow-ups and candidate stability checks
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class RecruitmentFollowUp(models.Model):
    _name = 'recruitment.followup'
    _description = 'Post-Placement Follow-Up Tracking'
    _order = 'scheduled_date asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Sequences and naming
    name = fields.Char(
        string='Follow-Up Reference',
        required=True,
        default=lambda self: _('New'),
        copy=False,
        tracking=True
    )
    
    # Links to deployment and candidate
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
    
    retention_id = fields.Many2one(
        'recruitment.retention',
        string='Associated Retention',
        help='Link to retention record if applicable'
    )
    
    # Follow-up Schedule
    followup_type = fields.Selection([
        ('week_1', 'Week 1 - Initial Check'),
        ('week_2', 'Week 2 - Settling In'),
        ('week_4', 'Week 4 - Progress Check'),
        ('day_30', 'Day 30 - One Month Review'),
        ('day_60', 'Day 60 - Two Month Review'),
        ('day_90', 'Day 90 - Retention Release Review'),
        ('custom', 'Custom Follow-up'),
        ('urgent', 'Urgent Issue Follow-up'),
    ], string='Follow-Up Type', required=True, tracking=True)
    
    scheduled_date = fields.Date(
        string='Scheduled Date',
        required=True,
        tracking=True
    )
    
    completed_date = fields.Date(
        string='Completed Date',
        help='Date when follow-up was actually completed'
    )
    
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_days_overdue'
    )
    
    # Candidate Status Tracking
    candidate_working = fields.Boolean(
        string='Candidate Working',
        default=True,
        tracking=True
    )
    
    candidate_location = fields.Selection([
        ('at_workplace', 'At Workplace'),
        ('on_leave', 'On Leave'),
        ('missing', 'Missing/Not Reachable'),
        ('absconded', 'Absconded'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated by Client'),
    ], string='Candidate Location/Status', default='at_workplace', tracking=True)
    
    # Issues and Concerns
    issue_reported = fields.Boolean(
        string='Any Issues Reported',
        tracking=True
    )
    
    issue_severity = fields.Selection([
        ('none', 'No Issues'),
        ('minor', 'Minor Issues'),
        ('moderate', 'Moderate Issues'),
        ('severe', 'Severe Issues'),
        ('critical', 'Critical - Retention at Risk'),
    ], string='Issue Severity', default='none', tracking=True)
    
    issue_description = fields.Text(
        string='Issue Description',
        help='Details of any issues or concerns'
    )
    
    issue_category = fields.Selection([
        ('accommodation', 'Accommodation Problems'),
        ('salary', 'Salary/Payment Issues'),
        ('working_conditions', 'Working Conditions'),
        ('harassment', 'Harassment/Bullying'),
        ('legal', 'Legal/Documentation Issues'),
        ('health', 'Health/Medical Issues'),
        ('personal', 'Personal/Family Issues'),
        ('other', 'Other'),
    ], string='Issue Category')
    
    # Contact Method
    contact_method = fields.Selection([
        ('phone', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('in_person', 'In-Person Visit'),
        ('client_report', 'Client Report'),
        ('other', 'Other'),
    ], string='Contact Method', default='phone', tracking=True)
    
    contact_person = fields.Char(
        string='Person Contacted',
        help='Name of person who was contacted'
    )
    
    contact_notes = fields.Text(
        string='Contact Notes',
        help='Summary of conversation or interaction'
    )
    
    # Recommendations
    next_action_required = fields.Boolean(
        string='Next Action Required',
        tracking=True
    )
    
    next_action_type = fields.Selection([
        ('none', 'No Further Action'),
        ('followup_contact', 'Follow-up Contact'),
        ('client_escalation', 'Escalate to Client'),
        ('management_review', 'Management Review'),
        ('candidate_assistance', 'Candidate Assistance'),
        ('forfeit_retention', 'Forfeit Retention'),
        ('replacement', 'Arrange Replacement'),
    ], string='Next Action', default='none')
    
    next_action_notes = fields.Text(
        string='Next Action Notes'
    )
    
    recommended_by = fields.Many2one(
        'res.users',
        string='Recommended By'
    )
    
    # Retention Impact
    retention_at_risk = fields.Boolean(
        string='Retention at Risk',
        compute='_compute_retention_risk',
        store=True,
        tracking=True,
        help='Indicates if retention amount may be forfeited'
    )
    
    # State
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='scheduled', tracking=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    
    @api.depends('scheduled_date', 'state')
    def _compute_days_overdue(self):
        """Calculate how many days overdue the follow-up is"""
        today = datetime.now().date()
        
        for rec in self:
            if rec.state in ('scheduled', 'in_progress') and rec.scheduled_date:
                days = (today - rec.scheduled_date).days
                rec.days_overdue = max(0, days)
            else:
                rec.days_overdue = 0
    
    @api.depends('candidate_working', 'issue_severity', 'retention_id')
    def _compute_retention_risk(self):
        """Flag if retention is at risk due to candidate issues"""
        for rec in self:
            rec.retention_at_risk = (
                not rec.candidate_working or
                rec.issue_severity in ['severe', 'critical']
            )
            
            # Update associated retention record
            if rec.retention_id and rec.retention_at_risk:
                if not rec.candidate_working:
                    rec.retention_id.write({
                        'candidate_status': 'absconded',
                        'risk_level': 'critical',
                    })
                elif rec.issue_severity == 'critical':
                    rec.retention_id.write({
                        'candidate_status': 'issue_major',
                        'risk_level': 'high',
                    })
    
    # ============================================================================
    # LIFECYCLE METHODS
    # ============================================================================
    
    @api.model
    def create(self, vals):
        """Create follow-up with auto-generated sequence"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'recruitment.followup'
            ) or _('New')
        return super().create(vals)
    
    def action_start(self):
        """Mark follow-up as in progress"""
        self.write({'state': 'in_progress'})
        return True
    
    def action_complete(self):
        """Mark follow-up as completed"""
        if not self.contact_notes:
            raise ValidationError(_('Please add contact notes before completing'))
        
        self.write({
            'state': 'completed',
            'completed_date': fields.Date.today(),
        })
        
        # Update retention if there are issues
        if self.retention_at_risk and self.retention_id:
            self.retention_id.write({
                'risk_notes': self.issue_description or '',
                'candidate_status': self.candidate_location,
            })
        
        return True
    
    def action_cancel(self):
        """Cancel follow-up"""
        self.write({'state': 'cancelled'})
        return True
    
    def action_schedule_next_followup(self):
        """Create next scheduled follow-up"""
        today = fields.Date.today()
        
        # Determine next follow-up based on type
        next_type_map = {
            'week_1': 'week_2',
            'week_2': 'week_4',
            'week_4': 'day_30',
            'day_30': 'day_60',
            'day_60': 'day_90',
            'day_90': 'custom',
        }
        
        next_type = next_type_map.get(self.followup_type, 'custom')
        
        # Calculate next scheduled date (usually 7 days later)
        next_date = today + timedelta(days=7)
        
        # Create next follow-up
        self.env['recruitment.followup'].create({
            'deployment_id': self.deployment_id.id,
            'followup_type': next_type,
            'scheduled_date': next_date,
            'state': 'scheduled',
        })
        
        return True
    
    def action_escalate_to_management(self):
        """Create management review activity"""
        self.write({'next_action_type': 'management_review'})
        
        # Get manager (HR manager or supervisor)
        manager = self.env.user.parent_id or self.env.user
        
        self.activity_schedule(
            activity_type_xmlid='mail.mail_activity_data_todo',
            summary=_('Urgent: Placement Issue - %s') % self.candidate_id.name,
            note=self.issue_description or _('Critical issue reported during follow-up'),
            user_id=manager.id,
        )
        
        return True
    
    def action_propose_replacement(self):
        """If candidate left, open wizard to find replacement"""
        if self.candidate_working:
            raise UserError(_('Candidate is still working. Cannot propose replacement.'))
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'replacement.candidate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_original_deployment_id': self.deployment_id.id,
                'default_followup_id': self.id,
            },
        }
    
    # ============================================================================
    # AUTOMATION/CRON METHODS
    # ============================================================================
    
    @api.model
    def cron_schedule_automatic_followups(self):
        """
        Cron: Auto-schedule follow-ups based on deployment date
        Creates follow-ups at: 1 week, 2 weeks, 1 month, 2 months, 3 months
        """
        # Get active deployments
        deployments = self.env['recruitment.deployment'].search([
            ('state', '=', 'deployed'),
        ])
        
        today = fields.Date.today()
        
        for deployment in deployments:
            if not deployment.deployment_date:
                continue
            
            days_deployed = (today - deployment.deployment_date).days
            
            # Create follow-ups if they don't exist
            if days_deployed == 7:
                self._create_scheduled_followup(deployment, 'week_1')
            elif days_deployed == 14:
                self._create_scheduled_followup(deployment, 'week_2')
            elif days_deployed == 30:
                self._create_scheduled_followup(deployment, 'day_30')
            elif days_deployed == 60:
                self._create_scheduled_followup(deployment, 'day_60')
            elif days_deployed == 90:
                self._create_scheduled_followup(deployment, 'day_90')
    
    def _create_scheduled_followup(self, deployment, followup_type):
        """Helper to create follow-up if it doesn't exist"""
        existing = self.search([
            ('deployment_id', '=', deployment.id),
            ('followup_type', '=', followup_type),
        ], limit=1)
        
        if not existing:
            scheduled_date = deployment.deployment_date + timedelta(
                days=self._get_days_for_followup_type(followup_type)
            )
            
            self.create({
                'deployment_id': deployment.id,
                'followup_type': followup_type,
                'scheduled_date': scheduled_date,
                'state': 'scheduled',
            })
    
    def _get_days_for_followup_type(self, followup_type):
        """Get number of days for each follow-up type"""
        days_map = {
            'week_1': 7,
            'week_2': 14,
            'week_4': 28,
            'day_30': 30,
            'day_60': 60,
            'day_90': 90,
        }
        return days_map.get(followup_type, 7)
    
    @api.model
    def cron_mark_overdue_followups(self):
        """Cron: Create activities for overdue follow-ups"""
        today = fields.Date.today()
        
        overdue = self.search([
            ('state', '=', 'scheduled'),
            ('scheduled_date', '<', today),
        ])
        
        for followup in overdue:
            # Get display value for followup_type selection
            followup_type_display = dict(
                followup._fields['followup_type'].selection
            ).get(followup.followup_type, followup.followup_type)
            
            followup.activity_schedule(
                activity_type_xmlid='mail.mail_activity_data_todo',
                summary=_('Overdue: %s Follow-up for %s') % (
                    followup_type_display,
                    followup.candidate_id.name
                ),
                note=_('This follow-up was scheduled for %s') % followup.scheduled_date,
                user_id=followup.env.user.id,
            )
