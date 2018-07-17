# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class DonateOrder(models.Model):
    _name = 'donate.order'


    donate_list_id = fields.Many2one(comodel_name='donate.single', ondelete='cascade', index = True)
    con_phone = fields.Char(string='連絡電話')
    p_type = fields.Char(string='人員種類')
    donate = fields.Integer(string='捐款金額')
    donate_total = fields.Integer(string='捐款總額')
    donate_type = fields.Selection(selection=[(01, '造橋'), (02, '補路'), (03, '施棺'), (04, '伙食費'), (05, '貧困扶助'),(06, '一般捐款'), (99, '其他工程')],
                                   string='捐款種類' , index =True)
    payment_method = fields.Selection(selection=[(1, '現金'), (2, '郵政劃撥'), (3, '信用卡扣款'), (4, '銀行轉帳'), (5, '支票')], string='繳費方式',
                                      required=True)
    state = fields.Selection([(1, '已產生'), (2, '已作廢')],
                             string='狀態', default=1, index=True)
    active = fields.Boolean(default=True)

    donate_member = fields.Many2one(comodel_name='openacademy.gofor', string='捐款人姓名', index=True)
    paid_id = fields.Char(string='收費編號')
    donate_id = fields.Char(string='收據編號')
    donate_date = fields.Date(string='捐款日期', index=True)
    self_id = fields.Char(string='身分證字號')
    clerk = fields.Char(string='收費員編號')
    temp_key_in_user = fields.Char(string='輸入人員')
    db_key_in_user = fields.Char(string='資料庫紀錄輸入人員')
    report_year = fields.Boolean(string='收據年度開立')
    db_chang_date = fields.Date(string='異動日期')
    receipt_send = fields.Boolean(string='收據寄送')
    report_send = fields.Boolean(string='報表寄送')
    year_receipt_send = fields.Boolean(string='年收據寄送')
    bridge = fields.Boolean(string='造橋')
    road = fields.Boolean(string='補路')
    coffin = fields.Boolean(string='施棺')
    poor_help = fields.Boolean(string='貧困扶助')
    others = fields.Boolean(string='一般捐款')
    bridge_money = fields.Integer(string='$')
    road_money = fields.Integer(string='$')
    coffin_money = fields.Integer(string='$')
    poor_help_money = fields.Integer(string='$')
    others_money = fields.Integer(string='$')
    cash = fields.Boolean(string='現金')
    mail = fields.Boolean(string='郵政劃撥')
    credit_card = fields.Boolean(string='信用卡扣款')
    bank = fields.Boolean(string='銀行轉帳')

    address = fields.Char(string='住址')
    city = fields.Char(string='市區')

    use_amount = fields.Boolean(string='施棺捐款是否已支用', default=False)
    available_balance = fields.Integer(string='可用餘額')
    used_money = fields.Integer(string='已用金額')
    donate_book_code = fields.Char(string='簿冊編號')
    ps = fields.Char(string='備註')
    bridge_money = fields.Integer(string='橋')
    road_money = fields.Integer(string='路')
    coffin_money = fields.Integer(string='棺')
    poor_help_money = fields.Integer(string='窮')
    noassign_money = fields.Integer(string='一般')
