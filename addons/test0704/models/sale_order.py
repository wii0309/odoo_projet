# -*- coding:utf-8 -*-
from odoo import api, fields, models
import datetime

class Test0704saleorder(models.Model):
    _inherit = 'sale.order'
    gym_id=fields.Many2one(comodel_name='openacademy.course',string='銷售健身房')

    @api.multi
    def action_confirm(self):
        res = super(Test0704saleorder, self).action_confirm()
        for r in self.order_line:
            res = self.env['read.class'].create({
                'buyer': self.partner_id.id,
                'date_order':self.date_order,
                'relatep': self.id,
                'checkp': r.product_id.id,
                'account': r.product_uom_qty,
                'price': r.price_unit,
                'total':r.price_subtotal,
            })
        return res

class Test0704saleexercise(models.Model):
    _inherit = 'sale.order.line'
    exercise_id=fields.Many2one(comodel_name='openacademy.gofor',string='Gofor資料輸入')