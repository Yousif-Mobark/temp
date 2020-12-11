# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderCustom(models.Model):
    _inherit = 'purchase.order'

    type = fields.Selection([('order' , 'Order') , ('contract' , 'Contract')] , string="Type" , default="order")