# -*- coding: utf-8 -*-
from odoo import http

# class AgreementAttachConfirmation(http.Controller):
#     @http.route('/agreement_attach_confirmation/agreement_attach_confirmation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/agreement_attach_confirmation/agreement_attach_confirmation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('agreement_attach_confirmation.listing', {
#             'root': '/agreement_attach_confirmation/agreement_attach_confirmation',
#             'objects': http.request.env['agreement_attach_confirmation.agreement_attach_confirmation'].search([]),
#         })

#     @http.route('/agreement_attach_confirmation/agreement_attach_confirmation/objects/<model("agreement_attach_confirmation.agreement_attach_confirmation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('agreement_attach_confirmation.object', {
#             'object': obj
#         })