# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ReturnedNRWizard(models.TransientModel):
    _name = 'returned.nr.wizard'
    _description = 'Returned NR Wizard'

    date = fields.Date(string='Date', translate=True, default=fields.Date.context_today)
    reason = fields.Text(string='rejected Reason', translate=True)
    note = fields.Char(string='Notes', translate=True)

    @api.multi
    def do_action(self):
        context = dict(self.env.context or {})
        active_id = context.get('active_id', False)
        if active_id:
            obj = self.env['account.check.nr'].browse(active_id)

            # reverse of journal entry generated from account.payment
            move = self.env['account.move'].search([('name', '=', obj.payment_id.move_name)])
            reverse_move = self.env['account.move'].browse(move.id).reverse_moves(self.date,
                                                                                  obj.payment_id.journal_id or False)
            operation_values = {
                'date': self.date,
                'type': 'nr',
                'type_of_check': 'nr',
                'operation': 'Returned',
                'move_id': reverse_move[0],
                'partner': obj.check_partner.id,
                'note': self.note,
                'reason': self.reason,
            }
            operation = self.env['account.check.operation.nr'].create(operation_values)

            obj.write({
                'state': 'returned',
                'operation_ids': [(4, operation.id)],
            })


