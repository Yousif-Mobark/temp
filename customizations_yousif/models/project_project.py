# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_type = fields.Selection([
        ('supply', 'Supply Only'),
        ('installation', 'Installation Only'),
        ('supply_installation', 'Supply and Installation'),
    ], string='Project Type', translate=True)

    project_code = fields.Char("Project Code")
