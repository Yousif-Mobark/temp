# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    progress_bill = fields.Boolean()
    progress_bill_type = fields.Selection([("internal", "Internal"), ("sub", "Sub contractor")])
