# -*- coding: utf-8 -*-
"""
Enhanced Job Requisition Model
Improvements:
- Added field tracking for chatter
- Auto-create applications on approval
- Smart buttons for related records
- Enhanced validation
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class RecruitmentJobRequisition(models.Model):
    _name = 'recruitment.job.requisition'
    _inherit = 'recruitment.job.requisition'
    _description = 'Job Requisition'
    _order = 'create_date desc, id desc'

    # ENHANCED FIELDS with tracking=True
    name = fields.Char(tracking=True)
    state = fields.Selection(tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
    employee_id = fields.Many2one('hr.employee', tracking=True)
    department_id = fields.Many2one('hr.department', tracking=True)
    job_id = fields.Many2one('hr.job', tracking=True)
    expected_employees = fields.Integer(tracking=True)
    
    # Smart button computed fields
    application_ids = fields.One2many('recruitment.application', 'job_requisition_id', string='Applications')
    application_count = fields.Integer('Application Count', compute='_compute_application_count')
    contract_count = fields.Integer('Contract Count', compute='_compute_contract_count')
    deployment_count = fields.Integer('Deployment Count', compute='_compute_deployment_count')

    @api.depends('application_ids')
    def _compute_application_count(self):
        """Compute number of applications"""
        for record in self:
            record.application_count = len(record.application_ids)

    def _compute_contract_count(self):
        """Compute number of contracts from applications"""
        for record in self:
            contracts = self.env['recruitment.contract'].search([
                ('application_id.job_requisition_id', '=', record.id)
            ])
            record.contract_count = len(contracts)

    def _compute_deployment_count(self):
        """Compute number of deployments"""
        for record in self:
            deployments = self.env['recruitment.deployment'].search([
                ('job_requisition_id', '=', record.id)
            ])
            record.deployment_count = len(deployments)

    # SMART BUTTON ACTIONS
    def action_view_applications(self):
        """View related applications"""
        self.ensure_one()
        return {
            'name': 'Applications',
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.application',
            'view_mode': 'tree,form',
            'domain': [('job_requisition_id', '=', self.id)],
            'context': {
                'default_job_requisition_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_job_id': self.job_id.id,
                'default_department_id': self.department_id.id,
            }
        }

    def action_view_contracts(self):
        """View related contracts"""
        self.ensure_one()
        contracts = self.env['recruitment.contract'].search([
            ('application_id.job_requisition_id', '=', self.id)
        ])
        return {
            'name': 'Contracts',
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.contract',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', contracts.ids)],
        }

    def action_view_deployments(self):
        """View related deployments"""
        self.ensure_one()
        return {
            'name': 'Deployments',
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.deployment',
            'view_mode': 'tree,form',
            'domain': [('job_requisition_id', '=', self.id)],
        }

    # AUTOMATED WORKFLOW
    def action_approve(self):
        """Override to auto-create applications when approved"""
        res = super(RecruitmentJobRequisition, self).action_approve()
        
        for record in self:
            # Schedule activity for creating applications
            record.activity_schedule(
                'recruitment_uae.mail_activity_create_applications',
                user_id=self.env.user.id,
                summary=f'Create applications for {record.expected_employees} positions'
            )
            
            # Log in chatter
            record.message_post(
                body=f"Job requisition approved. Ready to create applications for {record.expected_employees} positions.",
                message_type='notification',
                subtype_xmlid='mail.mt_comment'
            )
        
        return res

    def action_create_applications(self):
        """Manually create application records"""
        self.ensure_one()
        
        applications_created = 0
        for i in range(self.expected_employees):
            application_vals = {
                'name': f"{self.name} - Position {i+1}",
                'job_requisition_id': self.id,
                'partner_id': self.partner_id.id,
                'company_id': self.company_id.id,
                'state': 'draft',
                'job_id': self.job_id.id,
                'department_id': self.department_id.id,
            }
            
            application = self.env['recruitment.application'].create(application_vals)
            applications_created += 1
        
        # Mark activity as done
        activity = self.activity_ids.filtered(
            lambda a: a.activity_type_id == self.env.ref('recruitment_uae.mail_activity_create_applications')
        )
        if activity:
            activity.action_done()
        
        # Log success
        self.message_post(
            body=f"Created {applications_created} application records automatically",
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Applications Created',
                'message': f'{applications_created} applications created successfully',
                'type': 'success',
                'sticky': False,
            }
        }

    # VALIDATION
    @api.constrains('expected_employees')
    def _check_expected_employees(self):
        """Validate expected employees"""
        for record in self:
            if record.expected_employees <= 0:
                raise ValidationError("Expected employees must be greater than 0")
            if record.expected_employees > 1000:
                raise ValidationError("Expected employees cannot exceed 1000. Please create multiple requisitions.")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Auto-populate partner-related fields"""
        if self.partner_id:
            # Auto-fill contact information
            if not self.contact_person:
                self.contact_person = self.partner_id.name
            if not self.contact_email:
                self.contact_email = self.partner_id.email
            if not self.contact_phone:
                self.contact_phone = self.partner_id.phone

    @api.onchange('job_id')
    def _onchange_job_id(self):
        """Auto-populate job-related fields"""
        if self.job_id:
            if not self.department_id:
                self.department_id = self.job_id.department_id
            if not self.job_description:
                self.job_description = self.job_id.description

    # OVERRIDE CREATE/WRITE for activity tracking
    @api.model
    def create(self, vals):
        """Override create to schedule initial activities"""
        record = super(RecruitmentJobRequisition, self).create(vals)
        
        # Schedule review activity
        if record.state == 'draft':
            record.activity_schedule(
                'recruitment_uae.mail_activity_requisition_review',
                user_id=record.employee_id.user_id.id if record.employee_id.user_id else self.env.user.id,
                summary='Review and submit job requisition'
            )
        
        return record

    def write(self, vals):
        """Override write to track state changes"""
        old_state = {rec.id: rec.state for rec in self}
        res = super(RecruitmentJobRequisition, self).write(vals)
        
        if 'state' in vals:
            for record in self:
                if old_state[record.id] != record.state:
                    record._notify_stage_change(old_state[record.id], record.state)
        
        return res

    def _notify_stage_change(self, old_state, new_state):
        """Send notifications on stage change"""
        self.ensure_one()
        
        stage_messages = {
            'submitted': 'Job requisition submitted for approval',
            'approved': 'Job requisition approved - ready to create applications',
            'rejected': 'Job requisition rejected',
            'cancelled': 'Job requisition cancelled',
        }
        
        if new_state in stage_messages:
            self.message_post(
                body=stage_messages[new_state],
                message_type='notification',
                subtype_xmlid='mail.mt_comment'
            )
            
            # Notify followers
            self.message_subscribe(partner_ids=self.partner_id.ids)
