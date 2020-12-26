# -*- coding: utf-8 -*-
from odoo import fields, models, api


class GenerateAssignedDocSub(models.TransientModel):
    _name = "generate.assigned.doc.sub.wiz"

    subcontractor_id = fields.Many2one("res.partner", "Subcontractor", domain=[('is_subcontractor', '=', True)])
    task_id = fields.Many2one('project.task')
    project_id = fields.Many2one('project.project', related='task_id.project_id')
    assigned_line_ids = fields.Many2many('assigned.line')
    engineer_type = fields.Selection([('responsible', 'Responsible'), ('planned', 'Planned')], "Engineer",
                                     default='responsible')
    responsible_engineer = fields.Many2one('res.users', "Responsible Engineer")
    planned_engineer = fields.Many2one('res.users', "Planned Engineer")

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

        serial = str(self.task_id.project_id.project_code or '') +\
                 "/" + self.task_id.main_item_id.name + "/" + self.subcontractor_id.name
        print("###################################################")
        print(serial)
        print("###################################################")
        self.env['assigned.doc.sub'].create({
            'assigned_date': fields.Date.today(),
            'task_id': self.task_id.id,
            'assigned_line_ids': [(4, al.id) for al in self.assigned_line_ids],
            'creator_id': self._compute_creator_id(),
            'subcontractor_id': self.subcontractor_id.id,
            'serial': serial
        })

    def _compute_creator_id(self):
        if self.engineer_type == 'planned':
            return self.planned_engineer.id
        elif self.engineer_type == 'responsible':
            return self.responsible_engineer.id
