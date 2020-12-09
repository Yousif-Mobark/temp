# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class InBankNRWizard(models.TransientModel):
    _name = 'in.bank.nr.wizard'
    _description = 'In Bank NR Wizard'

    under_collection_journal_id = fields.Many2one('account.journal', string='Under Collection Journal', domain="[('under_collection_journal', '=', True)]",
                                      translate=True)
    under_deposit_journal_id = fields.Many2one('account.journal', string='Under Deposit Journal', domain="[('under_deposit_journal', '=', True)]",
                                      translate=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, translate=True)
    note = fields.Char(string='Notes', translate=True)

    @api.multi
    def do_action(self):
        context = dict(self.env.context or {})
        active_id = context.get('active_id', False)
        if active_id:
            obj = self.env['account.check.nr'].browse(active_id)
            move_line_vals = []

            if not self.under_collection_journal_id.default_debit_account_id:
                raise ValidationError(_("You must determine the default account of Under Collection Journal!"))

            if not self.under_deposit_journal_id.default_debit_account_id:
                raise ValidationError(_("You must determine the default account of Under Deposit Journal!"))

            line = (0, 0, {'account_id': self.under_deposit_journal_id.default_debit_account_id.id,
                           'partner_id': obj.check_partner.id,
                           'name': obj.check_number,
                           'debit': obj.amount,
                           'credit': 0.0,
                           })
            move_line_vals.append(line)
            line = (0, 0, {'account_id': self.under_collection_journal_id.default_credit_account_id.id,
                           'partner_id': obj.check_partner.id,
                           'name': obj.check_number,
                           'debit': 0.0,
                           'credit': obj.amount,
                           })
            move_line_vals.append(line)

            move_vals = {
                "date": self.date,
                "name": str(obj.check_number),
                "line_ids": move_line_vals,
                'ref': obj.payment_id.communication or '',
                'company_id': obj.company_id.id,
                'journal_id': obj.journal_id.id,
            }
            move = self.env['account.move'].create(move_vals)

            operation_values = {
                'date': self.date,
                'type': 'nr',
                'type_of_check': 'nr',
                'operation': 'In Bank',
                'journal_id': move.journal_id.id,
                'move_id': move.id,
                'partner': obj.check_partner.id,
                'note': self.note,
            }
            operation = self.env['account.check.operation.nr'].create(operation_values)

            obj.write({
                'state': 'in_bank',
                'operation_ids': [(4, operation.id)],
            })


