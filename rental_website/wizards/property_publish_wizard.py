# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PropertyPublishWizard(models.TransientModel):
    _name = 'property.publish.wizard'
    _description = 'Property Publishing Wizard'

    property_id = fields.Many2one(
        'property.details',
        string='Property',
        required=True,
        readonly=True
    )
    
    # Publishing Options
    publish_to_website = fields.Boolean(
        string='Publish to Website',
        default=True,
        help='Make this property visible on your website'
    )
    
    publish_to_portals = fields.Boolean(
        string='Publish to Portals',
        default=True,
        help='Syndicate this property to external portals'
    )
    
    portal_publish_mode = fields.Selection([
        ('all', 'All Active Portals'),
        ('selected', 'Selected Portals Only'),
    ], string='Portal Publish Mode', default='all')
    
    portal_ids = fields.Many2many(
        'portal.connector',
        string='Select Portals',
        domain=[('active', '=', True)]
    )
    
    # Auto-populated fields display
    selected_portals_count = fields.Integer(
        string='Portals Count',
        compute='_compute_selected_portals_count'
    )
    
    @api.depends('portal_publish_mode', 'portal_ids')
    def _compute_selected_portals_count(self):
        for wizard in self:
            if wizard.portal_publish_mode == 'all':
                wizard.selected_portals_count = self.env['portal.connector'].search_count([
                    ('active', '=', True),
                    ('include_in_bulk_publish', '=', True)
                ])
            else:
                wizard.selected_portals_count = len(wizard.portal_ids)

    @api.onchange('portal_publish_mode')
    def _onchange_portal_publish_mode(self):
        """Auto-select all portals when mode is 'all'"""
        if self.portal_publish_mode == 'all':
            self.portal_ids = self.env['portal.connector'].search([
                ('active', '=', True),
                ('include_in_bulk_publish', '=', True)
            ])

    def action_publish(self):
        """Execute the publishing process"""
        self.ensure_one()
        
        if not self.publish_to_website and not self.publish_to_portals:
            raise UserError(_('Please select at least one publishing option'))
        
        property_obj = self.property_id
        messages = []
        
        # Publish to Website
        if self.publish_to_website:
            property_obj.write({
                'is_published_website': True,
                'website_published_date': fields.Datetime.now()
            })
            messages.append('✓ Published to Website')
        
        # Publish to Portals
        if self.publish_to_portals:
            portals_to_publish = self.portal_ids if self.portal_publish_mode == 'selected' else self.env['portal.connector'].search([
                ('active', '=', True),
                ('include_in_bulk_publish', '=', True)
            ])
            
            if not portals_to_publish:
                raise UserError(_('No active portals found for publishing'))
            
            # Create or update portal lines
            portal_line_obj = self.env['property.portal.line']
            for portal in portals_to_publish:
                existing_line = portal_line_obj.search([
                    ('property_id', '=', property_obj.id),
                    ('portal_id', '=', portal.id)
                ], limit=1)
                
                if existing_line:
                    # Update existing
                    existing_line.write({
                        'status': 'published',
                        'last_sync': fields.Datetime.now(),
                    })
                else:
                    # Create new
                    portal_line_obj.create({
                        'property_id': property_obj.id,
                        'portal_id': portal.id,
                        'external_id': f'{portal.code}_{property_obj.id}',
                        'status': 'published',
                        'last_sync': fields.Datetime.now(),
                    })
            
            messages.append(f'✓ Published to {len(portals_to_publish)} portal(s)')
        
        # Show success notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Publishing Successful'),
                'message': '<br/>'.join(messages),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
