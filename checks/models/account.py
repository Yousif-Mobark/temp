# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_payment_method(models.Model):
    _name = "account.payment.method"
    _inherit = "account.payment.method"

    @api.model
    def _default_check_type(self):
        if not self.check_type:
            return 'cash'

    check_type = fields.Selection([('bank', 'bank'), ('cash', 'cash')], required=True, default=_default_check_type)


class AccountJournal(models.Model):
    _name = "account.journal"
    _inherit = "account.journal"

    deferred_checkbook = fields.Many2many('deferred.checks', string='Deferred Checkbook', domain="[('state', '=', 'in_use')]", translate=True)
    outbound_payment_method_ids_code = fields.Char(related="outbound_payment_method_ids.code")

    under_collection_journal = fields.Boolean(string="Under Collection Journal", translate=True)
    under_deposit_journal = fields.Boolean(string="Under Deposit Journal", translate=True)

    # # FIXME
    # @api.onchange('type')
    # def _onchange_type(self):
    #     if self.type == 'cash':
    #         return {'domain': {'inbound_payment_method_ids': [('payment_type', '=', 'inbound'), ('check_type', '=', 'cash')]}}
    #     if self.type == 'bank':
    #         return {'domain': {'inbound_payment_method_ids': [('payment_type', '=', 'inbound'), ('check_type', '=', 'bank')]}}


class DeferredChecks(models.Model):
    _name = "deferred.checks"
    _description = "Deferred checks"

    name = fields.Text(string="Checkbook Name", translate=True, required=True)
    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal', domain="[('type', '=', 'bank')]", translate=True)
    next_number = fields.Integer(string="Next Number", translate=True, required=True)
    to = fields.Integer(string="Next Number", translate=True, required=True)
    manual_numbering = fields.Boolean(string="manual numbering", translate=True, default=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('in_use', 'In Use'),
                              ('used', 'Used')
                              ], default='draft', copy=False, string="Status", translate=True)
