# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AssignedLine(models.Model):
    _name = 'assigned.line'

    # TODO: Define the object which sub_working_item field refers to
    sub_working_item = fields.Many2one('project.agreement.planned')
    planned_qty = fields.Float()
    remaining_qty = fields.Float()
    assigned_qty = fields.Float()
    planned_cost = fields.Float()
