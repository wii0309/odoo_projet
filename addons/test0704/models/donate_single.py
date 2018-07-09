# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Donatesingle(models.Model):
    _name = 'donate.single'

    donate_member = fields.Many2one(comodel_name='openacademy.gofor', string='捐款者',
                                    required = True, index = True)
    state = fields.Selection([(1, '已產生'), (2, '已列印'), (3, '已作廢')],
                             string='狀態', default=1, index=True)
    donate_date = fields.Date('捐款日期', index=True, required=True)
    donate_total = fields.Integer(string='捐款總額', compute='compute_total', store=True)
    receipt_send = fields.Boolean(string='收據寄送')
    # work_id = fields.Many2one(comodel_name='openacademy.gofor', string='收費員', states={2: [('readonly', True)]},
    #                           required=True)
    payment_method = fields.Selection([(1, '現金'), (2, '郵政劃撥'), (3, '信用卡扣款'), (4, '銀行轉帳'), (5, '支票')], string='繳費方式',
                                      required=True)
    name = fields.Char(string='姓名', store=True)
    self_iden = fields.Char(string='身分證字號', store=True)
    cellphone = fields.Char(string='手機', store=True)
    con_phone = fields.Char(string='聯絡電話', store=True)
    zip_code = fields.Char(string='報表郵遞區號', store=True)
    con_addr = fields.Char(string='報表地址', store=True)
    zip = fields.Char(string='收據郵遞區號', store=True)
    rec_addr = fields.Char(string='收據地址', store=True)
    ps = fields.Text('備註')



