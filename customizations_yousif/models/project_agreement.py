# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectAgreement(models.Model):
    _inherit = 'project.agreement'

    def _get_default_code(self):
        return self.env['ir.sequence'].next_by_code('project.agreement.code.sequence') or ''

    code = fields.Char('Code', states={'approved': [('readonly', True)]},
                       default=_get_default_code,
                       required=1)
    name = fields.Char('Project', required=True, states={'approved': [('readonly', True)]})

    @api.constrains('code')
    def _check_if_code_is_unique(self):
        pg = self.search([('code', '=', self.code)])
        if len(pg) > 1:
            raise ValidationError(_('Another Project Agreement Has The Same Code!!'))
