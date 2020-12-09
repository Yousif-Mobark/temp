# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountCheckOperation(models.Model):
    _name = "account.check.operation"
    _inherit = ['mail.thread']

    date = fields.Date(string='Date', translate=True)
    type = fields.Selection([('nr', "Notes Receivable"), ('np', "Notes Payable")], string="Type", translate=True)
    type_of_check = fields.Selection([('nr', "Notes Receivable"), ('np', "Notes Payable")], string="Type", translate=True)
    operation = fields.Char(string="Operation", translate=True)

    move_id = fields.Many2one('account.move', string='Journal Entry',
        readonly=True, index=True, ondelete='restrict', copy=False,
        help="Link to the automatically generated Journal Items.")
    check_partner = fields.Many2one('res.partner', string='Check Partner', translate=True)
    reason = fields.Char(string="Reason", translate=True)
    note = fields.Char(string="Note", translate=True)


class AccountCheckOperationNR(models.Model):
    _name = "account.check.operation.nr"
    _inherit = ['mail.thread']

    date = fields.Date(string='Date', translate=True)
    type = fields.Selection([('nr', "Notes Receivable"), ('np', "Notes Payable")], string="Type", translate=True)
    type_of_check = fields.Selection([('nr', "Notes Receivable"), ('np', "Notes Payable")], string="Type", translate=True)
    operation = fields.Char(string="Operation", translate=True)
    journal_id = fields.Many2one('account.journal', string='Journal', translate=True)
    partner = fields.Many2one('res.partner', string='Check Partner', translate=True)

    # reason = fields.Char(string="Reason", translate=True)
    note = fields.Char(string="Note", translate=True)


class AccountCheckOperationNP(models.Model):
    _name = "account.check.operation.np"
    _inherit = ['mail.thread']

    # date = fields.Date(string='Date', translate=True)
    type = fields.Selection([('nr', "Notes Receivable"), ('np', "Notes Payable")], string="Type", translate=True)
    type_of_check = fields.Selection([('nr', "Notes Receivable"), ('np', "Notes Payable")], string="Type", translate=True)
    operation = fields.Char(string="Operation", translate=True)
    journal_id = fields.Many2one('account.journal', string='Journal', translate=True)
    partner = fields.Many2one('res.partner', string='Check Partner', translate=True)

    # reason = fields.Char(string="Reason", translate=True)
    note = fields.Char(string="Note", translate=True)

