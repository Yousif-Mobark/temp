# -*- coding: utf-8 -*-
from odoo import http

# class StationArea(http.Controller):
#     @http.route('/station_area/station_area/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/station_area/station_area/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('station_area.listing', {
#             'root': '/station_area/station_area',
#             'objects': http.request.env['station_area.station_area'].search([]),
#         })

#     @http.route('/station_area/station_area/objects/<model("station_area.station_area"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('station_area.object', {
#             'object': obj
#         })