# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = "product.category"

    category_type = fields.Selection([
        ('normal', 'Normal'),
        ('raw_material', 'Raw Material'),
        ('working_items', 'Working Items'),
    ], string='Product type', required=True, default='normal')

    working_item_id = fields.Many2one('working.item', string='Working Item')


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    product_subtype = fields.Selection([
        ('normal', 'Normal'),
        ('raw_material', 'Raw Material'),
        ('working_items', 'Sub Working Items'),
    ], string='Product subtype', required=True, default='normal', track_visibility='onchange')
    product_brand_id = fields.Many2one('product.brand', string='Product Brand', track_visibility='onchange')

    @api.onchange('product_subtype')
    def _onchange_product_subtype(self):
        if self.product_subtype == 'raw_material':
            self.type = 'product'
        elif self.product_subtype == 'working_items':
            self.type = 'service'
        if self.product_subtype:
            self.categ_id = ''
            return {'domain': {'categ_id': [('category_type', '=', self.product_subtype)] }}


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Product Brand"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", requierd=True, track_visibility='onchange')
