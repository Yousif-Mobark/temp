# -*- coding: utf-8 -*-
from odoo import fields, models, api


class GenerateAssignedDocInter(models.TransientModel):
    _name = "generate.assigned.doc.inter.wiz"

    company_operation_costing_account_id = fields.Many2one("account.account",
                                                           related="project_id.company_operation_account")
    # main_item = fields.Many2one()
    task_id = fields.Many2one('project.task')
    engineer_type = fields.Selection([('responsible', 'Responsible'), ('planned', 'Planned')], "Engineer",
                                     default='responsible')
    responsible_engineer = fields.Many2one('res.users', "Responsible Engineer")
    planned_engineer = fields.Many2one('res.users', "Planned Engineer")
    project_id = fields.Many2one('project.project', related='task_id.project_id')
    assigned_line_ids = fields.Many2many("assigned.line")

    def do_action(self):
        self.ensure_one()
        for task in self.project_id.task_ids:
            task.state = 'run'
        self.env['mail.message'].create({'message_type': "notification",
                                         "subtype": self.env.ref("mail.mt_comment").id,
                                         'body': "Internal Assigned Document Created",
                                         'subject': "Assigned Document",
                                         'needaction_partner_ids':
                                             [(4, self.task_id.project_id.agreement_id.project_manager.id)],
                                         'model': self._name,
                                         'res_id': self.id,
                                         })
        self.env['assigned.doc.int'].create({
            'assigned_date':  fields.Date.today(),
            'task_id': self.task_id.id,
            'assigned_line_ids': [(4, al.id) for al in self.assigned_line_ids],
            'creator_id': self._compute_creator_id(),
        })

    def _compute_creator_id(self):
        if self.engineer_type == 'planned':
            return self.planned_engineer.id
        elif self.engineer_type == 'responsible':
            return self.responsible_engineer.id
