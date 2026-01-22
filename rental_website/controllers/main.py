# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
import json


_logger = logging.getLogger(__name__)

class PropertyWebsiteController(http.Controller):

    def _render_property_detail(self, property):
        """Render property detail page with safety checks and similar items."""

        if not property or not property.is_published_website:
            return request.render('website.404')

        property.sudo().increment_website_views()

        similar_domain = [
            ('is_published_website', '=', True),
            ('id', '!=', property.id),
            ('type', '=', property.type),
        ]
        similar_properties = request.env['property.details'].search(similar_domain, limit=4)

        values = {
            'property': property,
            'similar_properties': similar_properties,
            'main_object': property,
        }

        return request.render('rental_website.property_detail_page', values)

    @http.route(['/properties', '/properties/page/<int:page>'], type='http', auth='public', website=True)
    def property_listing(self, page=1, search='', min_price=0, max_price=0, 
                         property_type='', location='', bedrooms='', **kw):
        """Property listing page with search and filters"""
        
        Property = request.env['property.details']
        
        # Build search domain
        domain = [('is_published_website', '=', True)]
        
        if search:
            # Match on core address/name fields; description field does not exist on property.details
            domain.extend([
                '|', '|',
                ('name', 'ilike', search),
                ('street', 'ilike', search),
                ('city_id.name', 'ilike', search),
            ])
        
        if min_price:
            domain.append(('price', '>=', float(min_price)))
        
        if max_price:
            domain.append(('price', '<=', float(max_price)))
        
        if property_type:
            domain.append(('type', '=', property_type))
        
        if location:
            # Match against textual city or related location records (city/state/country)
            domain.extend([
                '|', '|', '|',
                ('city_id.name', 'ilike', location),
                ('state_id.name', 'ilike', location),
                ('country_id.name', 'ilike', location),
                ('region_id.name', 'ilike', location),
            ])
        
        if bedrooms:
            domain.append(('bed', '=', int(bedrooms)))
        
        # Pagination
        properties_per_page = 12
        total_properties = Property.search_count(domain)
        pager = request.website.pager(
            url='/properties',
            total=total_properties,
            page=page,
            step=properties_per_page,
            url_args={'search': search, 'min_price': min_price, 'max_price': max_price,
                     'property_type': property_type, 'location': location, 'bedrooms': bedrooms}
        )
        
        # Get properties for current page
        properties = Property.search(
            domain,
            limit=properties_per_page,
            offset=pager['offset'],
            order='website_featured desc, website_package desc, website_published_date desc'
        )
        
        # Get filter options
        property_types = Property.search([('is_published_website', '=', True)])._fields['type'].selection
        bedroom_options = sorted(set(Property.search([('is_published_website', '=', True)]).mapped('bed')))
        
        values = {
            'properties': properties,
            'pager': pager,
            'search': search,
            'min_price': min_price,
            'max_price': max_price,
            'property_type': property_type,
            'location': location,
            'bedrooms': bedrooms,
            'property_types': property_types,
            'bedroom_options': bedroom_options,
            'total_count': total_properties,
        }
        
        return request.render('rental_website.property_listing_page', values)

    @http.route(['/properties/<model("property.details"):property>'], type='http', auth='public', website=True)
    def property_detail(self, property, **kw):
        """Property detail page"""

        return self._render_property_detail(property)

    @http.route(['/properties/<string:property_slug>'], type='http', auth='public', website=True)
    def property_detail_slug(self, property_slug, **kw):
        """Fallback slug route when the model converter fails to resolve the record."""

        Property = request.env['property.details'].sudo()

        record = Property.browse(False)
        slug_parts = (property_slug or '').split('-')
        if slug_parts and slug_parts[-1].isdigit():
            record_id = int(slug_parts[-1])
            record = Property.browse(record_id)

        if not record:
            record = Property.search([('website_url', '=', f'/properties/{property_slug}')], limit=1)

        return self._render_property_detail(record)

    @http.route(['/properties/ajax/search'], type='json', auth='public', website=True)
    def ajax_property_search(self, search='', filters=None):
        """AJAX endpoint for live property search"""
        
        Property = request.env['property.details']
        domain = [('is_published_website', '=', True)]
        
        if search:
            domain.extend([
                '|', '|',
                ('name', 'ilike', search),
                ('street', 'ilike', search),
                ('city_id.name', 'ilike', search),
            ])
        
        if filters:
            filters = json.loads(filters) if isinstance(filters, str) else filters
            if filters.get('min_price'):
                domain.append(('price', '>=', float(filters['min_price'])))
            if filters.get('max_price'):
                domain.append(('price', '<=', float(filters['max_price'])))
            if filters.get('type'):
                domain.append(('type', '=', filters['type']))
            if filters.get('bedrooms'):
                domain.append(('bed', '=', int(filters['bedrooms'])))
        
        properties = Property.search(domain, limit=20)
        
        results = []
        for prop in properties:
            results.append({
                'id': prop.id,
                'name': prop.name,
                'price': prop.price,
                'type': prop.type,
                'bedrooms': prop.bed,
                'url': f'/properties/{slug(prop)}',
                'image': f'/web/image/property.details/{prop.id}/image_1920',
            })
        
        return {'properties': results, 'count': len(results)}

    @http.route(['/properties/contact'], type='http', auth='public', website=True, csrf=True, methods=['POST'])
    def property_contact_form(self, **post):
        """Handle property inquiry form submissions"""
        
        property_id = int(post.get('property_id', 0))
        name = post.get('name', '')
        email = post.get('email', '')
        phone = post.get('phone', '')
        message = post.get('message', '')
        
        if property_id and name and email:
            Property = request.env['property.details'].sudo()
            property_obj = Property.browse(property_id)

            # Build property URL for emails and logging
            base_url = (request.httprequest.host_url or '').rstrip('/')
            property_url = property_obj.website_url or f"/properties/{property_id}"
            full_property_url = f"{base_url}{property_url}"

            # Log message on property
            if property_obj.exists():
                property_obj.message_post(
                    body=f"""
                        <h3>Website Inquiry</h3>
                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Phone:</strong> {phone or 'Not provided'}</p>
                        <p><strong>Message:</strong><br/>{message}</p>
                        <p><strong>Property:</strong> <a href='{full_property_url}'>{property_obj.name}</a></p>
                    """,
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

            # Create CRM lead if CRM is installed
            lead = None
            try:
                crm_model = request.env['crm.lead'].sudo()
                lead_vals = {
                    'name': f"[Property Inquiry] {property_obj.name if property_obj.exists() else 'Property'}",
                    'contact_name': name,
                    'email_from': email,
                    'phone': phone or False,
                    'property_id': property_obj.id if property_obj.exists() else False,
                    'type': 'lead',
                    'priority': '2',
                    'description': (
                        f"Property: {property_obj.name if property_obj.exists() else 'N/A'}\n"
                        f"URL: {full_property_url}\n\n"
                        f"Message:\n{message}"
                    ),
                }
                lead = crm_model.create(lead_vals)
            except Exception as exc:  # CRM not installed or creation failed
                _logger.info('Skipping CRM lead creation for inquiry on property_id %s: %s', property_id, exc)

            # Persist inquiry record and increment counter for backend visibility
            inquiry = request.env['property.website.inquiry'].sudo().create({
                'property_id': property_obj.id if property_obj.exists() else False,
                'lead_id': lead.id if lead else False,
                'name': name,
                'email': email,
                'phone': phone,
                'message': message,
                'property_url': full_property_url,
            })
            if property_obj.exists():
                property_obj.sudo().write({'website_inquiry_count': property_obj.website_inquiry_count + 1})

            # Send notification email to staff
            mail_env = request.env['mail.mail'].sudo()
            safe_message_html = (message or '').replace('\n', '<br/>')
            admin_body = f"""
                <div style='font-family:Poppins,Montserrat,sans-serif;color:#1F2937;'>
                    <h2 style='color:#1E3A8A;margin-bottom:8px;'>New Property Inquiry</h2>
                    <p style='margin:0 0 12px 0;'>A new inquiry was submitted on the website.</p>
                    <table style='border-collapse:collapse;width:100%;max-width:640px;font-size:14px;'>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;'>Property</td><td style='padding:6px 0;'><a href='{full_property_url}' style='color:#1E3A8A;text-decoration:none;'>{property_obj.name if property_obj.exists() else 'Property'}</a></td></tr>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;'>Name</td><td style='padding:6px 0;'>{name}</td></tr>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;'>Email</td><td style='padding:6px 0;'>{email}</td></tr>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;'>Phone</td><td style='padding:6px 0;'>{phone or 'Not provided'}</td></tr>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;vertical-align:top;'>Message</td><td style='padding:6px 0;'>{safe_message_html}</td></tr>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;'>Lead</td><td style='padding:6px 0;'>{(lead and lead.display_name) or 'Created in property chatter'}</td></tr>
                    </table>
                    <p style='margin-top:16px;color:#4B5563;'>This inquiry was submitted via Scholarix Real Estate website.</p>
                </div>
            """

            mail_env.create({
                'subject': f"[Inquiry] {property_obj.name if property_obj.exists() else 'Property'}",
                'email_to': 'm.guido@scholarixglobal.com',
                'email_cc': 'info@sgctech.ai',
                'body_html': admin_body,
                'auto_delete': True,
            }).send()

            # Send acknowledgment to inquirer
            ack_body = f"""
                <div style='font-family:Poppins,Montserrat,sans-serif;color:#1F2937;'>
                    <h2 style='color:#1E3A8A;margin-bottom:8px;'>We received your inquiry</h2>
                    <p style='margin:0 0 12px 0;'>Hi {name},</p>
                    <p style='margin:0 0 12px 0;'>Thank you for your interest in <strong>{property_obj.name if property_obj.exists() else 'our property'}</strong>. Our team will contact you shortly.</p>
                    <p style='margin:0 0 12px 0;'>Property link: <a href='{full_property_url}' style='color:#1E3A8A;text-decoration:none;'>{full_property_url}</a></p>
                    <p style='margin:0 0 12px 0;'>Summary of your inquiry:</p>
                    <table style='border-collapse:collapse;width:100%;max-width:640px;font-size:14px;'>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;'>Name</td><td style='padding:6px 0;'>{name}</td></tr>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;'>Email</td><td style='padding:6px 0;'>{email}</td></tr>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;'>Phone</td><td style='padding:6px 0;'>{phone or 'Not provided'}</td></tr>
                        <tr><td style='padding:6px 0;width:120px;color:#4B5563;vertical-align:top;'>Message</td><td style='padding:6px 0;'>{safe_message_html}</td></tr>
                    </table>
                    <p style='margin-top:16px;color:#4B5563;'>Thank you,<br/>Scholarix Real Estate Team</p>
                </div>
            """

            mail_env.create({
                'subject': f"We received your inquiry for {property_obj.name if property_obj.exists() else 'the property'}",
                'email_to': email,
                'body_html': ack_body,
                'auto_delete': True,
            }).send()

            # Redirect back to the property with a submitted flag for UI feedback
            target_url = f"{property_url}?submitted=1"
            return request.redirect(target_url)
        
        return request.redirect('/properties')

    @http.route(['/properties/thank-you'], type='http', auth='public', website=True)
    def property_thank_you(self, **kw):
        """Thank you page after inquiry submission"""
        return request.render('rental_website.property_thank_you_page')
