# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class NotesPayableRejectedWizard(models.TransientModel):
    _name = 'np.rejected.wizard'
    _description = 'Notes Payable Rejected Wizard'

    date = fields.Date(string='Date', translate=True)
    reason = fields.Many2one('np.rejected.reason', string='rejected Reason', translate=True)
    note = fields.Char(string='Notes', translate=True)

    @api.multi
    def get_rejected(self):
        context = dict(self.env.context or {})
        active_id = context.get('active_id', False)
        if active_id:
            obj = self.env['account.check.np'].browse(active_id)
            obj.write({
                'state': 'rejected',
                'reject_reason_date': self.date,
                'reject_reason': self.reason.id,
                'reject_note': self.note,
                       })

            # reverse of journal entry generated from account.payment
            move = self.env['account.move'].search([('name', '=', obj.payment_id.move_name)])
            reverse_move = self.env['account.move'].browse(move.id).reverse_moves(self.date,
                                                                                  obj.payment_id.journal_id or False)

            operation_values = {
                'date': self.date,
                'reason': self.reason.id,
                'note': self.note,
                'type': 'np',
                'check_partner': obj.payment_id.partner_id.id,
                'operation': 'rejected',
            }
            operation = self.env['account.check.operation'].create(operation_values)

