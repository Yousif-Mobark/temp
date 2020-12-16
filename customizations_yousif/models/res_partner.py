# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_employee = fields.Boolean()
    is_subcontractor = fields.Boolean()
    custody_account = fields.Many2one("account.account")
