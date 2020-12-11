# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class EmergencyCompanyConf(models.Model):
    _inherit = "res.company"

    emergency_account_id = fields.Many2one('account.account')
    emergency_account_exp_id = fields.Many2one('account.account')
    emergency_journal_id = fields.Many2one('account.journal')


class EmergencyConfiguration(models.TransientModel):
    _name = 'emergency.general.settings'

    emergency_account_id = fields.Many2one('account.account', string="Emergency Account")
    emergency_account_exp_id = fields.Many2one('account.account', string="Emergency Expense Account")
    emergency_journal_id = fields.Many2one('account.journal', string="Emergency Journal")
    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.user.company_id)

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        self.emergency_account_id = company.emergency_account_id
        self.emergency_account_exp_id = company.emergency_account_exp_id
        self.emergency_journal_id = company.emergency_journal_id

    @api.one
    def set_company_values(self):
        company = self.company_id
        company.emergency_account_id = self.emergency_account_id
        company.emergency_account_exp_id = self.emergency_account_exp_id
        company.emergency_journal_id = self.emergency_journal_id
