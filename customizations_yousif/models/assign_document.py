# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AssignedDocument(models.Model):
    _name = "assigned.doc.sub"
    serial = fields.Char()
    subcontractor = fields.Many2one("res.partner")
    main_item = fields.Many2one()
    task = fields.Many2one()
    project = fields.Many2one()
