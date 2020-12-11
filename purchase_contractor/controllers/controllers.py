# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseContractor(http.Controller):
#     @http.route('/purchase_contractor/purchase_contractor/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_contractor/purchase_contractor/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_contractor.listing', {
#             'root': '/purchase_contractor/purchase_contractor',
#             'objects': http.request.env['purchase_contractor.purchase_contractor'].search([]),
#         })

#     @http.route('/purchase_contractor/purchase_contractor/objects/<model("purchase_contractor.purchase_contractor"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_contractor.object', {
#             'object': obj
#         })