# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = ['sale.order']



    agreement_id = fields.Many2one('project.agreement' , 'Agreement')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    agreement_id = fields.Many2one('project.agreement' , 'Agreement')
    agreement_line_id = fields.Many2one('project.agreement.planned' , 'Item')



class projectAgreement(models.Model):
    _inherit = 'project.agreement'
    deliver_order_ids = fields.One2many('sale.order.line', 'agreement_id', 'Delivers')
    deliver_line_ids = fields.One2many('sale.order', 'agreement_id', 'Delivers Line')

class projectAgreement(models.Model):
    _inherit = 'project.agreement.planned'

    deliver_ids = fields.One2many('sale.order.line' , 'agreement_line_id' , 'Delivers')
    delivered_quantity = fields.Monetary(compute='_compute_delivered_quantity', string='Delivered Qty')


    @api.depends('deliver_ids', 'required_quantity')
    def _compute_delivered_quantity(self):

       for line in self:
           line.update({
               'delivered_quantity' : sum(line.deliver_ids.mapped('qty_delivered'))
           })