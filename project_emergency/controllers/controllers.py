# -*- coding: utf-8 -*-
from odoo import http

# class ProjectEmergency(http.Controller):
#     @http.route('/project_emergency/project_emergency/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_emergency/project_emergency/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_emergency.listing', {
#             'root': '/project_emergency/project_emergency',
#             'objects': http.request.env['project_emergency.project_emergency'].search([]),
#         })

#     @http.route('/project_emergency/project_emergency/objects/<model("project_emergency.project_emergency"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_emergency.object', {
#             'object': obj
#         })