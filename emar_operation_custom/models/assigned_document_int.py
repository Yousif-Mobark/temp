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
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting for Approval'), ('running', 'Running'),
                              ('rejected', 'Rejected'), ('closed', 'Closed')], default='draft')

    def action_send_for_approval(self):
        self.env['mail.message'].create({'message_type': "notification",
                                         "subtype": self.env.ref("mail.mt_comment").id,
                                         'body': "Project Assigned",
                                         'subject': "Project Assigned",
                                         'needaction_partner_ids':
                                             [(4, self.project_id.agreement_id.project_manager.partner_id.id)],
                                         'model': self._name,
                                         'res_id': self.id,
                                         })
        self.state = 'waiting'

    def action_approve(self):
        self.env['mail.message'].create({'message_type': "notification",
                                         "subtype": self.env.ref("mail.mt_comment").id,
                                         'body': "Project Assigned",
                                         'subject': "Project Assigned",
                                         'needaction_partner_ids':
                                             [(4, self.create_uid.partner_id.id)],
                                         'model': self._name,
                                         'res_id': self.id,
                                         })
        self.state = 'running'
