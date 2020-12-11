# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class stationStation(models.Model):
    _name = 'station.station'

    name = fields.Char('Name' , required=True)
    user_id = fields.Many2one( 'res.users', 'Manager', required=True)
    super_user_id = fields.Many2one('res.users', 'Supervisior', required=True)
    project_ids = fields.Many2many('project.project', 'project_station_relation','station_id', 'project_id', 'Projects')
    area_id = fields.Many2one('area.area', 'Area')
    purchase_order_line_ids = fields.One2many('purchase.order.line','station',readonly=1)








class areaArea(models.Model):
    _name = 'area.area'

    name = fields.Char('Name' , required=True)
    user_id = fields.Many2one('res.users', 'Manager', required=True)
    super_user_id = fields.Many2one('res.users', 'Supervisior', required=True)
    project_ids = fields.Many2many('project.project', 'project_area_relation' ,'area_id', 'project_id', 'Projects')
    station_ids = fields.One2many('station.station', 'area_id' ,'Stations',)
    purchase_order_line_ids = fields.One2many('purchase.order.line','area',readonly=1)

class purchaseOrder(models.Model):
    _inherit = 'purchase.order'

    station = fields.Many2one('station.station' , 'Station' ,related='requisition_id.station',store=True)
    area = fields.Many2one('area.area' , 'Area' , related='requisition_id.area',store=True)


class purchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    station = fields.Many2one('station.station','Station' , related="order_id.station" , store=True)
    area = fields.Many2one('area.area', 'Area', related="order_id.area" , store=True)


class purchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    station = fields.Many2one('station.station','Area')
    area = fields.Many2one('area.area','Station')


class purchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'


    station = fields.Many2one('station.station','Station', related="requisition_id.station",store=True)
    area = fields.Many2one('area.area', 'Area',related="requisition_id.area",store=True)
