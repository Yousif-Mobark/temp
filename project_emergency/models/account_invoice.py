# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class accountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _is_user_proj_mng(self):
        for rec in self:
            print(">>>>>>>>>>>>>>>>>>>>>HERE 0")
            if rec.project_emg_id and rec.project_emg_id.project_id.user_id.id == self.env.user.id:
                print(">>>>>>>>>>>>>>>>>>>>>HERE 1")
                rec.is_user_proj_mng = True

    state = fields.Selection([
            ('draft','Draft'),
            ('sta_mng_approved','Station Manager Approved'),
            ('bil_mng_approved','Billing Manager Approved'),
            ('prj_mng_approved','Project Manager Approved'),
            ('emp_tra_approved','Employee Transfere Approved'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,)

    is_user_proj_mng = fields.Boolean(compute="_is_user_proj_mng")


    def station_manager_validate(self):
        self.state = 'sta_mng_approved'

    def station_manager_refuse(self):
        self.state = 'cancel'

    def billing_manager_validate(self):
        self.state = 'bil_mng_approved'
        
    def billing_manager_refuse(self):
        self.state = 'cancel'

    def project_manager_validate(self):
        self.state = 'prj_mng_approved'
        
    def project_manager_refuse(self):
        self.state = 'cancel'

    def action_invoice_open(self):
        self.state = 'draft'
        super(accountInvoice,self).action_invoice_open()

    def employee_transfere_refuse(self):
        self.state = 'cancel'
        


    