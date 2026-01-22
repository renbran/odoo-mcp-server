# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons.http_routing.models.ir_http import slug


class PropertyDetails(models.Model):
    _inherit = 'property.details'

    # Website Publishing Fields
    is_published_website = fields.Boolean(
        string='Published on Website',
        default=False,
        help='Check to make this property visible on the public website'
    )
    website_published_date = fields.Datetime(
        string='Website Published Date',
        readonly=True,
        copy=False
    )
    website_views_count = fields.Integer(
        string='Website Views',
        default=0,
        readonly=True,
        help='Number of times this property has been viewed on the website'
    )
    website_inquiry_count = fields.Integer(
        string='Website Inquiries',
        default=0,
        readonly=True,
        help='Number of inquiries received through the website'
    )
    
    # SEO Fields
    website_url = fields.Char(
        string='Website URL',
        compute='_compute_website_url',
        help='Public URL of the property on the website'
    )
    website_meta_title = fields.Char(
        string='Meta Title',
        help='SEO: Page title (50-60 characters recommended)'
    )
    website_meta_description = fields.Text(
        string='Meta Description',
        help='SEO: Page description (150-160 characters recommended)'
    )
    website_meta_keywords = fields.Char(
        string='Meta Keywords',
        help='SEO: Keywords separated by commas'
    )
    
    # Featured/Premium Status
    website_featured = fields.Boolean(
        string='Featured on Website',
        default=False,
        help='Featured properties appear at the top of listings'
    )
    website_package = fields.Selection([
        ('standard', 'Standard Listing'),
        ('premium', 'Premium Listing'),
        ('featured', 'Featured Listing'),
    ], string='Website Package', default='standard')
    
    website_package_expiry = fields.Date(
        string='Package Expiry Date',
        help='Date when the current package expires'
    )

    @api.depends('name')
    def _compute_website_url(self):
        """Generate SEO-friendly URL for the property"""
        for record in self:
            if record.id:
                record.website_url = f'/properties/{slug(record)}'
            else:
                record.website_url = False

    def action_publish_website(self):
        """Publish property to website"""
        self.ensure_one()
        self.write({
            'is_published_website': True,
            'website_published_date': fields.Datetime.now()
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Published'),
                'message': _('Property has been published to the website'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_unpublish_website(self):
        """Unpublish property from website"""
        self.ensure_one()
        self.write({'is_published_website': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Unpublished'),
                'message': _('Property has been removed from the website'),
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_open_publish_wizard(self):
        """Open wizard for multi-platform publishing"""
        self.ensure_one()
        return {
            'name': _('Publish Property'),
            'type': 'ir.actions.act_window',
            'res_model': 'property.publish.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_property_id': self.id,
            }
        }

    def increment_website_views(self):
        """Increment view counter (called from controller)"""
        self.sudo().write({'website_views_count': self.website_views_count + 1})

    @api.model
    def get_published_properties(self, domain=None, limit=None, order=None):
        """Get published properties for website display"""
        base_domain = [('is_published_website', '=', True)]
        if domain:
            base_domain.extend(domain)
        
        if not order:
            # Featured first, then premium, then by date
            order = 'website_featured desc, website_package desc, website_published_date desc'
        
        return self.search(base_domain, limit=limit, order=order)
