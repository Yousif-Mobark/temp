# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_type = fields.Selection([
        ('supply', 'Supply Only'),
        ('installation', 'Installation Only'),
        ('supply_installation', 'Supply and Installation'),
    ], string='Project Type', translate=True)

    project_code = fields.Char("Project Code")
    project_cost_account = fields.Many2one("account.account")
    company_operation_account= fields.Many2one("account.account","Company operation costing account")
    project_warehouse = fields.Many2one("stock.warehouse")
    purchase_engineer = fields.Many2one("res.users")
    start_date = fields.Date("Project Start Date")
    end_date = fields.Date("Project End Date")
    agreement_id = fields.Many2one("project.agreement")
    agreement_type=fields.Selection(related="agreement_id.agreement_type")
    #  Adding project profile data will be explained later


    #
    team_lines  = fields.One2many("project.team.member","project")
    raw_task = fields.Many2one("project.task","Task of raw material")

    main_items = fields.One2many("project.agreement.planned","project_id")
    raw_items  = fields.One2many("project.agreement.raw.material.line","project_id")







class projectTeam(models.Model):
    _name = "project.team.member"
    project = fields.Many2one("project.project")
    title = fields.Many2one("res.partner.title")
    count = fields.Integer()
    in_main= fields.Boolean("In main items?")
    cost   = fields.Float("cost per hour")
    total_hour = fields.Float()
    total_cost  = fields.Float()