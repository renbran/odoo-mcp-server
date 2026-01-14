# -*- coding: utf-8 -*-
"""
Enhanced Contract Model
Improvements:
- Added field tracking
- Auto-create deployment on signing
- Smart buttons
- Document management
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class RecruitmentContract(models.Model):
    _name = 'recruitment.contract'
    _inherit = 'recruitment.contract'
    _description = 'Recruitment Contract'
    _order = 'create_date desc, id desc'

    # ENHANCED FIELDS with tracking
    name = fields.Char(tracking=True)
    state = fields.Selection(tracking=True)
    application_id = fields.Many2one('recruitment.application', tracking=True)
    candidate_id = fields.Many2one('recruitment.candidate', tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
    salary_proposed = fields.Float(tracking=True)
    start_date = fields.Date(tracking=True)
    end_date = fields.Date(tracking=True)
    
    # Smart button fields
    deployment_id = fields.Many2one('recruitment.deployment', string='Deployment')
    deployment_count = fields.Integer('Deployments', compute='_compute_deployment_count')
    
    @api.depends('deployment_id')
    def _compute_deployment_count(self):
        """Compute deployment count"""
        for record in self:
            record.deployment_count = 1 if record.deployment_id else 0

    def action_view_deployment(self):
        """View related deployment"""
        self.ensure_one()
        if not self.deployment_id:
            return self.action_create_deployment()
        
        return {
            'name': 'Deployment',
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.deployment',
            'res_id': self.deployment_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_sign(self):
        """Override to auto-create deployment when signed"""
        res = super(RecruitmentContract, self).action_sign()
        
        for record in self:
            if not record.deployment_id:
                record.action_create_deployment()
        
        return res

    def action_create_deployment(self):
        """Create deployment from contract"""
        self.ensure_one()
        
        if not self.candidate_id:
            raise ValidationError("Candidate is required to create deployment")
        
        deployment_vals = {
            'name': f"Deployment - {self.candidate_id.name}",
            'contract_id': self.id,
            'candidate_id': self.candidate_id.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'state': 'draft',
            'job_id': self.job_id.id if hasattr(self, 'job_id') else False,
            'job_requisition_id': self.application_id.job_requisition_id.id if self.application_id else False,
            'expected_arrival_date': fields.Date.today() + timedelta(days=30),
        }
        
        deployment = self.env['recruitment.deployment'].create(deployment_vals)
        self.deployment_id = deployment.id
        
        # Schedule deployment activities
        deployment.activity_schedule(
            'recruitment_uae.mail_activity_deployment_preparation',
            user_id=self.env.user.id,
            summary='Prepare deployment documentation and logistics'
        )
        
        deployment.activity_schedule(
            'recruitment_uae.mail_activity_visa_processing',
            user_id=self.env.user.id,
            date_deadline=fields.Date.today() + timedelta(days=7),
            summary='Process visa and work permit'
        )
        
        # Log in chatter
        self.message_post(
            body=f"Deployment record <a href='#' data-oe-model='recruitment.deployment' data-oe-id='{deployment.id}'>{deployment.name}</a> created",
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.deployment',
            'res_id': deployment.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # VALIDATION
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validate dates"""
        for record in self:
            if record.end_date and record.start_date and record.end_date < record.start_date:
                raise ValidationError("End date cannot be before start date")

    @api.constrains('salary_proposed')
    def _check_salary(self):
        """Validate salary"""
        for record in self:
            if record.salary_proposed < 0:
                raise ValidationError("Salary cannot be negative")

    @api.onchange('application_id')
    def _onchange_application_id(self):
        """Auto-populate from application"""
        if self.application_id:
            if not self.candidate_id:
                self.candidate_id = self.application_id.candidate_id
            if not self.partner_id:
                self.partner_id = self.application_id.partner_id
            if not self.salary_proposed:
                self.salary_proposed = self.application_id.salary_expected

    @api.model
    def create(self, vals):
        """Override create to schedule activities"""
        record = super(RecruitmentContract, self).create(vals)
        
        if record.state == 'draft':
            record.activity_schedule(
                'recruitment_uae.mail_activity_contract_review',
                user_id=self.env.user.id,
                summary='Review and finalize contract terms'
            )
        
        return record

    def write(self, vals):
        """Track state changes"""
        old_state = {rec.id: rec.state for rec in self}
        res = super(RecruitmentContract, self).write(vals)
        
        if 'state' in vals:
            for record in self:
                if old_state[record.id] != record.state:
                    record._notify_stage_change(old_state[record.id], record.state)
        
        return res

    def _notify_stage_change(self, old_state, new_state):
        """Notify on stage change"""
        self.ensure_one()
        
        messages = {
            'sent': 'Contract sent to candidate for review',
            'signed': 'Contract signed - deployment initiated',
            'cancelled': 'Contract cancelled',
        }
        
        if new_state in messages:
            self.message_post(
                body=messages[new_state],
                message_type='notification',
                subtype_xmlid='mail.mt_comment'
            )
            
            # Subscribe relevant partners
            if self.candidate_id.partner_id:
                self.message_subscribe(partner_ids=[self.candidate_id.partner_id.id])
