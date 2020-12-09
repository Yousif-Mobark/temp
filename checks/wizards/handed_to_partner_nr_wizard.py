# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class HandedToPartnerNRWizard(models.TransientModel):
    _name = 'handed.to.partner.nr.wizard'
    _description = 'Handed To Partner NR Wizard'

    journal_id = fields.Many2one('account.journal', string='Journal', translate=True)
    account_id = fields.Many2one('account.account', string='Account', translate=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, translate=True)
    note = fields.Char(string='Notes', translate=True)

    @api.multi
    def handed_to_partner_action(self):
        context = dict(self.env.context or {})
        active_id = context.get('active_id', False)
        if active_id:
            obj = self.env['account.check.nr'].browse(active_id)
            move_line_vals = []

            if not self.journal_id.default_credit_account_id:
                raise ValidationError(_("You must determine the default account of Under Partnerion Journal!"))

            line = (0, 0, {'account_id': self.account_id.id,
                           'partner_id': obj.check_partner.id,
                           'name': obj.check_number,
                           'debit': obj.amount,
                           'credit': 0.0,
                           })
            move_line_vals.append(line)
            line = (0, 0, {'account_id': self.journal_id.default_credit_account_id.id,
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
                'operation': 'Handed To Partner',
                'journal_id': move.journal_id.id,
                'move_id': move.id,
                'partner': obj.check_partner.id,
                'note': self.note,
            }
            operation = self.env['account.check.operation.nr'].create(operation_values)

            obj.write({
                'state': 'handed_to_partner',
                'operation_ids': [(4, operation.id)],
            })


