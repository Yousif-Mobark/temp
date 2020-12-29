# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class ProjectAgreement(models.Model):
    _inherit = 'project.agreement'

    def _get_default_code(self):
        return self.env['ir.sequence'].next_by_code('project.agreement.code.sequence') or ''

    state = fields.Selection([('draft', 'Draft'), ('pq', 'PQ'),
                              ('waiting_approve', 'Waiting Approval'), ('approved', 'Approved'),
                              ('aq', 'AQ'),
                              ('refuse', 'Rejected'), ('closed', 'Canceled')],
                             default='draft', track_visibility='onchange')
    rm_agreement_cost = fields.Monetary(compute='_compute_cost_revenue', default=0,
                                        string='Planned Cost', store=True)
    rm_agreement_revenue = fields.Monetary(compute='_compute_cost_revenue', string='Planned Revenue', default=0,
                                           store=True)
    pm_added_revenue = fields.Monetary(compute='_compute_cost_revenue', string='PM Added Revenue', store=True,
                                       default=0)
    rm_vat_amount = fields.Monetary(string='VAT', default=0,
                                    store=False, compute="_compute_rm_vat")
    rm_total_after_vat = fields.Monetary(compute='_compute_rm_vat', string='Total after VAT', default=0,
                                         store=True)
    analytic_id = fields.Many2one('account.analytic.account',
                                  related="project_id.analytic_account_id", string="Analytic Account")
    code = fields.Char('Code', states={'approved': [('readonly', True)]},
                       default=_get_default_code,
                       required=1)
    name = fields.Char('Project', required=True, states={'approved': [('readonly', True)]})
    total_untaxed = fields.Monetary("Total", compute="_compute_total_untaxed")
    rm_total_untaxed = fields.Monetary("Total", compute="_compute_total_untaxed")
    total_financial_offer_untaxed = fields.Monetary("Total Financial Offer without Tax", compute="_compute_t_o_w_t")
    total_tax = fields.Monetary("Tax", compute="_compute_total_taxes")
    project_grand_total_offer = fields.Monetary("Total", compute="_compute_grand_total_offer")
    project_raw_material_line_ids = fields.One2many('project.agreement.raw.material.line', 'agreement_id')

    def _compute_total_untaxed(self):
        for rec in self:
            rec.total_untaxed = rec.pm_added_revenue + rec.agreement_cost + rec.agreement_revenue
            rec.rm_total_untaxed = rec.rm_agreement_cost + rec.rm_agreement_revenue

    def _compute_grand_total_offer(self):
        for rec in self:
            rec.project_grand_total_offer = rec.total_financial_offer_untaxed + rec.total_tax

    def _compute_t_o_w_t(self):
        for rec in self:
            rec.total_financial_offer_untaxed = rec.total_untaxed + rec.rm_total_untaxed

    def _compute_total_taxes(self):
        for rec in self:
            rec.total_tax = rec.vat_amount + rec.rm_vat_amount

    def _compute_cost_revenue(self):
        for rec in self:
            rec.agreement_cost = sum(rec.project_agreement_planned_line_ids.mapped('total'))
            rec.agreement_revenue = sum(rec.project_agreement_planned_line_ids.mapped('revenue_amount'))
            rec.rm_agreement_cost = sum(rec.project_raw_material_line_ids.mapped('total'))
            rec.rm_agreement_revenue = sum(rec.project_raw_material_line_ids.mapped('revenue_amount'))
            rec.pm_added_revenue = sum(rec.project_agreement_planned_line_ids.mapped('pm_revenue'))

    @api.depends('vat_percentage', 'rm_agreement_revenue', 'rm_agreement_cost')
    def _compute_rm_vat(self):
        print("##############################################")
        for rec in self:
            print("***********************************************************************************8")
            if rec.rm_agreement_revenue and rec.rm_agreement_cost:
                rm_amount = rec.rm_agreement_cost + rec.rm_agreement_revenue
                rm_vat = rm_amount * (rec.vat_percentage/100)
                rec.update({'rm_vat_amount': rm_vat, 'rm_total_after_vat': rm_amount + rm_vat})
            else:
                rec.update({'rm_vat_amount': 0, 'rm_total_after_vat': 0})

    @api.depends('vat_percentage', 'agreement_revenue', 'agreement_cost', 'pm_added_revenue')
    def _compute_vat(self):
        for rec in self:
            if rec.agreement_cost and rec.agreement_revenue:
                amount = rec.agreement_cost + rec.agreement_revenue + rec.pm_added_revenue
                vat = amount * (rec.vat_percentage/100)
                rec.update({'vat_amount': vat, 'total_after_vat': amount + vat})
            else:
                rec.update({'vat_amount': 0, 'total_after_vat': 0})

    def action_start_studying(self):
        self.state = 'pq'
        res = self.env['project.project'].create({'name': self.name, 'project_type': self.project_type,
                                                  'agreement_id': self.id})
        res.project_warehouse = self.env['stock.warehouse'].create({'name': 'WH-' + self.code or '',
                                                                    'code': 'WH' + str(self.id) or ''}).id
        res.analytic_account_id.name = self.code
        res.project_code = self.code
        self.project_id = res.id
        domain = [("groups_id", "=", self.env.ref("emar_operation_custom.group_pre_sales_engineer").id)]
        pre_sales_engineers = self.env['res.users'].search(domain)
        users_to_notify = pre_sales_engineers
        users_to_notify += self.project_manager

        self.env['mail.message'].create({'message_type': "notification",
                                         "subtype": self.env.ref("mail.mt_comment").id,
                                         'body': "Study Has Started",
                                         'subject': "Project Study",
                                         'needaction_partner_ids': [(4, user.partner_id.id) for user in users_to_notify],
                                         'model': self._name,
                                         'res_id': self.id,
                                         })

    @api.depends('vat_percentage', 'agreement_revenue', 'agreement_cost')
    def _compute_vat(self):
        for rec in self:
            if rec.agreement_cost and rec.agreement_revenue:
                amount = rec.agreement_cost + rec.agreement_revenue
                vat = amount * (rec.vat_percentage/100)
                rec.update({'vat_amount': vat, 'total_after_vat': amount + vat})
            else:
                rec.update({'vat_amount': 0, 'total_after_vat': 0})

    def action_send_for_approval(self):
        self.state = 'waiting_approve'

    def action_approve(self):
        self.state = 'approved'

    def action_reject(self):
        self.state = 'refuse'

    def action_cancel(self):
        self.state = 'closed'

    def action_assigned(self):
        self.state = 'aq'
        pre_sales_engineers = self.env['res.users'].search(
            [("groups_id", "=", self.env.ref("emar_operation_custom.group_pre_sales_engineer").id)])
        ceos = self.env['res.users'].search(
            [("groups_id", "=", self.env.ref("emar_operation_custom.group_hr_ceo").id)])
        users_to_notify = pre_sales_engineers
        users_to_notify += ceos
        users_to_notify += self.project_manager
        self.ensure_one()
        for task in self.project_id.task_ids:
            task.state = 'run'
        self.env['mail.message'].create({'message_type': "notification",
                                         "subtype": self.env.ref("mail.mt_comment").id,
                                         'body': "Project Assigned",
                                         'subject': "Project Assigned",
                                         'needaction_partner_ids': [(4, user.partner_id.id) for user in
                                                                    users_to_notify],
                                         'model': self._name,
                                         'res_id': self.id,
                                         })

    @api.constrains('code')
    def _check_if_code_is_unique(self):
        pg = self.search([('code', '=', self.code)])
        if len(pg) > 1:
            raise ValidationError(_('Another Project Agreement Has The Same Code!!'))


