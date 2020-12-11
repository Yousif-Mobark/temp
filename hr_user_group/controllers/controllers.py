# -*- coding: utf-8 -*-
from odoo import http

# class HrUserGroup(http.Controller):
#     @http.route('/hr_user_group/hr_user_group/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_user_group/hr_user_group/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_user_group.listing', {
#             'root': '/hr_user_group/hr_user_group',
#             'objects': http.request.env['hr_user_group.hr_user_group'].search([]),
#         })

#     @http.route('/hr_user_group/hr_user_group/objects/<model("hr_user_group.hr_user_group"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_user_group.object', {
#             'object': obj
#         })