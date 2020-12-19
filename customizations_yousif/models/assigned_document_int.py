# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AssignedDocumentInternal(models.Model):
    _name = "assigned.doc.int"

    company_operation_costing_account_id = fields.Many2one("account.account")
    assigned_date = fields.Date()
    creator_id = fields.Many2one("res.users")
    # main_item = fields.Many2one()
    task_id = fields.Many2one('project.task')
    project_id = fields.Many2one('project.project', related='task_id.project_id')
    assigned_line_ids = fields.Many2many("assigned.line")

    # TODO: Define the actions of the internal document object
