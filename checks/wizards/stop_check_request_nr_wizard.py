# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StopCheckRequestNRWizard(models.TransientModel):
    _name = 'stop.check.request.nr.wizard'
    _description = 'Stop Check Request NR Wizard'

    date = fields.Date(string='Date', translate=True, default=fields.Date.context_today)
    reason = fields.Text(string='Return Reason', translate=True)
    note = fields.Char(string='Notes', translate=True)

    @api.multi
    def do_action(self):
        context = dict(self.env.context or {})
        active_id = context.get('active_id', False)
        if active_id:
            obj = self.env['account.check.nr'].browse(active_id)

            operation_values = {
                'date': self.date,
                'type': 'nr',
                'type_of_check': 'nr',
                'operation': 'Stop Check Request',
                'partner': obj.check_partner.id,
                'note': self.note,
                'reason': self.reason,
            }
            operation = self.env['account.check.operation.nr'].create(operation_values)

            obj.write({
                'state': 'stop_check_request',
                'operation_ids': [(4, operation.id)],
            })


