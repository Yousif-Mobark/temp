# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,tools
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class projectAgreementTendarWizard(models.TransientModel):
    _name = 'project.agreement.tendar.wizard'
    
    agreement_id = fields.Many2one('project.agreement' , 'Agreement',readonly=True)
    agreement_type = fields.Selection([('civil','Civil') , ('emergency' , 'Emergency'),('construction','Construction')], related='agreement_id.agreement_type')
    wizard_type = fields.Selection([('all', 'All'), ('one', 'One')])
    #project_agreement_planned_line_ids = fields.One2many('project.agreement.planned','agreement_id',domain=[('type','=','material')])
    project_agreement_tendar_line_ids = fields.One2many('project.agreement.tendar.line.wizard','tendar_wizard_id')
    
    start_date = fields.Date('Start Date' )
    end_date = fields.Date('End Date')
    station = fields.Many2one('station.station')
    area = fields.Many2one('area.area')
    partner_id = fields.Many2one('res.partner',domain=[('supplier','=',True)],string="Vendor")
    reason = fields.Text(string="Overdraw Reason")
    attach_files_ids = fields.Many2many('ir.attachment',string="Attachment Files"#,relation="attach_attachment"
    )

    def request_overdraw_from_manager(self):
        """
        Send Mail When Overdraw
        :return:
        """
        ir_mail_server = self.env['ir.mail_server'].search([])
        message = ""
        for line in self.project_agreement_tendar_line_ids:
            if line.overdraw:
                message += "\n The Following "+ line.agreement_planned_id.name + " Item's Planned QTY is "+ str(line.required_quantity) +" "+line.product_uom.name+ " Required QTY " + str(line.residual_to_purchase)+" "+line.product_uom.name + "\n"
        message += "Reason for overdraw :"+ "  "+ self.reason
        message += "\n\n"+ "Please Allow overdraw for the previous item's"
        message += "\n\n\n\n"+ "Regards, " + "\n\n" + self.env.user.partner_id.name
        if ir_mail_server:
            try:
                email = ir_mail_server.build_email(email_from=self.env.user.partner_id.email,email_to=[self.agreement_id.project_id.user_id.partner_id.email],
                                                   subject=str("Overdraw For " + self.agreement_id.name + "-"+ self.agreement_id.project_id.name), body=message)
                ir_mail_server.send_email(email)
            except Exception as e:
                _logger.error("Exception while sending traceback by email: %s.\n Original Traceback:\n%s", e)
                pass
        return True

    @api.model
    def default_get(self,vals):
        """
        when create new record set country state automatically in one2many
        """
        values = []
        # agreement_obj = self.env['project.agreement']
        # agreement_id = agreement_obj.search([('id','=',self.agreement_id.id)])
        # for rec in agreement_id.project_agreement_planned_line_ids.filtered( lambda r: r.type != "material" ):
        #     values.append((0, 0, {'state_id':rec.id,'ship_value':0,'ship_value_plus':0}))
        res = super(projectAgreementTendarWizard, self).default_get(vals)
            
        # res.update({'ship_pricelist_line_ids': values})
        return res

    
    def button_create_tendar(self):
        tendar_obj = self.env['purchase.requisition']
        lines = []
        if not self.project_agreement_tendar_line_ids:
            raise ValidationError(_('Sorry Please Add Line First'))
        for line in self.project_agreement_tendar_line_ids:
            if line.overdraw == True :
                raise ValidationError(_('Sorry you Overdraw Planned QTY For %s , Please Send Overdraw Request To Manager') % (line.name))
            lines.append((0, 6, {
                'product_id': line.agreement_planned_id.product_id.id,
                'product_qty': line.residual_to_purchase,
                'product_uom_id': line.product_uom.id,
                'price_unit': line.price_unit,
                'previous_purchased': line.previous_purchased,
                'agreement_planned_id':line.agreement_planned_id.id,
                'account_analytic_id' : line.agreement_planned_id.analytic_account_id.id ,

                # 'agreement_type':self.agreement_type,
                'start_date' :self.start_date,
                'end_date': self.end_date,
                'station':self.station.id ,
                'area':self.area.id ,

            }))
            line.agreement_planned_id.requested_qty += line.residual_to_purchase
        
        record = tendar_obj.create(
            {
            'type':self.env.ref('purchase_requisition.type_multi').id,
            'vendor_id':self.partner_id.id,
            'agreement_id':self.agreement_id.id,
            'line_ids':lines
        })
        for line in self.attach_files_ids:
            line.res_id = record.id
            line.res_model = 'purchase.requisition' 

        
        

    @api.onchange('start_date','end_date')
    def onchange_date(self):
                
        if self.agreement_type == 'emergency':
            start_date = datetime.strptime(self.start_date, tools.DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.strptime(self.end_date, tools.DEFAULT_SERVER_DATE_FORMAT)

            delta = end_date - start_date
            
                
            for line in self.project_agreement_tendar_line_ids:
                line.required_quantity = delta.days
                line.residual_to_purchase = line.required_quantity


class projectAgreementTendarLineWizard(models.TransientModel):
    _name = 'project.agreement.tendar.line.wizard'
    
    @api.constrains('vat_percentage')
    def check_vat_percentage(self):
        if self.vat_percentage and (self.vat_percentage > 100 or self.vat_percentage < 0):
            raise ValidationError(_('Error!!, VAT Percentage must be between 0 and 100 only.'))
    
    name = fields.Char('Name' ,)
    #number = fields.Char('Code')
    tendar_wizard_id = fields.Many2one('project.agreement.tendar.wizard' )
    agreement_id = fields.Many2one('project.agreement' , 'Agreement')
    agreement_planned_id = fields.Many2one('project.agreement.planned' )
    product_id = fields.Many2one('product.product','Product' , readonly=1 )
    required_quantity = fields.Float(string='Required Qty',related='agreement_planned_id.required_quantity')
    product_uom = fields.Many2one('product.uom' , 'Unit of Measuer',related='agreement_planned_id.product_uom')
    price_unit = fields.Monetary('Unit Price',digits=dp.get_precision('Price'),related='agreement_planned_id.price_unit')
    total = fields.Monetary(string='Total Cost', store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=False,
        default=lambda self: self.env.user.company_id.currency_id.id)
    type = fields.Selection([('view' , 'View') , ('material' , 'Material') , ('internal','Internal Workers') , ('other' , 'Other')] ,required=False)

    state = fields.Selection([('draft','Draft'),('wating_approve','Wating Approve'),('approved','Approved'),('budget_generating','Budget generating'),
                              ('implementing','Implementing'),('refuse','Refused'), ('closed','Closed')] ,related="agreement_id.state")

    agreement_type = fields.Selection([('civil','Civil'),('emergency','Emergency'),('construction','Construction')] ,related="agreement_id.agreement_type")
    #set_to_child = fields.Boolean()
    previous_purchased = fields.Float("Previous Purchase QTY",related='agreement_planned_id.previous_purchased',readonly=1)
    purchase_cost = fields.Float('Previous Purchase Cost',related='agreement_planned_id.purchase_cost',readonly=1)
    requested_qty = fields.Float('Purchase Requested QTY',related='agreement_planned_id.requested_qty',readonly=1)
    residual_to_purchase = fields.Integer('Residual QTY')
    start_date = fields.Date('Start Date' )
    end_date = fields.Date('End Date')
    overdraw = fields.Boolean('Overdraw' , default=False)
    #child_ids = fields.One2many('project.agreement.planned',inverse_name="parent_id",string="Child Items")
    #revenue = fields.Float('Revenue %' , required=1)
    #revenue_amount = fields.Monetary(compute='_compute_revenue', string='Revenue Amount', store=True)
    #analytic_account_id = fields.Many2one('account.analytic.account' , 'Cost Center', readonly=True,)
    #account_id = fields.Many2one('account.account', string='Account')
    #is_cost_center = fields.Boolean('Is Cost Center')
    #delivered_quantity = fields.Monetary( string='Delivered Qty', store=True)
    #residual_quantity = fields.Monetary(string='Residual Qty', store=True)
    #progress = fields.Float('Progress %')
    #responsible_id = fields.Many2one('res.partner', string='Responsible')
    #parent_id = fields.Many2one('project.agreement.planned', string='Parent' ,  ondelete='cascade',)
    vat_percentage = fields.Float(default=5,string="Vat Percentage %")
    vat_amount = fields.Float(readonly=1,compute="_compute_vat")
    total_after_vat = fields.Float(readonly=1,compute="_compute_vat")
    total = fields.Float(readonly=1,compute="_compute_line_total")

    @api.depends('required_quantity','price_unit')
    def _compute_line_total(self):
        for rec in self:
            if rec.required_quantity and rec.price_unit:
                amount = rec.required_quantity * rec.price_unit
               
                rec.update({'total':amount})
            else:
                rec.update({'total':0})

    @api.depends('vat_percentage','required_quantity','price_unit')
    def _compute_vat(self):
        for rec in self:
            if rec.required_quantity and rec.price_unit:
                amount = rec.required_quantity * rec.price_unit
                vat = amount * (rec.vat_percentage/100)
                rec.update({'vat_amount':vat,'total_after_vat':amount + vat})
            else:
                rec.update({'vat_amount':0,'total_after_vat':0})


    @api.onchange('required_quantity','previous_purchased','requested_qty')
    def onchange_residual_to_purchase(self):
        for rec in self:
            if rec.agreement_type != 'emergency':
                rec.residual_to_purchase = rec.required_quantity - rec.requested_qty

            else:
                rec.residual_to_purchase = rec.required_quantity


    @api.onchange('agreement_planned_id','residual_to_purchase')
    def onchange_agreement_planned_id(self):
        for rec in self:
            rec.product_id = rec.agreement_planned_id.product_id
            rec.name = rec.agreement_planned_id.name
            if rec.agreement_planned_id and rec.agreement_type != 'emergency':
                if ((rec.required_quantity - rec.requested_qty) <= 0 or rec.residual_to_purchase > (rec.required_quantity - rec.requested_qty)) and rec.agreement_planned_id.allow_quantity_overdraw != True:
                    rec.overdraw = True
                else:
                    rec.overdraw = False
    @api.onchange('start_date', 'end_date','agreement_planned_id')
    def onchange_date(self):

        if self.agreement_type == 'emergency':
            start_date = datetime.strptime(self.start_date, tools.DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.strptime(self.end_date, tools.DEFAULT_SERVER_DATE_FORMAT)

            delta = end_date - start_date

            for line in self:
                line.required_quantity = delta.days
                line.residual_to_purchase = line.required_quantity

