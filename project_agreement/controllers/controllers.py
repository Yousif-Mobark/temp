# -*- coding: utf-8 -*-
from odoo import http

# class ProjectBaptism(http.Controller):
#     @http.route('/project_agreement/project_agreement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_agreement/project_agreement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_agreement.listing', {
#             'root': '/project_agreement/project_agreement',
#             'objects': http.request.env['project_agreement.project_agreement'].search([]),
#         })

#     @http.route('/project_agreement/project_agreement/objects/<model("project_agreement.project_agreement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_agreement.object', {
#             'object': obj
#         })