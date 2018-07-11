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
    donate_total = fields.Integer(string='捐款總額')
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
    # bridge_money = fields.Integer(string='$')
    # road_money = fields.Integer(string='$')
    # coffin_money = fields.Integer(string='$')
    # poor_help_money = fields.Integer(string='$')
    # noassign_money = fields.Integer(string='$')
    family_check =fields.One2many(comodel_name='donate.family.line', inverse_name='parent_id', string='捐款人名冊')

    donate_list = fields.One2many(comodel_name='donate.order', inverse_name='donate_list_id', string='捐款明細',
                                  states={2: [('readonly', True)]})

    current_donate_people = fields.Integer('捐款人數小計')

    ps = fields.Text('備註')

    history_donate_flag = fields.Boolean(string='是否上次捐款')
    #    history_payment_method = fields.Boolean('是否上次捐款方式')
    report_price_big = fields.Char(string='報表用大寫金額')
    report_donate = fields.Char(string='報表用捐款日期')
    sreceipt_number = fields.Integer(string='收據筆數', compute='compute_total', store=True)
    print_count = fields.Integer(string='列印筆數', store=True)
    print_date = fields.Date('列印日期')
    donate_family_list = fields.Char('眷屬列表', compute='compute_family_list')
    print_all_donor_list = fields.Boolean(string='列印願意捐助的眷屬')
    donate_list_id = fields.Many2one(comodel_name='donate.single', ondelete='cascade', index=True)

    @api.onchange('donate_member')
    def show_family(self):
        r = []
        family = None

        for line in self.donate_member.store_history.history_data: #捐款者若為眷屬，要先找到戶長，在搜尋該戶長下所登記的所有人
            r.append([0, 0, {
                'donate_member': line.id
            }])
        self.update({
            'family_check': r,
        })




    def add_to_list(self):
        for r in self.donate_member.history_data:
            res=self.env['donate.order'].create({
                'donate_member':r.id,
                'donate':self.donate_total,
                'con_phone':self.con_phone
            })


class DonateSingleLine(models.Model): #先產出一個資料表供當次捐款明細的編輯，才不會更改到原始會員資料
    _name = 'donate.family.line'

    parent_id = fields.Many2one(comodel_name='donate.single', index=True)
    donate_member = fields.Many2one(comodel_name='openacademy.gofor', string='捐款人', index=True)
    is_donate = fields.Boolean(string='是否捐助', related='donate_member.is_donate')
    is_merge = fields.Boolean(string='是否合併收據', related='donate_member.is_merge')

