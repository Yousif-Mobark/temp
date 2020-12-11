# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta


class ProjectEmergencyConfirmation(models.Model):
    _name = 'project.emergency.confirmation'

    name = fields.Char(readonly=1,default=_("New"),copy=False)
    agreement_id = fields.Many2one('project.agreement', domain=[('agreement_type','=','emergency')])
    project_id = fields.Many2one(related='agreement_id.project_id')
    station_id = fields.Many2one('station.station')
    area_id = fields.Many2one('area.area')
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'), ('done', 'Done'), ('close', 'Close')],
                             default="draft", string="Status")
    invoice_ids = fields.One2many('account.invoice', 'project_emg_id')
    invoice_count = fields.Integer(string="Invoice Number", compute="compute_invoice_count")
    amount = fields.Float(compute="_compute_totals")
    invoiced_amount = fields.Float(compute="_compute_totals")
    residual_amount = fields.Float(compute="_compute_totals")
    project_emg_conf_line_ids = fields.One2many('project.emergency.confirmation.line', 'project_emg_id')
    invoice_limit = fields.Float(default=20)
    attachment_id = fields.Many2many('ir.attachment', 'emergency_attachment_rel', 'emergency_ref', 'attach_ref1',
                                     string="Attachment",
                                     help='You can attach File', required=True)
    
    @api.constrains('attachment_id','project_emg_conf_line_ids')
    def _check_con_line_attachments(self):
        for rec in self:
            if rec.attachment_id and not rec.project_emg_conf_line_ids:
                raise ValidationError("Sorry, You added Attachment so you Must Add Confirmation Line with it")
            if rec.project_emg_conf_line_ids and not rec.attachment_id:
                raise ValidationError("Sorry, You Must Add Attachment")

    #@api.constrains('attachment_id')
    def _check_attachments(self):
        for rec in self:
            if not rec.attachment_id:
                raise ValidationError("Sorry, You Must Add Document To Save")
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('project.emergency.confirmation') or _('New')
        result = super(ProjectEmergencyConfirmation, self).create(vals)
        return result

    @api.one
    def action_progress(self):
        self.write({'state': 'in_progress'})

    @api.one
    def action_done(self):
        self._check_attachments()
        if not self.project_emg_conf_line_ids:
            raise ValidationError(_("Please Add Confirmation Line first"))
        if self.residual_amount < 0.0:
            raise ValidationError(_("The remaining amount is unbalanced"))
        self.write({'state': 'done'})

    @api.one
    def action_close(self):
        self.write({'state': 'close'})

    @api.one
    def action_draft(self):
        self.write({'state': 'draft'})

    def action_open_invoice(self):
        #view_id = self.env['ir.model.data'].get_object_reference('account', 'project_emergency.invoice_emerg_tree')[1]
            
        return {
            'name': _('Emergency ' + self.agreement_id.name + ' Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'view_ids':[(5, 0, 0),
                (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('project_emergency.invoice_emerg_tree')}),
                (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('project_emergency.invoice_supplier_emerg_form')})],
            'domain': [('project_emg_id', '=', self.id)],
        }

    def compute_invoice_count(self):
        count = 0
        for rec in self:
            for line in rec.invoice_ids:
                count += 1
            rec.invoice_count = count

    @api.depends('invoice_ids')
    def _compute_totals(self):
        for rec in self:
            amount = sum(rec.project_emg_conf_line_ids.mapped('total_price')) if rec.project_emg_conf_line_ids else rec.station_id.residual_amount
            invoiced_amount = sum(rec.invoice_ids.mapped('amount_total'))
            residual_amount = 0
            for invoice in rec.invoice_ids:
                residual_amount += sum(invoice.payment_ids.mapped('amount'))
            rec.update({
                'invoiced_amount': invoiced_amount,
                'residual_amount': amount - invoiced_amount,
                'amount': amount
            }
            )


