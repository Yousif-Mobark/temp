# -*- coding: utf-8 -*-

from odoo import models, fields, api


class projectAgreement(models.Model):
    _name = 'project.agreement'
    _inherit = 'project.agreement'

    project_type = fields.Selection([
        ('supply', 'Supply Only'),
        ('installation', 'Installation Only'),
        ('supply_installation', 'Supply and Installation'),
    ], string='Project Type', translate=True, track_visibility='onchange')
    customer_rfq = fields.Binary(string="Customer RFQ", translate=True, track_visibility='onchange')
    user_id = fields.Many2one('res.partner', string='Account Manager', track_visibility='onchange', translate=True, index=True)
    source_person = fields.Many2one('res.partner', string='Source Person', track_visibility='onchange', translate=True,
                                    index=True)

    opportunity_type = fields.Selection([
        ('tender', 'Tender'),
        ('direct_assign', 'Direct Assign')
    ], string='Opportunity Type', translate=True, track_visibility='onchange')
