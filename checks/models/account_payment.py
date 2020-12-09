# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class account_payment(models.Model):
    _name = "account.payment"
    _inherit = ['account.payment']

    # Account Recievable
    issue_date = fields.Date(string='Issue Date', translate=True)
    due_date = fields.Date(string='Due Date', translate=True)
    from_bank_id = fields.Many2one('res.bank', string='From Bank', translate=True)
    in_bank_journal_id = fields.Many2one('account.journal', string='In Bank', domain="[('type', '=', 'bank')]")
    bank_check_template = fields.Many2one('res.bank', string='Bank Check Template', translate=True)
    printed_due_date = fields.Date(string='Printed Due Date', translate=True)
    check_number = fields.Integer(string='Check Number', translate=True)
    check_guarantor = fields.Many2one('res.partner', string='Check Guarantor', translate=True)
    nr = fields.Many2one('account.check.nr', string='Account Check Notes Receivable', translate=True)

    # "Generate Notes Payable"
    deferred_checkbook = fields.Many2one('deferred.checks', string='Deferred Checkbook', translate=True, domain="[('state', '=', 'in_use')]")
    deferred_bank_journal = fields.Many2one(related="deferred_checkbook.bank_journal_id", string='Deferred Bank Journal', translate=True)
    deferred_manual_numbering = fields.Boolean(related="deferred_checkbook.manual_numbering", string='Deferred manual numbering', translate=True)
    deferred_next_number = fields.Integer(related="deferred_checkbook.next_number", string='Next Number', translate=True)

    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'waiting_revision':
                raise UserError(_("Only a Waiting Revision payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to Waiting Revision
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                    sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(
                    lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})

            # Received Notes Receivable
            if rec.payment_method_code == 'rnr':

                operation_values = {
                    'operation': 'In Hand',
                    'journal_id': move.journal_id.id,
                    'partner': rec.partner_id.id,
                    'type': 'nr',
                    'type_of_check': 'nr',
                    'note': rec.communication,
                }
                operation = self.env['account.check.operation.nr'].create(operation_values)

                # date -> accounting date "by default date of action validate"
                check_values = {
                    'type': 'nr',
                    'date': rec.validate_date,
                    'partner': rec.partner_id.id,
                    'debit': rec.journal_id.default_debit_account_id.id,
                    'credit': rec.destination_account_id.id,
                    'state': 'in_hand',

                    'payment_method_id': rec.payment_method_id.id,
                    'journal_id': rec.journal_id.id,
                    'check_partner': rec.partner_id.id,
                    'issue_date': rec.issue_date,
                    'due_date': rec.due_date,
                    'operation_ids': [(4, operation.id)],
                    'amount': rec.amount,

                    'from_bank_id': rec.from_bank_id.id,
                    'in_bank_journal_id': rec.in_bank_journal_id.id,
                    'bank_check_template': rec.bank_check_template.id,
                    'printed_due_date': rec.printed_due_date,
                    'check_number': rec.check_number,
                    'check_guarantor': rec.check_guarantor.id,

                    'payment_id': rec.id,
                }
                self.env['account.check.nr'].create(check_values)

            # Delivered Notes Receivable
            elif rec.payment_method_code == 'dnr':

                operation_values = {
                    'type': 'nr',
                    'operation': 'Handed to Other Partner',
                    'journal_id': move.journal_id.id,
                    'partner': rec.partner_id.id,
                    'note': rec.communication,
                }
                operation = self.env['account.check.operation.nr'].create(operation_values)

                check_values = {
                    'type': 'nr',
                    'date': rec.validate_date,
                    'partner': rec.partner_id.id,
                    'debit': rec.destination_account_id.id,
                    'credit': rec.nr.debit.id,
                    'state': 'in_hand',

                    'payment_id': rec.id,
                }
                self.env['account.check.nr'].create(check_values)

                rec.nr.write({'state': 'handed_to_other'})

            # Generate Notes Payable
            elif rec.payment_method_code == 'gnp':

                operation_values = {
                    'type': 'np',
                    'operation': 'Handed',
                    'journal_id': move.journal_id.id,
                    'note': rec.communication,
                }
                operation = self.env['account.check.operation.np'].create(operation_values)

                automatic_check_number = False
                if not rec.deferred_manual_numbering:
                    check_number = self.env["account.check.np"].search([], order="id desc", limit=1).check_number
                    if check_number:
                        automatic_check_number = check_number + rec.deferred_next_number
                    else:
                        automatic_check_number = rec.deferred_next_number

                check_values = {
                    'type': 'nr',
                    'date': rec.validate_date,
                    'partner': rec.partner_id.id,
                    'debit': rec.destination_account_id.id,
                    'credit': rec.journal_id.default_credit_account_id.id,
                    'state': 'handed',

                    'journal_id': rec.journal_id.id,
                    'issue_date': rec.issue_date,
                    'due_date': rec.due_date,

                    'deferred_checkbook': rec.deferred_checkbook.id,
                    'bank_check_template': rec.bank_check_template.id,
                    'deferred_bank_journal': rec.deferred_bank_journal.id,
                    'check_number': automatic_check_number or rec.check_number,
                    'operation_ids': [(4, operation.id)],
                    'amount': rec.amount,
                    'payment_id': rec.id,

                }
                self.env['account.check.np'].create(check_values)

        return True
