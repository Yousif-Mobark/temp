# -*- coding: utf-8 -*-

from odoo import api, fields, models , _ , tools


class AgreementSales(models.TransientModel):
    _name = "agreement.sale"
    _description = "Agreement Sale Order"

    agreement_id = fields.Many2one('project.agreement','Agreement' , readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer',related='agreement_id.customer_id' , readonly=1)
    agreement_line_id = fields.Many2one('project.agreement.planned' , 'Item' )
    product_id = fields.Many2one('product.product','Product' ,related='agreement_line_id.product_id' ,readonly=1 )
    uom = fields.Many2one('product.uom', 'Unit of Measuer', related='agreement_line_id.product_uom' ,required=1)
    required_quantity = fields.Float(string='Required Qty',related='agreement_line_id.required_quantity' , readonly=1)
    delivered_quantity = fields.Monetary(string='Delivered Qty', related='agreement_line_id.delivered_quantity', readonly=1)
    residual_quantity = fields.Monetary(string='Residual Qty',)
    currency_id = fields.Many2one('res.currency', 'Currency',related='agreement_line_id.currency_id',readonly=1)


    @api.onchange('required_quantity','delivered_quantity','agreement_line_id',)
    def onchange_set_residual_quantity(self):
        self.residual_quantity = self.required_quantity - self.delivered_quantity




    @api.multi
    def create_sale_order(self):
        so = self.env['sale.order'].create({
            'agreement_id' : self.agreement_id.id,
            'partner_id': self.customer_id.id,
            'partner_invoice_id': self.customer_id.id,
            'partner_shipping_id': self.customer_id.id,
            'analytic_account_id' : self.agreement_line_id.analytic_account_id.id ,
            'order_line': [(0, 0,
                            {'name': self.product_id.name, 'product_id': self.product_id.id,
                             'product_uom_qty': self.residual_quantity, 'product_uom': self.uom.id,
                             'price_unit': self.product_id.list_price ,
                             'agreement_id':self.agreement_id.id , 'agreement_line_id' : self.agreement_line_id.id})],
            'pricelist_id': self.env.ref('product.list0').id,
        })

        return {
            'name': _('Deliver'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', so.id)],
            'context': {'default_agreement_id': self.agreement_id.id}
        }

