# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,tools
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class EmergencyInvoice(models.TransientModel):
    _name = 'project.emergency.invoice.wizard'
    
    @api.constrains('attach_files_ids')
    def check_have_attach_files(self):
        if len(self.attach_files_ids) == 0:
            raise ValidationError(_("Sorry , You Must Attach Files!!"))

    @api.model
    def default_emergency_id(self):
        """
        set a default value for emergency_id field
        :return:
        """
        if self._context.get('emergency_id', False):
            return self._context.get('emergency_id')

    @api.model
    def default_amount(self):
        """
        set a default value for emergency_id field
        :return:
        """
        if self._context.get('emergency_id', False):
            emergency_id = self.env['project.emergency.confirmation'].search([('id','=', self._context.get('emergency_id'))])
            return emergency_id.amount if emergency_id.residual_amount == 0.0 and emergency_id.invoiced_amount == 0.0 else emergency_id.residual_amount

    emergency_id = fields.Many2one('project.emergency.confirmation', string="Emergency", default=default_emergency_id)
    partner_id = fields.Many2one('res.partner', string="Vendor")
    amount = fields.Float(string="Invoice Amount", default=default_amount)
    date = fields.Date(required=True)
    push = fields.Integer()
    describe = fields.Text('Description',required=True)
    attach_files_ids = fields.Many2many('ir.attachment',string="Attachment Files"#,relation="attach_attachment"
    )

    def button_create_invoice(self):
        """
        Create Invoice based on agreement
        :return:
        """
        invoice_obj = self.env['account.invoice']
        lines = []
        if self.amount < 0:
            raise ValidationError(_("the Amount Cannot be less than zero"))
        elif self.amount == 0.0:
            raise ValidationError(_("Invoice Amount Cannot Be zero"))
        for rec in self.emergency_id:
            invoice_limit = rec.amount * rec.invoice_limit / 100
            if rec.residual_amount <= 0.0 or rec.residual_amount < self.amount:
                raise ValidationError(_("You don't have enough amount to complete the transaction"))
            elif rec.residual_amount - self.amount  < invoice_limit:
                raise ValidationError(_("You can't pay more than Invoice Limit %s percentage")%(rec.invoice_limit))
            elif rec.amount < self.amount:
                raise ValidationError(_("You don't have enough amount to complete the transaction"))

            if not self.env.user.company_id.emergency_journal_id.id or not self.env.user.company_id.emergency_account_exp_id\
                    or not self.env.user.company_id.emergency_journal_id.default_credit_account_id.id:
                raise ValidationError(_("Please Set Expense Journal in Configuration First"))
            lines = [(0, 6, {
                'name': self.describe,
                'account_id': self.env.user.company_id.emergency_account_exp_id.id,
                'quantity': 1,
                'price_unit': self.amount,
            })]
            myinvoice = invoice_obj.create({
                "partner_id": self.partner_id.id,
                'project_emg_id' : self.emergency_id.id,
                "type": 'in_invoice',
                'station_id' : self.emergency_id.station_id.id,
                'area_id' : self.emergency_id.area_id.id,
                "date_invoice" : self.date,
                "comment" : self.describe,
                "journal_id": self.env.user.company_id.emergency_journal_id.id,
                "invoice_line_ids": lines,
            })
            for line in self.attach_files_ids:
                line.res_id = myinvoice.id
                line.res_model = 'account.invoice'
            rec.write({'invoice_ids': [(4, myinvoice.id)]})


