# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class projectAgreementTender(models.Model):
    _inherit = 'project.agreement'

    project_agreement_consumed_ids = fields.One2many('purchase.order.line', 'agreement_id')

    @api.multi
    def open_agreement_tendar_wizard(self):
        action_name = self.env.context.get('action_name', False)
        request_type = self.env.context.get('type', False)
        if not action_name:
            return False

        ir_model_obj = self.env['ir.model.data']
        model, action_id = ir_model_obj.get_object_reference(
            'project_agreement_purchase', action_name)
        [action] = self.env[model].browse(action_id).read()
        tender_lines = []
        if request_type == 'all':
            for line in self.all_project_agreement_planned_line_ids.filtered(lambda r: r.type == 'material'):
                tender_lines.append((0, 6, {
                    'agreement_type': self.agreement_type,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'agreement_planned_id':line.id,
                    'name':line.name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'required_quantity': line.required_quantity,
                    'previous_purchased': line.previous_purchased,
                    'purchase_cost' : line.purchase_cost ,
                    'requested_qty' : line.requested_qty ,
                    'price_unit': line.price_unit,
                    'residual_to_purchase':line.required_quantity - (line.previous_purchased+line.requested_qty) if line.agreement_type == 'civil' else line.required_quantity ,

                }))
                #print(">>>>>>>>>>>>",line.required_quantity,"-",line.requested_qty,"-",line.previous_purchased,"-",str(tender_lines))
        action['context'] = {'default_agreement_id': self.id, 'default_agreement_type': self.agreement_type,'default_wizard_type':request_type ,
        

                             #'default_project_agreement_planned_line_ids':self.project_agreement_planned_line_ids.filtered(lambda r:r.type=='material').ids,
                             'default_project_agreement_tendar_line_ids':tender_lines,
                             
                             'default_start_date': self.start_date, 'default_end_date': self.end_date}
        # if ctx.get('use_domain', False):
        #     action['domain'] = ['|', ('journal_id', '=', self.id), ('journal_id', '=', False)]
        #     action['name'] += ' for journal ' + self.name
        return action


class project_agreement_planned(models.Model):
    _inherit = 'project.agreement.planned'

    previous_purchased = fields.Float('Previous Purchase QTY',compute="_compute_purchase_values")
    purchase_cost = fields.Float('Purchase Cost',compute="_compute_purchase_values")
    purchase_residual = fields.Float('Purchase Residual QTY',compute="_compute_purchase_values")
    requested_qty = fields.Float('Purchase Requested QTY',default=0.0,readonly=1)#Update By Wizard
    allow_quantity_overdraw = fields.Boolean('Allow Overdraw' , default=False)

    @api.one
    @api.depends('product_id')
    def _compute_purchase_values(self):
        purchase_line_obj = self.env['purchase.order.line']
        for rec in self:
            lines = purchase_line_obj.search(
                [('product_id', '=', rec.product_id.id)])
            qty_received = sum(lines.mapped('qty_received'))
            price_subtotal = sum(lines.mapped('price_subtotal'))
            rec.update({
                'previous_purchased': qty_received,
                'purchase_cost': price_subtotal,
                'purchase_residual':  rec.required_quantity - qty_received,
            })


    def agreement_product_product_action_all(self):

        view_id_form = self.env['ir.ui.view'].search(
             [('name','=','product.template.product.form')])
        view_id_kanban = self.env['ir.ui.view'].search(
            [('name', '=', 'Product.template.product.kanban')])
        view_id_tree = self.env['ir.ui.view'].search(
            [('name', '=', 'product.template.product.tree')])
        line_ids=self.search([('id','child_of',self.id)]).mapped('product_id')
        line_tmp=line_ids.mapped('product_tmpl_id').ids
        return {
            'name': _('Items'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'product.template',

            'views': [(view_id_kanban[0].id, 'kanban'),(view_id_tree[0].id, 'tree'),(view_id_form[0].id,'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', line_tmp)],
            'context': {'search_default_group_by_state': 1, 'default_board_id': self.id},
        }

class purchaseOrder(models.Model):
    _inherit = 'purchase.order'

    agreement_id = fields.Many2one('project.agreement' , related='requisition_id.agreement_id',store=True)
    project_id = fields.Many2one('project.project', 'Project', related='agreement_id.project_id', store=True)
    start_date = fields.Date('Start Date' , related='requisition_id.start_date',store=True)
    end_date = fields.Date('End Date' , related='requisition_id.end_date',store=True)
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('project_confirm', 'Project Manager'),('assistance_approve', 'Assistance Approve'),('executive_director','Executive Director'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    
    total_purchase_qty = fields.Integer(readonly=1,compute="_compute_purchase_qty")
    total_purchase_qty_received = fields.Integer(readonly=1,compute="_compute_purchase_qty")
   
    @api.multi
    @api.depends('order_line')
    def _compute_purchase_qty(self):
        for rec in self:
            qty_purchased = sum(rec.order_line.mapped('product_qty'))
            qty_received = sum(rec.order_line.mapped('qty_received'))
            rec.update({
                'total_purchase_qty': qty_purchased,
                'total_purchase_qty_received': qty_received,
                
            })
            
    @api.multi
    def button_confirm(self):
        for order in self:
            order.write({'state': 'purchase','date_approve': fields.Date.context_today(self)})
        return True

    @api.multi
    def send_to_project(self):
        for order in self:
            order.write({'state': 'project_confirm'})
        return True

    @api.multi
    def button_project_confirm(self):
        for order in self:
            order.write({'state': 'assistance_approve'})
        return True

    @api.multi
    def button_assistance_confirm(self):
        for order in self:
            order.write({'state': 'executive_director'})
        return True

    @api.multi
    def button_approve(self, force=False):
        self._create_picking()
        self.write({'state': 'done'})
        return {}

class purchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    agreement_id = fields.Many2one('project.agreement', related="order_id.agreement_id" , store=True)
    project_id = fields.Many2one('project.project', 'Project', related='agreement_id.project_id', store=True)
    agreement_planned_id = fields.Many2one('project.agreement.planned')
    start_date = fields.Date('Start Date' ,related="order_id.start_date" , store=True)
    end_date = fields.Date('End Date' ,related="order_id.end_date" , store=True)


class purchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    agreement_id = fields.Many2one('project.agreement','Agreement')
    project_id = fields.Many2one('project.project' , 'Project' ,related='agreement_id.project_id' , store=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    attach_no = fields.Integer(compute="_get_attachment_no")
    
    @api.multi
    def _get_attachment_no(self):
        attachment_obj = self.env['ir.attachment']
        for rec in self:
            rec.update({
                'attach_no' : len(attachment_obj.search([('res_id','=',rec.id),('res_model','=','purchase.requisition')]))
            })




class purchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    agreement_id = fields.Many2one('project.agreement','Apgreement' , related="requisition_id.agreement_id" , store=True)
    project_id = fields.Many2one('project.project', 'Project' , related='agreement_id.project_id' , store=True)
    agreement_planned_id = fields.Many2one('project.agreement.planned')
    start_date = fields.Date('Start Date',related="requisition_id.start_date" , store=True)
    end_date = fields.Date('End Date',related="requisition_id.end_date" ,store=True)
