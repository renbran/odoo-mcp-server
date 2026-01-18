# -*- coding: utf-8 -*-
from odoo import fields, models


class DealStage(models.Model):
    _name = 'deal.stage'
    _description = 'Deal Stage'
    _order = 'sequence'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    is_won = fields.Boolean(string='Is Won Stage', default=False)
    is_lost = fields.Boolean(string='Is Lost Stage', default=False)
    color = fields.Integer(string='Color', default=0)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Stage name must be unique'),
    ]