class ProjectAgreementRMLine(models.Model):
    _name = 'project.agreement.raw.material.line'

    @api.constrains("revenue")
    def check_revenue_percentage(self):
        if self.revenue > 100 or self.revenue < 0:
            raise ValidationError(_('Revenue must be between 0 and 100: )'))

    @api.model
    def _getAccounts(self):
        return [('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)]

    @api.model
    def _getProducts(self):
        return [('product_subtype', '=', 'raw_material')]

    code = fields.Char('Code')
    agreement_id = fields.Many2one('project.agreement', 'Agreement')
    project_id = fields.Many2one('project.project', related='agreement_id.project_id', store=True)
    product_id = fields.Many2one('product.product', 'Raw material', readonly=0, domain=_getProducts)
    required_quantity = fields.Float(string='Required Qty', )
    delivered_quantity = fields.Monetary(string='Delivered Qty')
    expected_delivery_date = fields.Date("Expected Delivery Date")
    residual_quantity = fields.Monetary(compute='_compute_residual_quantity', string='Residual Qty')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', required=1, related='product_id.uom_id')
    price_unit = fields.Monetary('Unit Price', digits=dp.get_precision('Price'))
    total = fields.Monetary(string='Total Cost', compute='compute_total_amount')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    revenue = fields.Float('Revenue %', required=1)
    revenue_amount = fields.Monetary(compute='_compute_revenue', string='Revenue Amount', )
    account_id = fields.Many2one('account.account', string='Account', domain=_getAccounts)
    is_cost_center = fields.Boolean('Is Cost Center')
    type = fields.Selection(
        [('view', 'View'), ('material', 'Material'), ('internal', 'Internal Workers'), ('other', 'Other')],
        required=False)
    progress = fields.Float('Progress %')
    responsible_id = fields.Many2one('res.partner', string='Responsible')
    parent_id = fields.Many2one('project.agreement.planned', string='Parent', ondelete='cascade', )
    state = fields.Selection([('draft', 'Draft'), ('wating_approve', 'Wating Approve'), ('approved', 'Approved'),
                              ('budget_generating', 'Budget generating'),
                              ('implementing', 'Implementing'), ('refuse', 'Refused'), ('closed', 'Closed')],
                             default='draft')
    child_ids = fields.One2many('project.agreement.planned', inverse_name="parent_id", string="Child Items")
    agreement_type = fields.Selection(
        [('civil', 'Civil'), ('emergency', 'Emergency'), ('construction', 'Construction')],
        related="agreement_id.agreement_type", store=True)
    sale_ok = fields.Boolean(
        'Can be Deliver', default=True,
        help="Specify if the product can be selected in a sales order line.")
    purchase_ok = fields.Boolean('Can be Purchased', default=True)
    stock_ok = fields.Boolean('Can Stored')
    set_to_child = fields.Boolean()
    pre_sales_engineer = fields.Many2one('res.users', "Pre-Sales Engineer",
                                         domain=lambda self: [("groups_id", "=", self.env.ref("emar_operation_custom.group_pre_sales_engineer").id)])

    cost = fields.Float(compute="_sum_lines_total", string="Lines Total Cost")

    @api.multi
    @api.depends('child_ids')
    def _sum_lines_total(self):
        for rec in self:
            agreement_planned_obj = self.env['project.agreement.planned']
            agreement_planned_ids = agreement_planned_obj.search([('parent_id', '=', rec.id)])

            total = sum(agreement_planned_ids.mapped('total'))
            rec.cost = total

    @api.model
    def create(self, vals):
        return super(ProjectAgreementRMLine, self).create(vals)

    def write(self, vals):
        return super(ProjectAgreementRMLine, self).write(vals)

    @api.onchange('set_to_child', 'account_id')
    def onchange_set_to_child_account(self):
        """
        when select set_to_child set account = parent account
        """

        for rec in self:
            if rec.child_ids:
                for child in rec.child_ids:
                    if rec.set_to_child == True:
                        child.write({
                            'account_id': rec.account_id.id,
                        })
                    elif rec.set_to_child == False and child.account_id.id == rec.account_id.id:
                        child.write({
                            'account_id': False,
                        })

    @api.depends('required_quantity', 'price_unit', 'child_ids', 'type')
    def compute_total_amount(self):
        for rec in self:
            if rec.type != 'view':
                if rec.agreement_type != 'emergency' and rec.required_quantity != 0:
                    rec.total = rec.price_unit * rec.required_quantity
                else:
                    rec.total = rec.price_unit
            else:
                rec.total = rec.child_ids and sum(rec.child_ids.mapped('total')) or 0.0
                rec.price_unit = rec.required_quantity != 0 and rec.total / rec.required_quantity or 0.0

    @api.depends('required_quantity', 'delivered_quantity')
    def _compute_residual_quantity(self):

        for line in self:
            line.update({
                'residual_quantity': line.required_quantity - line.delivered_quantity
            })

    @api.depends('total', 'revenue')
    def _compute_revenue(self):
        for line in self:
            line.update({
                'revenue_amount': (line.revenue / 100) * line.total
            })


class ProjectAgreementLine(models.Model):
    _inherit = 'project.agreement.planned'

    expected_end_date = fields.Date("Expected End Date")
    pm_revenue = fields.Float("PM Revenue")
    task_id = fields.Many2one("project.task")
    pre_sales_engineer = fields.Many2one("res.users", "Pres-Sales Engineer", domain=lambda self: [("groups_id", "=",  self.env.ref( "emar_operation_custom.group_pre_sales_engineer").id)])
    working_item_id = fields.Many2one("working.item")
    name =fields.Char(related="working_item_id.name",required=False)