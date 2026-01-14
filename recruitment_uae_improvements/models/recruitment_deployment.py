# -*- coding: utf-8 -*-
"""
Enhanced Deployment Model
Improvements:
- Added field tracking
- Travel and logistics management
- Document tracking
- Arrival confirmation
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RecruitmentDeployment(models.Model):
    _name = 'recruitment.deployment'
    _inherit = 'recruitment.deployment'
    _description = 'Recruitment Deployment'
    _order = 'expected_arrival_date desc, id desc'

    # ENHANCED FIELDS with tracking
    name = fields.Char(tracking=True)
    state = fields.Selection(tracking=True)
    contract_id = fields.Many2one('recruitment.contract', tracking=True)
    candidate_id = fields.Many2one('recruitment.candidate', tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
    expected_arrival_date = fields.Date(tracking=True)
    actual_arrival_date = fields.Date(tracking=True)
    flight_details = fields.Text(tracking=True)
    visa_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Visa Status', tracking=True)
    
    # Smart buttons
    retention_ids = fields.One2many('recruitment.retention', 'deployment_id', string='Retentions')
    retention_count = fields.Integer('Retentions', compute='_compute_retention_count')

    @api.depends('retention_ids')
    def _compute_retention_count(self):
        """Compute retention count"""
        for record in self:
            record.retention_count = len(record.retention_ids)

    def action_view_retentions(self):
        """View retention records"""
        self.ensure_one()
        return {
            'name': 'Retention Records',
            'type': 'ir.actions.act_window',
            'res_model': 'recruitment.retention',
            'view_mode': 'tree,form',
            'domain': [('deployment_id', '=', self.id)],
            'context': {
                'default_deployment_id': self.id,
                'default_candidate_id': self.candidate_id.id,
                'default_partner_id': self.partner_id.id,
            }
        }

    def action_confirm_arrival(self):
        """Confirm candidate arrival"""
        self.ensure_one()
        
        self.write({
            'actual_arrival_date': fields.Date.today(),
            'state': 'arrived',
        })
        
        # Create retention record
        retention_vals = {
            'name': f"Retention - {self.candidate_id.name}",
            'deployment_id': self.id,
            'candidate_id': self.candidate_id.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'state': 'active',
            'start_date': fields.Date.today(),
        }
        
        retention = self.env['recruitment.retention'].create(retention_vals)
        
        # Schedule follow-up activities
        retention.activity_schedule(
            'recruitment_uae.mail_activity_followup_30days',
            user_id=self.env.user.id,
            date_deadline=fields.Date.today() + timedelta(days=30),
            summary='30-day follow-up check'
        )
        
        self.message_post(
            body=f"Candidate arrived successfully. Retention tracking <a href='#' data-oe-model='recruitment.retention' data-oe-id='{retention.id}'>started</a>",
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Arrival Confirmed',
                'message': 'Candidate arrival confirmed and retention tracking started',
                'type': 'success',
                'sticky': False,
            }
        }

    # VALIDATION
    @api.constrains('expected_arrival_date', 'actual_arrival_date')
    def _check_dates(self):
        """Validate dates"""
        for record in self:
            if record.actual_arrival_date and record.actual_arrival_date > fields.Date.today():
                raise ValidationError("Actual arrival date cannot be in the future")

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        """Auto-populate from contract"""
        if self.contract_id:
            if not self.candidate_id:
                self.candidate_id = self.contract_id.candidate_id
            if not self.partner_id:
                self.partner_id = self.contract_id.partner_id
            if not self.name:
                self.name = f"Deployment - {self.contract_id.candidate_id.name}"

    @api.model
    def create(self, vals):
        """Override create to schedule activities"""
        record = super(RecruitmentDeployment, self).create(vals)
        
        if record.state == 'draft':
            record.activity_schedule(
                'recruitment_uae.mail_activity_deployment_preparation',
                user_id=self.env.user.id,
                summary='Prepare deployment documentation'
            )
        
        return record

    def write(self, vals):
        """Track state changes"""
        old_state = {rec.id: rec.state for rec in self}
        res = super(RecruitmentDeployment, self).write(vals)
        
        if 'state' in vals:
            for record in self:
                if old_state[record.id] != record.state:
                    record._notify_stage_change(old_state[record.id], record.state)
        
        return res

    def _notify_stage_change(self, old_state, new_state):
        """Notify on stage change"""
        self.ensure_one()
        
        messages = {
            'processing': 'Deployment documentation in progress',
            'visa_applied': 'Visa application submitted',
            'visa_approved': 'Visa approved - arranging travel',
            'traveling': 'Candidate en route',
            'arrived': 'Candidate arrived successfully',
            'cancelled': 'Deployment cancelled',
        }
        
        if new_state in messages:
            self.message_post(
                body=messages[new_state],
                message_type='notification',
                subtype_xmlid='mail.mt_comment'
            )
