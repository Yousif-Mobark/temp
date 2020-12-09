# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _name = 'account.analytic.account'
    _inherit = 'account.analytic.account'

    is_project = fields.Boolean("Is Project", track_visibility='onchange', translate=True, default=False)


class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = 'account.analytic.line'

    working_item_id = fields.Many2one('working.item', string='Working Item', track_visibility='onchange', translate=True)
    is_project = fields.Boolean(related="account_id.is_project", string="Is Project", translate=True, store=True)


class Project(models.Model):
    _name = "project.project"
    _inherit = "project.project"

    @api.multi
    def write(self, vals):
        # directly compute is_favorite to dodge allow write access right
        if 'is_favorite' in vals:
            vals.pop('is_favorite')
            self._fields['is_favorite'].determine_inverse(self)
        res = super(Project, self).write(vals) if vals else True
        if 'active' in vals:
            # archiving/unarchiving a project does it on its tasks, too
            self.with_context(active_test=False).mapped('tasks').write({'active': vals['active']})
            # archiving/unarchiving a project implies that we don't want to use the analytic account anymore
            self.with_context(active_test=False).mapped('analytic_account_id').write({'active': vals['active']})
        if vals.get('partner_id') or vals.get('privacy_visibility'):
            for project in self.filtered(lambda project: project.privacy_visibility == 'portal'):
                project.message_subscribe(project.partner_id.ids)
        
        self.mapped('analytic_account_id').write({'is_project': True})
        return res
