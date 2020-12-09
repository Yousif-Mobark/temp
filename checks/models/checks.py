# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class AccountCheckNR(models.Model):
    _name = "account.check.nr"
    _inherit = ['mail.thread']
    _rec_name = "check_number"
    _order = "id desc"

    type = fields.Selection([('nr', "Notes Receivable"), ('np', "Notes Payable")], string="Type", translate=True)
    payment_method_id = fields.Many2one('account.payment.method', string='NR Type', translate=True)
    journal_id = fields.Many2one('account.journal', string='Journal', translate=True)
    check_partner = fields.Many2one('res.partner', string='Check Partner', translate=True)
    issue_date = fields.Date(string='Issue Date', translate=True)
    due_date = fields.Date(string='Due Date', translate=True)
    # FIXME
    operation_ids = fields.Many2many('account.check.operation.nr', string='Account Check Operation', domain=[('type', '=', 'nr')])

    amount = fields.Monetary(string='Amount', currency_field='company_currency_id')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)

    # if NR type
    from_bank_id = fields.Many2one('res.bank', string='From Bank')
    in_bank_journal_id = fields.Many2one('account.journal', string='In Bank', domain="[('type', '=', 'bank')]")
    # bank_check_date = fields.Date(string='Bank Check Template', translate=True)  # from payment
    bank_check_template = fields.Many2one('res.bank', string='Bank Check Template', translate=True)
    printed_due_date = fields.Date(string='Printed Due Date', translate=True)
    check_number = fields.Integer(string='Check Number', translate=True)
    check_guarantor = fields.Many2one('res.partner', string='Check Guarantor', translate=True)
    state = fields.Selection([('in_hand', 'In Hand'),
                              ('handed_to_collect', 'Handed to Collect'),
                              ('handed_to_other', 'Handed to Other Partner'),
                              ('in_bank', 'In Bank'),
                              ('collected_cash', 'Collected Cash'),
                              ('returned', 'Returned'),
                              ('returned_from_bank', 'Returned from Bank'),
                              ('bank_deposited', 'Bank Deposited'),
                              ('rejected', 'Rejected'),
                              ('re_banking', 'Re-Banking'),
                              ('handed_to_partner', 'Handed to Partner'),
                              ('stop_check_request', 'Stop Check Request'),
                              ('cancelled', 'Cancelled')
                              ], readonly=True, default='in_hand', copy=False, string="Status", translate=True)

    date = fields.Date(string='Accounting Date', translate=True)  # validate date
    partner = fields.Many2one('res.partner', string='Partner', translate=True)
    debit = fields.Many2one('account.account', string='Debit Account', domain=[('deprecated', '=', False)], translate=True)
    credit = fields.Many2one('account.account', string='Credit Account', domain=[('deprecated', '=', False)], translate=True)

    payment_id = fields.Many2one('account.payment', string="Payment", help="Payment that created this entry", copy=False, translate=True)
    responsible_id = fields.Many2one('res.partner', 'Responsible for Check collecting', domain="[('responsible_check_collecting', '=', True)]", translate=True)

    @api.multi
    def handed_to_partner(self):
        for rec in self:

            operation_values = {
                'date': datetime.today(),
                'type': 'nr',
                'type_of_check': 'nr',
                'operation': 'Handed to Partner',
                'partner': self.check_partner.id,

            }
            operation = self.env['account.check.operation.nr'].create(operation_values)

            rec.state = 'handed_to_partner'
            rec.operation_ids = [(4, operation.id)]


class AccountCheckNP(models.Model):
    _name = "account.check.np"
    _inherit = ['mail.thread']
    _rec_name = "check_number"
    _order = "id desc"

    journal_id = fields.Many2one('account.journal', string='Journal', translate=True)
    issue_date = fields.Date(string='Issue Date', translate=True)
    due_date = fields.Date(string='Due Date', translate=True)
    deferred_checkbook = fields.Many2one('deferred.checks', string='Deferred Checkbook', translate=True)
    bank_check_template = fields.Many2one('res.bank', string='Bank Check Template', translate=True)
    deferred_bank_journal = fields.Many2one('account.journal', string='Bank Journal', domain="[('type', '=', 'bank')]", translate=True)
    check_number = fields.Integer(string='Check Number', translate=True)
    # FIXME
    operation_ids = fields.Many2many('account.check.operation.np', string='Account Check Operation', domain=[('type', '=', 'np')], translate=True)
    amount = fields.Monetary(string='Amount', currency_field='company_currency_id', translate=True)

    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, translate=True)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, translate=True)

    state = fields.Selection([('handed', 'Handed'),
                              ('bank_debited', 'Bank Debited'),
                              ('rejected', 'Rejected'),
                              ('returned', 'Returned')
                              ], readonly=True, default='handed', copy=False, string="Status", translate=True)

    return_reason_date = fields.Date(string='Reason Date', translate=True)
    return_reason = fields.Many2one('np.return.reason', string='Returned Reason', translate=True)
    return_note = fields.Char(string='Notes Reason', translate=True)

    reject_reason_date = fields.Date(string='Reason Date', translate=True)
    reject_reason = fields.Many2one('np.rejected.reason', string='Rejected Reason', translate=True)
    reject_note = fields.Char(string='Notes Reason', translate=True)

    reason = fields.Text(string='Reason', translate=True)
    note = fields.Char(string='Notes', translate=True)

    payment_id = fields.Many2one('account.payment', string="Payment", help="Payment that created this entry", copy=False, translate=True)
    move_id = fields.Many2one('account.move', string='Journal Entry',
                              readonly=True, index=True, ondelete='restrict', copy=False,
                              help="Link to the automatically generated Journal Items.")

    @api.multi
    def bank_debited(self):
        for rec in self:
            rec.state = 'bank_debited'

            move = rec.create_journal()

            operation_values = {
                'date': datetime.today(),
                'type': 'np',
                'check_partner': rec.payment_id.partner_id.id,
                'move_id': move.id,
                'operation': 'Bank Debited',
            }
            operation = self.env['account.check.operation'].create(operation_values)

    def create_journal(self):

        move_line_vals = []

        line = (0, 0, {'account_id': self.payment_id.journal_id.default_credit_account_id.id,
                       'partner_id': self.payment_id.partner_id.id,
                       'name': self.check_number,
                       'debit': self.amount,
                       'credit': 0.0,
                       })
        move_line_vals.append(line)
        line = (0, 0, {'account_id': self.deferred_bank_journal.default_debit_account_id.id,
                       'partner_id': self.payment_id.partner_id.id,
                       'name': self.check_number,
                       'debit': 0.0,
                       'credit': self.amount,
                       })
        move_line_vals.append(line)

        move_vals = {
            "date": datetime.today(),
            "name": str(self.payment_id.name),
            "line_ids": move_line_vals,
            'ref': self.payment_id.communication or '',
            'company_id': self.company_id.id,
            'journal_id': self.journal_id.id,
        }
        return self.env['account.move'].create(move_vals)


class AccountCheckNPReturnReason(models.Model):
    _name = "np.return.reason"
    _inherit = ['mail.thread']

    name = fields.Text('Reasons', translate=True)


class AccountCheckNPRejectReason(models.Model):
    _name = "np.rejected.reason"
    _inherit = ['mail.thread']

    name = fields.Text('Reasons', translate=True)


class Partner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    responsible_check_collecting = fields.Boolean('Responsible for Check collecting', translate=True, default=False)