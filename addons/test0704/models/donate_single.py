# -*- coding: utf-8 -*-
from docutils.parsers.rst.directives import images
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Donatesingle(models.Model):
    _name = 'donate.single'

    donate_member = fields.Many2one(comodel_name='openacademy.gofor', string='捐款者',
                                    required = True, index = True)
    state = fields.Selection(selection=[('a', '已產生'), ('b', '已列印'), ('c', '已作廢')],
                             string='狀態', default='a', index=True)
    donate_date = fields.Date('捐款日期', index=True, required=True)
    donate_total = fields.Integer(string='捐款總額' , compute='calculate', store=True)
    receipt_send = fields.Boolean(string='收據寄送')
    payment_method = fields.Selection([(1, '現金'), (2, '郵政劃撥'), (3, '信用卡扣款'), (4, '銀行轉帳'), (5, '支票')], string='繳費方式',
                                      required=True)
    name = fields.Char(string='姓名',related='donate_member.name', readonly=True)
    self_iden = fields.Char(string='身分證字號')
    cellphone = fields.Char(string='手機' )
    con_phone = fields.Char(string='聯絡電話',related='donate_member.con_phone',readonly=True)
    zip_code = fields.Char(string='報表郵遞區號' ,help="bao biao yo di qu hao")
    con_addr = fields.Char(string='報表地址')
    zip = fields.Char(string='收據郵遞區號' ,related='donate_member.zip',readonly=True)
    rec_addr = fields.Char(string='收據地址',related='donate_member.rec_addr',readonly=True)
    bridge_money = fields.Integer(string='$')
    road_money = fields.Integer(string='$' )
    coffin_money = fields.Integer(string='$')
    poor_help_money = fields.Integer(string='$')
    noassign_money = fields.Integer(string='$')
    family_check =fields.One2many(comodel_name='donate.family.line', inverse_name='parent_id', string='捐款人名冊')

    donate_list = fields.One2many(comodel_name='donate.order', inverse_name='donate_list_id', string='捐款明細',
                                  states={2: [('readonly', True)]})
    ps = fields.Text('備註' ,compute='compute_des',store=True)

    history_donate_flag = fields.Boolean(string='是否上次捐款')
    # history_payment_method = fields.Boolean('是否上次捐款方式')
    report_price_big = fields.Char(string='報表用大寫金額')
    report_donate = fields.Char(string='報表用捐款日期')
    sreceipt_number = fields.Integer(string='收據筆數', compute='compute_total', store=True)
    print_count = fields.Integer(string='列印筆數', store=True)
    print_date = fields.Date('列印日期')
    donate_family_list = fields.Char('眷屬列表', compute='compute_family_list')
    print_all_donor_list = fields.Boolean(string='列印願意捐助的眷屬')
    donate_list_id = fields.Many2one(comodel_name='donate.single', ondelete='cascade', index=True)
    donate_type = fields.Selection(selection=[(01, '造橋'), (02, '補路'), (03, '施棺'), (04, '伙食費'), (05, '貧困扶助'), (06, '一般捐款'), (99, '其他工程')],
        string='捐款種類', index=True)
    current_donate_project = fields.Integer('捐款項目小計')
    current_donate_total = fields.Integer('捐款總額小計')
    current_donate_people = fields.Integer('捐款人數小計')

    show_current_donate_project =fields.Integer('本次捐款項目共計',related='current_donate_project',readonly=True)
    show_current_donate_total = fields.Integer('本次捐款總額共計',related='current_donate_total',readonly=True)

    image =fields.Binary("Photo", attachment=True,
                                  help="This field holds the image used as photo for the test, limited to 1024x1024px.")

    w_id = fields.Char('舊團員編號', related='donate_member.w_id')
    new_coding = fields.Char('新捐款者編號', related='donate_member.new_coding')
    donate_id = fields.Char(string='收據編號')
    key_in_user = fields.Many2one(comodel_name='res.users', string='輸入人員')
    work_id = fields.Many2one(comodel_name='res.partner', string='收費員')
    year_fee = fields.Boolean(string='年繳')
    rec_send = fields.Boolean(string='收據寄送', default=True)
    # @api.model
    # def create(self, vals):
    #     tools.image_resize_images(vals)
    #     return super(Donatesingle, self).create(vals)

    def button_to_cnacel_donate(self):
        single_data = self.env['wizard.abandon.single'].create({
            'donate_single_code': self.id
        })
        action = self.env.ref('test0704.action_wizard_abandon_single').read()[0]
        action['res_id'] = single_data.id
        return action

    @api.onchange('family_check')
    def current_people(self):
        self.current_donate_people = 0
        self.current_donate_total = 0
        self.current_donate_project = 0
        for line in self.family_check:
            if line.is_donate is True:
                self.current_donate_people += 1
                if line.bridge_money != 0:
                    self.current_donate_project += 1
                    self.current_donate_total += line.bridge_money
                if line.road_money != 0:
                    self.current_donate_project += 1
                    self.current_donate_total += line.road_money
                if line.coffin_money != 0:
                    self.current_donate_project += 1
                    self.current_donate_total += line.coffin_money
                if line.poor_help_money != 0:
                    self.current_donate_project += 1
                    self.current_donate_total += line.poor_help_money
                if line.noassign_money != 0:
                    self.current_donate_project += 1
                    self.current_donate_total += line.noassign_money
            elif line.is_donate is False:
                line.bridge_money = 0
                line.road_money = 0
                line.coffin_money = 0
                line.poor_help_money = 0
                line.noassign_money = 0

    @api.onchange('bridge_money', 'road_money', 'coffin_money', 'poor_help_money', 'noassign_money')
    def add_to_family(self):
        self.current_donate_total = 0
        if self.family_check:
            for line in self.family_check.filtered(lambda x: x.is_donate == True):
                if self.bridge_money != 0:
                    line.bridge_money = self.bridge_money
                elif self.bridge_money == 0:
                    if line.bridge_money != 0:
                        line.bridge_money = self.bridge_money
                if self.road_money != 0:
                    line.road_money = self.road_money
                elif self.road_money == 0:
                    if line.road_money != 0:
                        line.road_money = self.road_money
                if self.coffin_money != 0:
                    line.coffin_money = self.coffin_money
                elif self.coffin_money == 0:
                    if line.coffin_money != 0:
                        line.coffin_money = self.coffin_money
                if self.poor_help_money != 0:
                    line.poor_help_money = self.poor_help_money
                elif self.poor_help_money == 0:
                    if line.poor_help_money != 0:
                        line.poor_help_money = self.poor_help_money
                if self.noassign_money != 0:
                    line.noassign_money = self.noassign_money
                elif self.noassign_money == 0:
                    if line.noassign_money != 0:
                        line.noassign_money = self.noassign_money

        for line in self.family_check:
            if line.is_donate is True:
                if line.bridge_money != 0:
                    self.bridge = True
                if line.road_money != 0:
                    self.road = True
                if line.coffin_money != 0:
                    self.coffin = True
                if line.poor_help_money != 0:
                    self.poor_help = True
                if line.noassign_money != 0:
                    self.noassign = True
                self.current_donate_total += line.bridge_money
                self.current_donate_total += line.road_money
                self.current_donate_total += line.coffin_money
                self.current_donate_total += line.poor_help_money
                self.current_donate_total += line.noassign_money

    @api.onchange('donate_member') #################重要
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

    def add_to_list_create(self, record):
        if record.family_check:
            for line in record.family_check.filtered(lambda x: x.is_donate == True):
                if record.print_all_donor_list:
                    if line.bridge_money == 0 and line.road_money == 0 and line.coffin_money == 0 and line.poor_help_money == 0 and line.noassign_money == 0:
                        record.save_donate_list(6, line.donate_member, line.noassign_money)
                    if line.bridge_money != 0:
                        record.save_donate_list(1, line.donate_member, line.bridge_money)
                    if line.road_money != 0:
                        record.save_donate_list(2, line.donate_member, line.road_money)
                    if line.coffin_money != 0:
                        record.save_donate_list(3, line.donate_member, line.coffin_money)
                    if line.poor_help_money != 0:
                        record.save_donate_list(5, line.donate_member, line.poor_help_money)
                    if line.noassign_money != 0:
                        record.save_donate_list(6, line.donate_member, line.noassign_money)
                else:
                    if line.bridge_money != 0:
                        record.save_donate_list(1, line.donate_member, line.bridge_money)
                    if line.road_money != 0:
                        record.save_donate_list(2, line.donate_member, line.road_money)
                    if line.coffin_money != 0:
                        record.save_donate_list(3, line.donate_member, line.coffin_money)
                    if line.poor_help_money != 0:
                        record.save_donate_list(5, line.donate_member, line.poor_help_money)
                    if line.noassign_money != 0:
                        record.save_donate_list(6, line.donate_member, line.noassign_money)
        else:
            raise ValidationError(u'捐款名冊為空，無法進行捐款作業')

    def add_to_list(self):
        for r in self.family_check:
            res = self.env['donate.order'].create({
                'donate_member': r.donate_member.id,
                'donate': self.donate_total,
                'con_phone': r.donate_member.cellphone,
                'donate_total': self.donate_total,
                'self_id': self.self_iden,
                'donate_type': self.donate_type,
                'payment_method': self.payment_method,
                'donate_date': self.donate_date,
                'road_money': r.road_money,
                'bridge_money': r.bridge_money,
                'coffin_money': r.coffin_money,
                'poor_help_money':r.poor_help_money,
                'noassign_money':r.noassign_money,
            })

    def save_donate_list(self, donate_type, member_id, money):  # 將明細產生

        if donate_type == 3:            #施棺捐款多了可用餘額的欄位
            self.write({
                'donate_list': [(0, 0, {
                    'donate_id': self.donate_id,
                    'donate_member': member_id.id,
                    'donate_type': donate_type,
                    'donate': money,
                    'donate_date': self.donate_date,
                    # 'self_id': member_id.self_iden,
                    # 'payment_method': int(self.payment_method),
                    # 'available_balance': money,
                    # 'key_in_user': self.key_in_user.id,
                    # 'cashier':self.work_id.id,
                    # 'debit_method': self.debit_method,
                })],
                'print_all_donor_list': self.print_all_donor_list
            })
        else:
            self.write({
                'donate_list': [(0, 0, {
                    'donate_id': self.donate_id,
                    'donate_member': member_id.id,
                    'donate_type': donate_type,
                    'donate': money,
                    'donate_date':self.donate_date,
                    # 'self_id': member_id.self_iden,
                    # 'payment_method': int(self.payment_method),
                    # 'key_in_user': self.key_in_user.id,
                    # 'cashier': self.work_id.id,
                    # 'debit_method': self.debit_method,
                })],
                'print_all_donor_list': self.print_all_donor_list
            })

        def parent_list_creat(self):
            r = []
            for line in self.donate_member.store_history.history_data:
                exist = False
                for family_line in self.family_check:
                    if family_line.donate_member.id == line.id:
                        exist = True

                if exist is False:
                    r.append([0, 0, {
                        'donate_member': line.id
                    }])

            self.write({
                'family_check': r
            })
            self.donate_list.unlink()

    @api.depends('bridge_money','road_money','coffin_money','poor_help_money','noassign_money')
    def calculate(self):
        for r in self:
            r.donate_total=r.bridge_money+r.road_money+r.coffin_money+r.poor_help_money+r.noassign_money

    def compute_des(self):
        for r in self:
            r.ps = r.donate_total

    @api.depends('donate_list')
    def compute_family_list(self):
        for line in self:
            str = ''
            for row in line.donate_list:
                if row.donate_type == 1:
                    str += " (%s %s %s )," % (row.donate_member.name, u'造橋', row.donate)
                if row.donate_type == 2:
                    str += " (%s %s %s )," % (row.donate_member.name, u'補路', row.donate)
                if row.donate_type == 3:
                    str += " (%s %s %s )," % (row.donate_member.name, u'施棺', row.donate)
                if row.donate_type == 4:
                    str += " (%s %s %s )," % (row.donate_member.name, u'伙食費', row.donate)
                if row.donate_type == 5:
                    str += " (%s %s %s )," % (row.donate_member.name, u'貧困扶助', row.donate)
                if row.donate_type == 6:
                    str += " (%s %s %s )," % (row.donate_member.name, u'一般捐款', row.donate)
                if row.donate_type == 99:
                    str += " (%s %s %s )," % (row.donate_member.name, u'其他工程', row.donate)
            line.donate_family_list = str.rstrip(',')

class DonateSingleLine(models.Model): #先產出一個資料表供當次捐款明細的編輯，才不會更改到原始會員資料
    _name = 'donate.family.line'

    parent_id = fields.Many2one(comodel_name='donate.single', index=True)
    donate_member = fields.Many2one(comodel_name='openacademy.gofor', string='捐款人', index=True)

    is_donate = fields.Boolean(string='是否捐助', related='donate_member.is_donate')
    is_merge = fields.Boolean(string='是否合併收據', related='donate_member.is_merge')

    bridge_money = fields.Integer(string='造橋')
    road_money = fields.Integer(string='補路')
    coffin_money = fields.Integer(string='施棺')
    poor_help_money = fields.Integer(string='貧困扶助')
    noassign_money = fields.Integer(string='一般捐款')


    #需要多一個class儲存donate_list
