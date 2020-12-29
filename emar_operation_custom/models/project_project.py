# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'
    state = fields.Selection([("draft", "Draft"), ("pend", "Pending"), ("under", "Under Study"),
                              ("wait", "Wainting"), ("run", "Running"), ("cancel", "Canceled")], default="draft")
    project_type = fields.Selection([
        ('supply', 'Supply Only'),
        ('installation', 'Installation Only'),
        ('supply_installation', 'Supply and Installation'),
    ], string='Project Type', translate=True)

    project_code = fields.Char("Project Code")
    project_cost_account = fields.Many2one("account.account")
    company_operation_account = fields.Many2one("account.account", "Company operation costing account")
    project_warehouse = fields.Many2one("stock.warehouse")
    purchase_engineer = fields.Many2one("res.users")
    start_date = fields.Date("Project Start Date")
    end_date = fields.Date("Project End Date")
    agreement_id = fields.Many2one("project.agreement")
    agreement_type = fields.Selection(related="agreement_id.agreement_type")
    #  Adding project profile data will be explained later
    project_profile = fields.Binary("Project Profile", attachment=True)
    project_profile_filename = fields.Char()
    team_lines = fields.One2many("project.team.member", "project")
    raw_task = fields.Many2one("project.task", "Task of raw material")

    main_items = fields.One2many("project.agreement.planned", "project_id")
    raw_items = fields.One2many("project.agreement.raw.material.line", "project_id")

    def send_notification(self):
        # todo:sending notification to the Users for the tasks

        pass

    def start_study(self):
        # todo logic
        # all project task states should be "waiting"
        # send notification to Accounting Manager to print Technical and Financial Proposals
        # Planning Engineer should not access planning lines in tasks
        # the editing in the lines is reflecting on agreement and project is that okay ??
        # - PM should add PM extra cost in lines to be able to take this action ???
        self.ensure_one()
        for task in self.task_ids:
            task.state = 'under'
        self.state = "pend"

    def cancel(self):
        self.state = "cancel"

    def closed(self):
        # only if account manager add assigned hard copy
        # send notification to CEO , Account Manager and Responsible Engineers in tasks
        # related tasks will convert to close
        self.ensure_one()
        for task in self.task_ids:
            task.state = 'close'

    def generate_tasks(self):
        # todo: call send notification for all users related to the tasks
        # Read the main_items and generate task per each line
        # - Task Name: main item in line
        # - Project: Current        Project       Code
        # - Planning  Engineer: Pre - sales  engineer in line      of    main   item
        # - Purchase    Manager: If     project type     "Both"
        # - Scheduled Start Date: in main item line
        # - Scheduled End Date: in main item line
        # - Raw Material Lines:   from raw material tab if project     type is "Both"
        # - AnalyticAccount: from project form
        for rec in self.main_items:
            rec.task_id = self.task_ids.create({
                'main_item_id': rec.id,
                'project_id': self.id,
                'presale_eng': rec.pre_sales_engineer.id
            })

        self.state = "under"

    def study_finish(self):
        self.state = "wait"
        self.ensure_one()
        for task in self.task_ids:
            task.state = 'wait'

    def print_financial(self):
        pass


class projectTeam(models.Model):
    _name = "project.team.member"
    project = fields.Many2one("project.project")
    title = fields.Many2one("res.partner.title")
    count = fields.Integer()
    in_main = fields.Boolean("In main items?")
    cost = fields.Float("cost per hour")
    total_hour = fields.Float()
    total_cost = fields.Float(compute="get_total", stored=True)

    @api.depends("cost", "total_hour")
    @api.one
    def get_total(self):
        self.total_cost = self.total_hour * self.cost


class mainitemline(models.Model):
    _inherit = "project.agreement.planned"


