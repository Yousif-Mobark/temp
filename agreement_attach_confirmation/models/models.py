# -*- coding: utf-8 -*-

from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError

class AgreementAttachConfirmation(models.Model):
    _name = 'agreement.attach.confirmation'

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    type = fields.Selection([('agreement','Agreement') , ('item' , 'Item')] , default='item' ,required=True)
    attach_id = fields.Binary( "Files", attachment=True,required=True)
    date = fields.Date('Date' , default=fields.Datetime.now ,required=True)
    #end_date = fields.Date('End Date' , required=True)
    agreement_id = fields.Many2one('project.agreement' ,'Agreement' , required=True)
    agreement_line_ids = fields.One2many('project.agreement.planned','confirmation_id', 'Items')
    project_id = fields.Many2one('project.project','Project' , readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)] ,readonly=True)
    state = fields.Selection([('draft','Draft') , ('approved','Approved')] , default='draft')

    @api.model
    def create(self, vals):
        if vals.get('agreement_id', False):
            vals['project_id'] = self.agreement_id.search([('id' ,'=',vals['agreement_id'])]).project_id.id
            vals['customer_id'] = self.agreement_id.search([('id' ,'=',vals['agreement_id'])]).customer_id.id
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('agreement.attach.confirmation') or '/'
        return super(AgreementAttachConfirmation, self).create(vals)

    def write(self, vals):
        if vals.get('agreement_id', False):
            vals['project_id'] = self.agreement_id.search([('id' ,'=',vals['agreement_id'])]).project_id.id
            vals['customer_id'] = self.agreement_id.search([('id' ,'=',vals['agreement_id'])]).customer_id.id
        return super(AgreementAttachConfirmation, self).write(vals)

    @api.multi
    def approved(self):
        if self.type == 'agreement':
            self.env['ir.attachment'].create({'res_model':'project.agreement' , 'res_id':self.agreement_id.id , 'datas':self.attach_id ,'name':self.name })
            for rec in self.agreement_id.all_project_agreement_planned_line_ids:
                self.env['ir.attachment'].create({'res_model': 'project.agreement.planned', 'res_id': rec.id, 'datas': self.attach_id,
                     'name': self.name})
                rec.confirmation_id = self.id
        elif self.type == 'item':
             for rec in self.agreement_line_ids:
                 self.env['ir.attachment'].create({'res_model': 'project.agreement.planned', 'res_id': rec.id, 'datas': self.attach_id,
                      'name': self.name})
             rec.confirmation_id = self.id
        self.write({'state': 'approved'})


    @api.onchange('agreement_id')
    def onchange_agreement_id(self):
        for rec in self:
            rec.project_id = rec.agreement_id.project_id
            rec.customer_id = rec.agreement_id.customer_id

class projectAgreement(models.Model):
        _inherit = 'project.agreement'

        confirmation_ids = fields.One2many('agreement.attach.confirmation','agreement_id')


class projectAgreementLine(models.Model):
        _inherit = 'project.agreement.planned'

        check_confirmaion = fields.Boolean('Check Confirmation' ,default=True)
        confirmation_id = fields.Many2one('agreement.attach.confirmation','Confirmation')
        attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments' , store=True)

        @api.multi
        @api.depends('confirmation_id')
        def _compute_attachment_number(self):
            attachment_data = self.env['ir.attachment'].read_group(
                [('res_model', '=', 'project.agreement.planned'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
            attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
            for rec in self:
                rec.attachment_number = attachment.get(rec.id, 0)


class projectAgreementTendarWizard(models.TransientModel):
    _inherit = 'project.agreement.tendar.wizard'

    def button_create_tendar(self):
        for line in self.project_agreement_tendar_line_ids:
            if line.agreement_planned_id.check_confirmaion:
                if line.agreement_planned_id.attachment_number == 0:
                    raise ValidationError(_('Please you must Add Confirmation For This Line %s') % (line.name))
        return super(projectAgreementTendarWizard, self).button_create_tendar()