class ProjectEmergencyConfirmationLine(models.Model):
    _name = 'project.emergency.confirmation.line'
    _rec_name = 'project_emg_id'

    project_emg_id = fields.Many2one('project.emergency.confirmation')
    agreement_id = fields.Many2one('project.agreement', related="project_emg_id.agreement_id", store=True)
    project_id = fields.Many2one(related='project_emg_id.project_id', store=True)
    station_id = fields.Many2one('station.station', related='project_emg_id.station_id', store=True)
    area_id = fields.Many2one('area.area', related='project_emg_id.area_id', store=True)
    agreement_line_id = fields.Many2one('project.agreement.planned', )
    start_date = fields.Date(required=1)
    end_date = fields.Date(required=1)
    product_uom = fields.Many2one('product.uom', 'Unit of Measuer'  # ,related='agreement_line_id.product_uom',
                                  , domain=[('proj_emg_unit', '!=', False)],
                                  default=lambda self: self.env.ref('product.product_uom_day').id)
    quantity = fields.Float("Period Value",compute="_compute_quantity",inverse='_inverse_quantity_value')
    q_sum = fields.Float(string="Quantity")
    price_unit = fields.Monetary(related='agreement_line_id.price_unit', readonly=1)
    currency_id = fields.Many2one('res.currency')
    total_price = fields.Float(compute="_compute_total")
    type = fields.Selection([
        ('view' , 'View') ,
        ('material' , 'Material') ,
        ('internal','Internal Workers') ,
        ('other' , 'Other')
        ] ,related='agreement_line_id.type',required=True)
     

    @api.depends('product_uom', 'start_date', 'end_date', 'agreement_line_id')
    def _compute_total(self):
        for rec in self:
            rec.update({
                'total_price': (rec.quantity * rec.price_unit) * rec.q_sum,
            })

    def workdays(self,d, end, excluded=(5,)):
        """
        excluded #5 is Friday , 6 Sturday and 7 Sunday and so on
        """
        days = []
        while d <= end:
            if d.isoweekday() in excluded:
                days.append(d)
            d += timedelta(days=1)
        print("DDDDD",days)
        return days

    @api.depends('start_date', 'end_date', 'product_uom')
    def _compute_quantity(self):
        resource_attendance_obj =  self.env['resource.calendar.attendance']#calendar_id
        for rec in self:
            if rec.product_uom and rec.start_date and rec.end_date:
                
                d1 = datetime.strptime(rec.start_date, "%Y-%m-%d")
                d2 = datetime.strptime(rec.end_date, "%Y-%m-%d")
                if rec.project_id:
                    project_calendar = rec.project_id.resource_calendar_id#.attendance_ids
                    resource_attendance = resource_attendance_obj.read_group([('calendar_id','=',project_calendar.id)],['dayofweek'],['dayofweek'])
                    days = [int(line['dayofweek'])+1 for line in resource_attendance]
                    diff = len(self.workdays(d1,d2,days))
                else:
                    disff = len(self.workdays(d1,d2))
                
                if rec.product_uom.proj_emg_unit == 'day':
                    rec.quantity = diff
                elif rec.product_uom.proj_emg_unit == 'week':
                    rec.quantity = diff / 6
                elif rec.product_uom.proj_emg_unit == 'month':
                    rec.quantity = diff / 30

    def _inverse_quantity_value(self):
        for rec in self:
            if rec.product_uom.proj_emg_unit == 'day':
                diff = rec.quantity
            elif rec.product_uom.proj_emg_unit == 'week':
                diff = rec.quantity * 6
            elif rec.product_uom.proj_emg_unit == 'month':
                diff = rec.quantity * 30
            rec.end_date = fields.Date.from_string(rec.start_date) + relativedelta(days=diff)
            print("Revvvvvvvvvvvv",rec.end_date)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    project_emg_id = fields.Many2one('project.emergency.confirmation','Confirmation')
    station_id = fields.Many2one('station.station',related='project_emg_id.station_id',store=True)
    area_id = fields.Many2one('area.area',related='project_emg_id.area_id',store=True)


class ProductUOM(models.Model):
    _inherit = 'product.uom'

    proj_emg_unit = fields.Selection([('day', 'Day'), ('week', 'Week'), ('month', 'Month')])


class stationStation(models.Model):
    _inherit = 'station.station'

    amount = fields.Float(string="Amount")
    invoiced_amount = fields.Float(compute="_compute_totals")
    residual_amount = fields.Float(compute="_compute_totals")
    emergency_count = fields.Integer(string="Invoice Number", compute="compute_emergency_count")

    def compute_emergency_count(self):
        emergency_ids = self.env['project.emergency.confirmation'].search([('station_id', '=', self.id)])
        self.emergency_count = len(emergency_ids)

    def _compute_totals(self):
        invoiced_amount = 0.0
        for rec in self:
            emergency_ids = self.env['project.emergency.confirmation'].search([('station_id', '=', self.id)])
            for emergency in emergency_ids:
                if not emergency.project_emg_conf_line_ids:
                    invoiced_amount += emergency.invoiced_amount
            residual_amount = 0
            rec.update({
                'invoiced_amount': invoiced_amount,
                'residual_amount': abs(invoiced_amount - rec.amount) if invoiced_amount > 0.0 else rec.amount,
            }
            )

    def action_open_emergency(self):
        return {
            'name': _('Emergency Project For' + self.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.emergency.confirmation',
            'type': 'ir.actions.act_window',
            'domain': [('station_id', '=', self.id)],
        }