class rawMaterialLine(models.Model):
    _inherit = "project.agreement.raw.material.line"

    main_working_item_id = fields.Many2one("project.agreement.planned")  # not nessery field already used parent_id
    task_id = fields.Many2one(related="parent_id.task_id")
    planned_unit_cost = fields.Float()
    remaining_quantity = fields.Float(compute="compute_remain_qty")
    line_planned_cost = fields.Float(compute="compute_plan_cost")

    @api.one
    def compute_plan_cost(self):
        self.line_planned_cost = self.required_quantity * self.planned_unit_cost

    @api.one
    def compute_remain_qty(self):
        # todo :should be depends on purchase ordered Qtys

        self.remaining_quantity = 10


class workingItemLine(models.Model):
    _name = "working.item.line"

    task_id = fields.Many2one("project.task")
    working_item = fields.Many2one("product.product", domain=[("product_subtype", '=', "working_items")])
    uom_cat_id = fields.Many2one(related="working_item.uom_id.category_id")
    uom_id = fields.Many2one("product.uom")
    planned_unit_cost = fields.Float()
    planned_quantity = fields.Float()
    line_planned_cost = fields.Float(compute="compute_plan_cost", stored=True)

    @api.one
    @api.depends("planned_unit_cost", "planned_quantity")
    def compute_plan_cost(self):
        self.line_planned_cost = self.planned_quantity * self.planned_unit_cost


class CustodySettlement(models.Model):
    _name = "custody.settlement"
    task_id = fields.Many2one("project.task")
    name = fields.Char('Description')
    amount = fields.Float()
    state = fields.Selection([("draft", "Draft"), ("confirmed", "Confirmed")], default="draft")
    # todo : the logic will be added here later


class ProjectTask(models.Model):
    _inherit = "project.task"

    # todo : pre-sales access tasks in planing sate only "rule"
    # - smart buttons : assign documents, progress bills, purchase orders, receipt orders, vendor bills,
    # custody settlements, journal entries
    # - Working item line : show only in case of project type both or installation

    main_item_id = fields.Many2one("project.agreement.planned")
    name = fields.Char(related="main_item_id.name")
    presale_eng = fields.Many2one("res.users", "pre sales engineer")
    purchase_manager = fields.Many2one("res.users", "Purchase Manager")
    start_date = fields.Date("Schedule Start Date")
    end_date = fields.Date("Schedule End Date")
    working_item_palnned_cost = fields.Float(compute="compute_planned_cost")
    working_item_palnned_qty = fields.Float(compute="compute_planned_qty")
    raw_material_planned_cost = fields.Float(compute="compute_raw_cost")
    account_analytic_id = fields.Many2one("account.analytic.account", related="project_id.analytic_account_id")
    raw_material_ids = fields.One2many("project.agreement.raw.material.line", "task_id")
    working_item_ids = fields.One2many("working.item.line", "task_id")
    custody_lines = fields.Many2many("custody.settlement")
    state = fields.Selection([('draft', 'Draft'), ('under', "Under study"),
                              ("wait", "Waiting"), ("run", "Running"), ("close", "Closed")
                              ], default="draft")
    project_type = fields.Selection(related='project_id.project_type')

    def receipt_orders(self):
        # todo: get all stock  receipts
        pass

    def assign_docs(self):
        # todo: get all docs
        pass

    def progress_bill(self):
        # todo : get all  progress bills
        pass

    def purchase_order(self):
        # todo: get all POs
        pass

    def custody_settlements(self):
        # todo : get all
        pass

    def all_entries(self):
        # todo: get all
        pass

    def generate_custody_settlement_entry(self):
        # todo:
        pass

    @api.one
    def compute_raw_cost(self):
        self.raw_material_planned_cost = \
            sum(self.raw_material_ids.mapped("total"))

    @api.one
    def compute_planned_qty(self):
        self.working_item_palnned_qty = \
            sum(self.working_item_ids.mapped('planned_quantity'))

    @api.one
    def compute_planned_cost(self):
        self.working_item_palnned_cost = \
            sum(self.working_item_ids.mapped('planned_unit_cost'))
