# -*- coding: utf-8 -*-
from odoo import http

# class ProjectAgreementPurchase(http.Controller):
#     @http.route('/project_agreement_purchase/project_agreement_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_agreement_purchase/project_agreement_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_agreement_purchase.listing', {
#             'root': '/project_agreement_purchase/project_agreement_purchase',
#             'objects': http.request.env['project_agreement_purchase.project_agreement_purchase'].search([]),
#         })

#     @http.route('/project_agreement_purchase/project_agreement_purchase/objects/<model("project_agreement_purchase.project_agreement_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_agreement_purchase.object', {
#             'object': obj
#         })