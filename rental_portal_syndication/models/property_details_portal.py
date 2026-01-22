# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PropertyDetails(models.Model):
    _inherit = "property.details"

    portal_line_ids = fields.One2many(
        "property.portal.line", "property_id", string="Portal Listings"
    )
    portal_line_count = fields.Integer(compute="_compute_portal_counts")
    portal_lead_count = fields.Integer(compute="_compute_portal_counts")

    @api.depends("portal_line_ids")
    def _compute_portal_counts(self):
        """Compute portal and lead counts efficiently using batch queries"""
        # Batch count leads for all properties at once (prevents N+1 queries)
        lead_counts = {}
        if self:
            lead_data = self.env["portal.lead"].read_group(
                [("property_id", "in", self.ids)],
                ["property_id"],
                ["property_id"],
            )
            for data in lead_data:
                lead_counts[data["property_id"][0]] = data["property_id_count"]
        
        for rec in self:
            rec.portal_line_count = len(rec.portal_line_ids)
            rec.portal_lead_count = lead_counts.get(rec.id, 0)

    def action_open_portal_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Portal Listings",
            "res_model": "property.portal.line",
            "view_mode": "tree,form",
            "domain": [("property_id", "=", self.id)],
            "context": {"default_property_id": self.id},
            "target": "current",
        }

    def action_open_portal_leads(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Portal Leads",
            "res_model": "portal.lead",
            "view_mode": "tree,form",
            "domain": [("property_id", "=", self.id)],
            "context": {"default_property_id": self.id},
            "target": "current",
        }
