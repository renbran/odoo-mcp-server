# -*- coding: utf-8 -*-
"""
Retention Forfeiture Wizard
Used to forfeit retention with reason documentation
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RetentionForfeitWizard(models.TransientModel):
    _name = 'retention.forfeit.wizard'
    _description = 'Retention Forfeiture Wizard'
    
    retention_id = fields.Many2one(
        'recruitment.retention',
        string='Retention Record',
        required=True,
        ondelete='cascade'
    )
    
    candidate_id = fields.Many2one(
        'recruitment.candidate',
        related='retention_id.candidate_id',
        string='Candidate',
        readonly=True,
        store=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        related='retention_id.partner_id',
        string='Client',
        readonly=True,
        store=True
    )
    
    retention_amount = fields.Monetary(
        string='Retention Amount to Forfeit',
        related='retention_id.retention_amount',
        currency_field='currency_id',
        readonly=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='retention_id.currency_id',
        readonly=True
    )
    
    forfeiture_reason = fields.Selection([
        ('absconded', 'Candidate Absconded/Missing'),
        ('early_resignation', 'Resigned Before Retention Period'),
        ('poor_performance', 'Poor Performance - Client Terminated'),
        ('misconduct', 'Misconduct/Violation'),
        ('mutual_agreement', 'Mutual Agreement'),
        ('other', 'Other'),
    ], string='Reason for Forfeiture', required=True, tracking=True)
    
    forfeiture_date = fields.Date(
        string='Forfeiture Date',
        required=True,
        default=lambda self: fields.Date.today()
    )
    
    forfeiture_notes = fields.Text(
        string='Detailed Explanation',
        required=True,
        help='Detailed explanation of why retention is being forfeited'
    )
    
    # Optional: Track replacement if applicable
    replacement_required = fields.Boolean(
        string='Replacement Required',
        help='If candidate left early and guarantee applies, mark replacement required'
    )
    
    replacement_deployment_id = fields.Many2one(
        'recruitment.deployment',
        string='Replacement Deployment',
        help='Link to replacement candidate deployment if applicable'
    )
    
    # Confirmation
    confirm_forfeiture = fields.Boolean(
        string='I confirm forfeiture of this retention amount',
        required=True
    )
    
    def action_forfeit_retention(self):
        """Execute the forfeiture of retention"""
        if not self.confirm_forfeiture:
            raise UserError(_('You must confirm forfeiture before proceeding'))
        
        # Update retention record
        self.retention_id.write({
            'state': 'forfeited',
            'retention_status': 'forfeited',
            'forfeiture_reason': self.forfeiture_reason,
            'forfeiture_date': self.forfeiture_date,
            'forfeiture_notes': self.forfeiture_notes,
            'candidate_status': self._map_reason_to_status(),
            'risk_level': 'critical',
        })
        
        # Update candidate availability if absconded
        if self.forfeiture_reason == 'absconded':
            self.candidate_id.write({
                'availability_status': 'unavailable',
            })
        
        # Create activity log for management
        self._create_forfeiture_activity()
        
        # Track replacement if applicable
        if self.replacement_required and self.replacement_deployment_id:
            self.retention_id.write({
                'replacement_count': self.retention_id.replacement_count + 1,
            })
        
        return True
    
    def _map_reason_to_status(self):
        """Map forfeiture reason to candidate status"""
        mapping = {
            'absconded': 'absconded',
            'early_resignation': 'resigned',
            'poor_performance': 'terminated',
            'misconduct': 'issue_major',
        }
        return mapping.get(self.forfeiture_reason, 'issue_major')
    
    def _create_forfeiture_activity(self):
        """Create activity for management notification"""
        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': _('Retention Forfeited: %s') % self.candidate_id.name,
            'note': _('Retention amount %s %s forfeited on %s\nReason: %s\n%s') % (
                self.retention_amount,
                self.currency_id.symbol,
                self.forfeiture_date,
                self.get_forfeiture_reason_display(),
                self.forfeiture_notes
            ),
            'res_id': self.retention_id.id,
            'res_model_id': self.env['ir.model']._get_id('recruitment.retention'),
            'user_id': self.env.user.manager_id.id or self.env.user.id,
        })
