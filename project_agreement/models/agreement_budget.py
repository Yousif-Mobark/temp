# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp



class AccountBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    residual = fields.Float(compute='_compute_residual_amount', string='Residual Amount')
    required_quantity = fields.Float(string='Required Qty',)
    total = fields.Monetary(string='Total Cost')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    price_unit = fields.Monetary('Unit Price',digits=dp.get_precision('Price'))

    @api.depends('planned_amount','practical_amount')
    def _compute_residual_amount(self):
        for line in self:
            line.residual = line.planned_amount + line.practical_amount