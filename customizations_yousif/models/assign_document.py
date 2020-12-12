from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class assign_document(models.Model):
    _name = "assigned.doc.sub"
    serial = fields.Char()
    subcontractor = fields.Many2one("res.partner")
    main_item = fields.Many2one()
    task = fields.Many2one()
    project = fields.Many2one()

class assign_document_internal(models.Model):
    _name = "assigned.doc.inter"
    