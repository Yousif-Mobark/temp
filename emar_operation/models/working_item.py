# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WorkingItem(models.Model):
    _name = 'working.item'
    _description = "Working Item"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", requierd=True, track_visibility='onchange')
    code = fields.Char(string="Code", requierd=True, track_visibility='onchange')
