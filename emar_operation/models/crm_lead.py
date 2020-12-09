# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError

class Lead(models.Model):
    _name = "crm.lead"
    _inherit = "crm.lead"

    is_project = fields.Boolean(string="Is a Project", translate=True, default=False, track_visibility='onchange')
    customer_rfq = fields.Binary(string="Customer RFQ", translate=True, track_visibility='onchange')
    project_type = fields.Selection([
        ('supply', 'Supply Only'),
        ('installation', 'Installation Only'),
        ('supply_installation', 'Supply and Installation'),
    ], string='Project Type', translate=True, track_visibility='onchange')
    source_person = fields.Many2one('res.partner', string='Source Person', track_visibility='onchange', translate=True, index=True)
    opportunity_type = fields.Selection([
        ('tender', 'Tender'),
        ('direct_assign', 'Direct Assign')
    ], string='Opportunity Type', translate=True, track_visibility='onchange')

    project_agreement_create_check = fields.Boolean(string="Project Agreement Create Check", translate=True, default=False)

    def action_generate_project_agreement(self):
        if not self.partner_id:
            raise ValidationError(_("You must choose the Customer"))

        # FIXME [project.agreement] creation should be review "start_date" and "end_date" not clarified in the task
        self.ensure_one()
        vals = {
            'name': self.name,
            'project_type': self.project_type,
            'customer_rfq': self.customer_rfq,
            'user_id': self.user_id.id,
            'source_person': self.source_person.id,
            'opportunity_type': self.opportunity_type,

            'start_date': datetime.today(),
            'end_date': datetime.today(),
            'customer_id': self.partner_id.id,
        }
        self.env['project.agreement'].create(vals)

        self.project_agreement_create_check = True
