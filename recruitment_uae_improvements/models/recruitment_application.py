# -*- coding: utf-8 -*-
"""
Enhanced Application Model
Improvements:
- Added field tracking
- Auto-create contract on acceptance
- Smart buttons
- Enhanced validation
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RecruitmentApplication(models.Model):
    _name = 'recruitment.application'
    _inherit = 'recruitment.application'
    _description = 'Recruitment Application'
    _order = 'create_date desc, id desc'

    # ENHANCED FIELDS with tracking
    name = fields.Char(tracking=True)
    state = fields.Selection(tracking=True)
    job_requisition_id = fields.Many2one('recruitment.job.requisition', tracking=True)
    candidate_id = fields.Many2one('recruitment.candidate', tracking=True)
    job_id = fields.Many2one('hr.job', tracking=True)
    department_id = fields.Many2one('hr.department', tracking=True)
    salary_expected = fields.Float(tracking=True)
    
    # Partner field (if missing)
    partner_id = fields.Many2one('res.partner', string='Client', tracking=True)
    
    # Smart button fields
    contract_id = fields.Many2one('recruitment.contract', string='Contract')
    contract_count = fields.Integer('Contracts', compute='_compute_contract_count')

    @api.depends('contract_id')
    def _compute_contract_count(self):
        """Compute contract count"""
        for record in self:
            record.contract_count = 1 if record.contract_id else 0

    def action_view_contract(self):
        """View related contract"""
        self.ensure_one()
        if not self.contract_id:
            return self.action_create_contract()
        
        return {
            'name': 'Contract',
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.contract',
            'res_id': self.contract_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_accept(self):
        """Override to auto-create contract when accepted"""
        res = super(RecruitmentApplication, self).action_accept()
        
        for record in self:
            if not record.contract_id:
                record.action_create_contract()
        
        return res

    def action_create_contract(self):
        """Create contract from application"""
        self.ensure_one()
        
        if not self.candidate_id:
            raise ValidationError("Please select a candidate before creating a contract")
        
        contract_vals = {
            'name': f"Contract - {self.candidate_id.name}",
            'application_id': self.id,
            'candidate_id': self.candidate_id.id,
            'partner_id': self.partner_id.id if self.partner_id else self.job_requisition_id.partner_id.id,
            'company_id': self.company_id.id,
            'state': 'draft',
            'job_id': self.job_id.id,
            'department_id': self.department_id.id,
            'salary_proposed': self.salary_expected,
        }
        
        contract = self.env['recruitment.contract'].create(contract_vals)
        self.contract_id = contract.id
        
        # Schedule contract review activity
        contract.activity_schedule(
            'recruitment_uae.mail_activity_contract_review',
            user_id=self.env.user.id,
            summary='Review and finalize contract terms'
        )
        
        # Notify via chatter
        self.message_post(
            body=f"Contract <a href='#' data-oe-model='recruitment.contract' data-oe-id='{contract.id}'>{contract.name}</a> created automatically",
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.contract',
            'res_id': contract.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # VALIDATION
    @api.constrains('salary_expected')
    def _check_salary(self):
        """Validate salary"""
        for record in self:
            if record.salary_expected < 0:
                raise ValidationError("Salary cannot be negative")

    @api.onchange('candidate_id')
    def _onchange_candidate_id(self):
        """Auto-populate from candidate"""
        if self.candidate_id:
            if not self.name:
                self.name = f"Application - {self.candidate_id.name}"
            if not self.salary_expected and self.candidate_id.expected_salary:
                self.salary_expected = self.candidate_id.expected_salary

    @api.onchange('job_requisition_id')
    def _onchange_job_requisition_id(self):
        """Auto-populate from requisition"""
        if self.job_requisition_id:
            if not self.partner_id:
                self.partner_id = self.job_requisition_id.partner_id
            if not self.job_id:
                self.job_id = self.job_requisition_id.job_id
            if not self.department_id:
                self.department_id = self.job_requisition_id.department_id

    @api.model
    def create(self, vals):
        """Override create to schedule activities"""
        record = super(RecruitmentApplication, self).create(vals)
        
        if record.state == 'draft':
            record.activity_schedule(
                'recruitment_uae.mail_activity_application_review',
                user_id=self.env.user.id,
                summary='Review and process application'
            )
        
        return record

    def write(self, vals):
        """Track state changes"""
        old_state = {rec.id: rec.state for rec in self}
        res = super(RecruitmentApplication, self).write(vals)
        
        if 'state' in vals:
            for record in self:
                if old_state[record.id] != record.state:
                    record._notify_stage_change(old_state[record.id], record.state)
        
        return res

    def _notify_stage_change(self, old_state, new_state):
        """Notify on stage change"""
        self.ensure_one()
        
        messages = {
            'submitted': 'Application submitted for review',
            'interview': 'Interview scheduled',
            'accepted': 'Application accepted - contract creation initiated',
            'rejected': 'Application rejected',
        }
        
        if new_state in messages:
            self.message_post(
                body=messages[new_state],
                message_type='notification',
                subtype_xmlid='mail.mt_comment'
            )
