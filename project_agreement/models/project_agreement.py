# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp

class projectAgreement(models.Model):
    _name = 'project.agreement'
    _inherit = ['mail.thread']
    
    @api.constrains('vat_percentage')
    def check_vat_percentage(self):
        if self.vat_percentage and (self.vat_percentage > 100 or self.vat_percentage < 0):
            raise ValidationError(_('Error!!, VAT Percentage must be between 0 and 100 only.'))
    
    
    name = fields.Char('Name' ,required=True ,states={'approved': [('readonly', True)]})
    code = fields.Char('Code' ,states={'approved': [('readonly', True)]})
    start_date = fields.Date('Start Date' , required=True ,states={'approved': [('readonly', True)]})
    end_date = fields.Date('End Date' , required=True ,states={'approved': [('readonly', True)]})
    project_id = fields.Many2one('project.project' ,'Project' ,states={'approved': [('readonly', True)]})
    state = fields.Selection([('draft','Draft'),('wating_approve','Wating Approve'),('approved','Approved'),('budget_generating','Budget generating'),
                              ('implementing','Implementing'),('refuse','Refused'), ('closed','Closed')] , default='draft', track_visibility='onchange')
    agreement_type = fields.Selection([('civil','Civil') , ('emergency' , 'Emergency'),('construction','Construction')] , default='civil' ,required=True)
    budget_id = fields.Many2one('crossovered.budget' ,'Budget' ,readonly=True )
    project_agreement_planned_line_ids = fields.Many2many('project.agreement.planned',domain=[('parent_id','=',False)])

    all_project_agreement_planned_line_ids = fields.One2many('project.agreement.planned', 'agreement_id')
    agreement_cost = fields.Monetary(compute='_compute_cost_revenue', string='Planned Cost', store=True)
    agreement_revenue = fields.Monetary(compute='_compute_cost_revenue', string='Planned Revenue', store=True)
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)] , required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    budget_id = fields.Many2one('crossovered.budget')
    budget_type = fields.Selection(string="Budget Type", selection=[('detail', 'Detail'), ('project', 'Project'), ], required=False,default='project')
    project_manager = fields.Many2one('res.users')
    vat_percentage = fields.Float(default=5,string="Vat Percentage %")
    vat_amount = fields.Float(readonly=1,compute="_compute_vat")
    total_after_vat = fields.Float(readonly=1,compute="_compute_vat")
    project_manager_recom = fields.Text()
    finance_manager_recom = fields.Text()
    assistant_executive_manager_recom = fields.Text()
    executive_manager_recom = fields.Text()

    @api.depends('vat_percentage','agreement_revenue','agreement_cost')
    def _compute_vat(self):
        for rec in self:
            if rec.agreement_cost and rec.agreement_revenue:
                amount = rec.agreement_cost + rec.agreement_revenue
                vat = amount * (rec.vat_percentage/100)
                rec.update({'vat_amount':vat,'total_after_vat':amount + vat})
            else:
                rec.update({'vat_amount':0,'total_after_vat':0})

    @api.multi
    def wating_approve(self):
        print("#####################",self.env.ref('account.data_account_type_expenses').id)
        self.write({'state': 'wating_approve'})

    @api.depends('project_agreement_planned_line_ids')
    def _compute_cost_revenue(self):
        for rec in self:
            rec.agreement_cost = sum(rec.project_agreement_planned_line_ids.mapped('total'))
            rec.agreement_revenue = sum(rec.project_agreement_planned_line_ids.mapped('revenue_amount'))


    @api.multi
    def approved(self):
        #=>create in emergency project , but specify account
        for rec in self:
            if len(rec.project_agreement_planned_line_ids) == 0:
                raise ValidationError(_('Please you must create planned lines under agreement planned page'))
            if not rec.project_manager:
                raise ValidationError(_('Please you must specify Project Manager For this Agreement'))
            if rec.agreement_type != 'emergency':
                rec.project_id = rec.project_id.create({
                    'name': rec.name,
                    'user_id': rec.project_manager.id,
                    'partner_id': rec.customer_id.id,
                })
            else:
                rec.create_material()
                for rec in self:
                    for line in rec.all_project_agreement_planned_line_ids:
                        line.write({'analytic_account_id': rec.project_id.analytic_account_id.id})
        self.write({'state': 'approved'})

    @api.multi
    def create_material(self):
        product = self.env['product.product']
        for rec in self:
            for line in rec.all_project_agreement_planned_line_ids:
                    record = product.create({
                        'name': line.name,
                        'uom_id': line.product_uom.id,
                        'uom_po_id': line.product_uom.id,
                        'standard_price': line.price_unit,
                        'property_account_expense_id' : line.account_id,
                        'sale_ok' : line.sale_ok ,
                        'purchase_ok' : line.purchase_ok,
                        'list_price': (line.price_unit * (line.revenue / 100)) + line.price_unit,
                        'type': line.stock_ok and 'product' or 'service',
                    })
                    line.product_id = record.id
            rec.write({'state': 'approved'})

    @api.multi
    def budget_generating(self):
        budegt_model = self.env['crossovered.budget']
        analytic_account = self.env['account.analytic.account']
        budgetary_model = self.env['account.budget.post']
        budget_lines = []
        total_amount = 0.0
        
        for rec in self:
            cost_center_found = False
            if rec.budget_type == 'detail':
                for line in rec.all_project_agreement_planned_line_ids:
                    if line.is_cost_center:
                        cost_center_found = True
                        #create analytic
                        analytic = analytic_account.create({
                            'name':line.name,
                        })

                        line.analytic_account_id = analytic
                        child_lines=rec.all_project_agreement_planned_line_ids.search([('parent_id', 'child_of', [line.id]),('is_cost_center','!=',True)])
                        child_lines.write({'analytic_account_id':analytic.id})
                        #print("Account child",child_lines)
                        account=[]
                        #if child_lines.mapped('account_id'):
                        for acc in child_lines:
                            if acc.account_id:
                               account.append(acc.account_id.id)
                        account.append(line.account_id.id)
                        print(account)
                        #create budgetary
                        budgetary = budgetary_model.create({
                            'name':line.name,
                            'account_ids':[(6, 0, account)],
                        })
                        total_amount = (line.type == 'view') and sum(line.child_ids.filtered(lambda x:x.is_cost_center != True).mapped('total')) or line.total
                        #add budget lines
                        budget_lines.append((0, 6, {
                                             'general_budget_id': budgetary.id,
                                             'analytic_account_id': analytic.id,
                                             'planned_amount': total_amount ,
                                             'date_from': rec.start_date,
                                             'date_to': rec.end_date,
                                             }))

            elif rec.budget_type == 'project':
                for line in rec.all_project_agreement_planned_line_ids:
                    if not line.parent_id:
                        print("111111111111111111")
                        line.write({'analytic_account_id': rec.project_id.analytic_account_id.id})
                        child_lines = rec.all_project_agreement_planned_line_ids.search(
                            [('parent_id', 'child_of', [line.id])])
                        child_lines.write({'analytic_account_id': rec.project_id.analytic_account_id.id})
                        # print("Account child",child_lines)
                        account = []
                        # if child_lines.mapped('account_id'):
                        print("222222222222222222222")
                        for acc in child_lines:
                            print("h11111111111",acc.account_id.id)
                            if acc.account_id.id:
                                print("h222222222222222")
                                if acc.account_id.id not in account:
                                    account.append(acc.account_id.id)
                        if line.account_id.id and line.account_id.id not in account:
                            account.append(line.account_id.id)
                        print(account)
                        # create budgetary
                        budgetary = budgetary_model.create({
                            'name': line.name,
                            'account_ids': [(6, 0, account)],
                        })
                        print("333333333333333333333333",line,line.total)
                        if line.type == 'view':
                            total_amount = line.cost
                        else:
                            total_amount = line.total
                        # add budget lines
                        budget_lines.append((0, 6, {
                            'general_budget_id': budgetary.id,
                            'analytic_account_id': rec.project_id.analytic_account_id.id,
                            'planned_amount': total_amount,
                            'date_from': rec.start_date,
                            'date_to': rec.end_date,
                            'price_unit':line.price_unit,
                            'required_quantity':line.required_quantity,
                            'total':line.total,
                        }))
                        print("44444444444444444444")
            if self.agreement_type != 'emergency' and rec.all_project_agreement_planned_line_ids.search([('agreement_id','=',self.id),'|',('analytic_account_id', '=', False),('account_id','=',False)]):
                    print("IIIIIIIIIIIIIIIIII")
                    non_analytic_account= rec.all_project_agreement_planned_line_ids.search([('agreement_id','=',self.id),'|',('analytic_account_id', '=', False),('account_id','=',False)])
                    raise ValidationError(_('Please you must specify one cost center for  agreement plan line %s' )%(non_analytic_account.mapped('name')))
            
            #create budget                                                      
            budget_record = budegt_model.create({
                'name': rec.name,
                'date_from': rec.start_date,
                'date_to': rec.end_date,
                'crossovered_budget_line': budget_lines,

            })  

            #link budget to aggrement record
            rec.budget_id = budget_record.id

            #Create Products
            rec.create_material()

            rec.write({'state': 'budget_generating'})

    @api.multi
    def implementing(self):
        self.write({'state': 'implementing'})

    @api.multi
    def closed(self):
        self.write({'state': 'closed'})

    @api.multi
    def refuse(self):
        self.write({'state': 'refuse'})
    
