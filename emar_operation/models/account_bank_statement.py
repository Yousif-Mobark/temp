# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import float_is_zero, pycompat
from odoo.tools import float_compare, float_round, float_repr
from odoo.tools.misc import formatLang, format_date
from odoo.exceptions import UserError, ValidationError


class AccountBankStatementLine(models.Model):
    _name = "account.bank.statement.line"
    _inherit = "account.bank.statement.line"

    operation_type = fields.Selection([('in', 'In'),('out', 'Out')], string="Operation Type", translate=True, requierd=True)
    attach = fields.Binary(string="Attachment", translate=True)
    amount = fields.Monetary(digits=0, currency_field='journal_currency_id')

    @api.depends('amount', 'operation_type')
    @api.onchange('amount', 'operation_type')
    def onchange_amount(self):
        if self.operation_type == 'out':
            self.amount = -self.amount

