# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class NotesPayableReturnedWizard(models.TransientModel):
    _name = 'np.returned.wizard'
    _description = 'Notes Payable Returned Wizard'

    date = fields.Date(string='Date', translate=True)
    reason = fields.Many2one('np.return.reason', string='Returned Reason', translate=True)
    note = fields.Char(string='Notes', translate=True)

    @api.multi
    def get_reason(self):
        context = dict(self.env.context or {})
        active_id = context.get('active_id', False)
        if active_id:
            obj = self.env['account.check.np'].browse(active_id)
            obj.write({
                'state': 'returned',
                'return_reason_date': self.date,
                'return_reason': self.reason.id,
                'return_note': self.note,
                       })
            # reverse of journal entry generated from account.payment
            move = self.env['account.move'].search([('name', '=', obj.payment_id.move_name)])
            reverse_move = self.env['account.move'].browse(move.id).reverse_moves(self.date, obj.payment_id.journal_id or False)

            operation_values = {
                'date': self.date,
                'reason': self.reason.id,
                'note': self.note,
                'type': 'np',
                'check_partner': obj.payment_id.partner_id.id,
                'operation': 'Returned',
            }
            operation = self.env['account.check.operation'].create(operation_values)