class projectAgreementLine(models.Model):
    _name = 'project.agreement.planned'


    @api.constrains("revenue")
    def check_revenue_percentage(self):
        if self.revenue > 100 or self.revenue < 0:
             raise ValidationError(_('Revenue must be between 0 and 100: )'))

    @api.model
    def _getAccounts(self):
        return [('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)]

    name = fields.Char('Name' , required=True)
    code = fields.Char('Code')
    agreement_id = fields.Many2one('project.agreement' , 'Agreement')
    project_id = fields.Many2one('project.project',related='agreement_id.project_id',store=True)
    product_id = fields.Many2one('product.product','Product' , readonly=1 )
    required_quantity = fields.Float(string='Required Qty',)
    delivered_quantity = fields.Monetary(string='Delivered Qty')
    residual_quantity = fields.Monetary(compute='_compute_residual_quantity', string='Residual Qty')
    product_uom = fields.Many2one('product.uom' , 'Unit of Measuer',required=1)
    price_unit = fields.Monetary('Unit Price',digits=dp.get_precision('Price'))
    total = fields.Monetary(string='Total Cost',compute='compute_total_amount')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    revenue = fields.Float('Revenue %' , required=1)
    revenue_amount = fields.Monetary(compute='_compute_revenue', string='Revenue Amount', )
    analytic_account_id = fields.Many2one('account.analytic.account' , 'Cost Center', readonly=True)
    account_id = fields.Many2one('account.account', string='Account' ,domain=_getAccounts)
    is_cost_center = fields.Boolean('Is Cost Center')
    type = fields.Selection([('view' , 'View') , ('material' , 'Material') , ('internal','Internal Workers') , ('other' , 'Other')] ,required=True)
    progress = fields.Float('Progress %')
    responsible_id = fields.Many2one('res.partner', string='Responsible')
    parent_id = fields.Many2one('project.agreement.planned', string='Parent' ,  ondelete='cascade',)
    state = fields.Selection([('draft','Draft'),('wating_approve','Wating Approve'),('approved','Approved'),('budget_generating','Budget generating'),
                              ('implementing','Implementing'),('refuse','Refused'), ('closed','Closed')] ,related="agreement_id.state")
    child_ids = fields.One2many('project.agreement.planned',inverse_name="parent_id",string="Child Items")
    agreement_type = fields.Selection([('civil','Civil'),('emergency','Emergency'),('construction','Construction')] ,related="agreement_id.agreement_type",store=True)
    sale_ok = fields.Boolean(
        'Can be Deliver', default=True,
        help="Specify if the product can be selected in a sales order line.")
    purchase_ok = fields.Boolean('Can be Purchased', default=True)
    stock_ok = fields.Boolean('Can Stored')
    set_to_child = fields.Boolean()

    cost = fields.Float(compute="_sum_lines_total",string="Lines Total Cost")




    @api.multi
    @api.depends('child_ids')
    def _sum_lines_total(self):
        for rec in self:
            agreement_planned_obj = self.env['project.agreement.planned']
            agreement_planned_ids = agreement_planned_obj.search([('parent_id','=',rec.id)])

            total = sum(agreement_planned_ids.mapped('total'))
            rec.cost = total

    @api.model
    def create(self, vals):
        #if vals.get('total',False) and vals.get('required_quantity',False) != 0:
        #    vals['price_unit'] = vals['total'] / vals['required_quantity']
        return super(projectAgreementLine, self).create(vals)
    
    def write(self,vals):
        #if vals.get('total',False) and vals.get('required_quantity',False) != 0:
        #    vals['price_unit'] = vals.get('total',self.total) / vals.get('required_quantity',self.required_quantity)
        return super(projectAgreementLine, self).write(vals)
   
    @api.onchange('set_to_child','account_id')
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
                    elif rec.set_to_child == False and child.account_id.id  == rec.account_id.id :
                        child.write({
                            'account_id': False,
                        })
                

    '''@api.onchange('product_id')
    def set_product_qty(self):
        """
        when select product set product cost price
        """
        for line in self:
            line.update({
                'price_unit': line.product_id.standard_price,
            })'''


    @api.depends('required_quantity','price_unit','child_ids','type')
    def compute_total_amount(self):
        print("Compute>>>>>>>>>>>>>>>")
        for rec in self:
            if rec.type != 'view':
                if rec.agreement_type != 'emergency' and rec.required_quantity != 0:
                    rec.total = rec.price_unit * rec.required_quantity
                else:
                    rec.total = rec.price_unit
            else:
                print("HERRRRRRRRRRRRRR",sum(rec.child_ids.mapped('total')))
                rec.total = rec.child_ids and sum(rec.child_ids.mapped('total')) or 0.0
                rec.price_unit = rec.required_quantity != 0 and rec.total / rec.required_quantity or 0.0


    """@api.depends('required_quantity', 'price_unit')
    def _compute_amount(self):
        if type != 'view':
            for line in self:
                line.update({
                    'total': line.required_quantity * line.price_unit,
                })
        else:
            for line in self:
                line.update({
                    'total': line.child_ids and sum(line.child_ids.mapped('total')) or 0.0,
                })"""

    @api.depends('required_quantity', 'delivered_quantity')
    def _compute_residual_quantity(self):

       for line in self:
           line.update({
               'residual_quantity' : line.required_quantity - line.delivered_quantity
           })

    @api.depends('total', 'revenue')
    def _compute_revenue(self):
        for line in self:
            line.update({
                'revenue_amount': (line.revenue / 100)*line.total
            })



class CrossoveredBudget(models.Model):
    _name = "crossovered.budget"
    _description = "Budget"
    _inherit = ['crossovered.budget']


    agreement_ids = fields.One2many('project.agreement',inverse_name="budget_id",string="Agreements")

    @api.multi
    def button_agreements(self):
        if self.agreement_ids:
            views = [(self.env.ref('project_agreement.view_project_agreement_tree').id, 'tree'), (self.env.ref('project_agreement.view_project_agreement_form').id, 'form')]
        return {
            'name': _('Agreements'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.agreement',
            'view_id': False,
            'views': views,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.agreement_ids])],
        }
