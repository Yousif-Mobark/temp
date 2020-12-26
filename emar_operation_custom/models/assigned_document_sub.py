# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AssignedDocumentSubcontractor(models.Model):
    _name = "assigned.doc.sub"

    serial = fields.Char("Serial", readonly=1, compute='_compute_serial')
    subcontractor_id = fields.Many2one("res.partner", "Subcontractor", domain=[('is_subcontractor', '=', True)])
    assigned_date = fields.Date()
    creator_id = fields.Many2one("res.users")
    # main_item = fields.Many2one()
    task_id = fields.Many2one('project.task')
    project_id = fields.Many2one('project.project', related='task_id.project_id')
    assigned_line_ids = fields.Many2many('assigned.line')
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting for Approval'), ('running', 'Running'),
                              ('rejected', 'Rejected'), ('closed', 'Closed')], default='draft')
    _rec_name = 'serial'

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

    def _compute_serial(self):
        for rec in self:
            rec.serial =\
                str(rec.project_id.project_code or '') + "/" + str(rec.task_id.main_item_id.name or '') + "/" +\
                str(rec.subcontractor_id.name or '')
