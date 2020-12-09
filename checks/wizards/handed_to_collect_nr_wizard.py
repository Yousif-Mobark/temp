# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class HandedToCollectNRWizard(models.TransientModel):
    _name = 'handed.to.collect.nr.wizard'
    _description = 'Handed To Collect NR Wizard'

    journal_id = fields.Many2one('account.journal', string='Under Collection Journal', domain="[('under_collection_journal', '=', True)]",
                                      translate=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, translate=True)
    responsible_id = fields.Many2one('res.partner', 'Responsible for Check collecting', domain="[('responsible_check_collecting', '=', True)]", translate=True)
    in_bank_journal_id = fields.Many2one('account.journal', string='In Bank', domain="[('type', '=', 'bank')]", translate=True)
    note = fields.Char(string='Notes', translate=True)

    @api.multi
    def handed_to_collect_action(self):
        context = dict(self.env.context or {})
        active_id = context.get('active_id', False)
        if active_id:
            obj = self.env['account.check.nr'].browse(active_id)
            move_line_vals = []

            if not self.journal_id.default_debit_account_id:
                raise ValidationError(_("You must determine the default account of Under Collection Journal!"))

            line = (0, 0, {'account_id': self.journal_id.default_debit_account_id.id,
                           'partner_id': obj.check_partner.id,
                           'name': obj.check_number,
                           'debit': obj.amount,
                           'credit': 0.0,
                           })
            move_line_vals.append(line)
            line = (0, 0, {'account_id': obj.journal_id.default_credit_account_id.id,
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
                'operation': 'Handed To Collect',
                'journal_id': move.journal_id.id,
                'move_id': move.id,
                'partner': obj.check_partner.id,
                'note': self.note,
            }
            operation = self.env['account.check.operation.nr'].create(operation_values)

            obj.write({
                'in_bank': self.in_bank_journal_id.id,
                'state': 'handed_to_collect',
                'responsible_id': self.responsible_id.id,
                'operation_ids': [(4, operation.id)],
            })


