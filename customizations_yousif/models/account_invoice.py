# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    progress_bill = fields.Boolean()
    progress_bill_type = fields.Selection([("internal", "Internal"), ("sub", "Sub contractor")])


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_employee = fields.Boolean()
    is_subcontractor = fields.Boolean()
    custody_account = fields.Many2one("account.account")
