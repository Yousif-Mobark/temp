# -*- coding: utf-8 -*-
from odoo import http

# class ProjectAgreementSales(http.Controller):
#     @http.route('/project_agreement_sales/project_agreement_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_agreement_sales/project_agreement_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_agreement_sales.listing', {
#             'root': '/project_agreement_sales/project_agreement_sales',
#             'objects': http.request.env['project_agreement_sales.project_agreement_sales'].search([]),
#         })

#     @http.route('/project_agreement_sales/project_agreement_sales/objects/<model("project_agreement_sales.project_agreement_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_agreement_sales.object', {
#             'object': obj
#         })