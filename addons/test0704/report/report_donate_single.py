# _*_ coding: utf-8 _*_
from odoo import models, api,fields
from odoo.exceptions import ValidationError
import datetime

class DonateSingleReport(models.Model):
    _name = 'donate.single.report'
    _description = u'報表用來整理收據資料用table'

    title_donate = fields.Many2one(comodel_name='openacademy.gofor', string='收據收件人')
    # donate_wizard = fields.Many2one(comodel_name='wizard.batch',string='捐款日期')
    title_doante_code = fields.Char(string='捐款編號')
    title_doante_date = fields.Char(string='捐款日期')
    title_work_id = fields.Char(string='收費員')
    title_Make_up_date=fields.Char(string='日期',default=lambda self: fields.date.today())
    title_state = fields.Integer(string='列印狀態')
    donate_line = fields.One2many(comodel_name='report.line',inverse_name='parent_id', string='個人捐款明細')
    title_total_price = fields.Integer(string='捐款總金額', compute='compute_price', store=True)
    title_total_price_big = fields.Char(string='金額大寫', compute='compute_price', store=True)
    title_year_fee = fields.Integer(string='年繳')
    key_in_user = fields.Many2one(comodel_name='res.users', string='輸入人員', states={2: [('readonly', True)]})
    work_id = fields.Many2one(comodel_name='res.partner', string='收費員')

    @api.depends('donate_line')
    def compute_price(self):
        for line in self:
            price = 0
            for row in line.donate_line:
                price += row.donate_price

            line.title_total_price = price
            line.title_total_price_big = self.convert(price)

    def convert(self, n):
        units = ['', '萬', '億']
        nums = ['零', '壹', '貳', '參', '肆', '伍', '陸', '柒', '捌', '玖']
        decimal_label = ['角', '分']
        small_int_label = ['', '拾', '佰', '仟']
        int_part, decimal_part = str(int(n)), str(n - int(n))[2:]  # 分离整数和小数部分

        res = []
        if decimal_part:
            res.append(''.join([nums[int(x)] + y for x, y in zip(decimal_part, decimal_label) if x != '0']))

        if int_part != '0':
            while int_part:
                small_int_part, int_part = int_part[-4:], int_part[:-4]
                tmp = ''.join([nums[int(x)] + (y if x != '0' else '') for x, y in
                               zip(small_int_part[::-1], small_int_label)[::-1]])
                tmp = tmp.rstrip('零').replace('零零零', '零').replace('零零', '零')
                unit = units.pop(0)
                if tmp:
                    tmp += unit
                    res.append(tmp)
        return ''.join(res[::-1])

class ReportLine(models.Model):
    _name = 'report.line'

    parent_id = fields.Many2one(comodel_name='donate.single.report')
    donate_id = fields.Char(string='捐款編號')
    donate_member_id = fields.Many2one(comodel_name='openacademy.gofor', string='收據收件人')
    name = fields.Char(string='捐款姓名')
    donate_type = fields.Selection(selection=[(01, '造橋'), (02, '補路'), (03, '施棺'), (05, '貧困扶助'), (06, '一般捐款')],
                                   string='捐款種類')
    donate_price = fields.Integer(string='捐款金額')
    is_merge = fields.Boolean(string='是否合併收據')
    print_all_donor_list = fields.Boolean(string='列印願意捐助的眷屬')

class ReportDonateSingleMerge(models.AbstractModel):
    _name = 'report.test0704.donate_single_merge'

    @api.multi
    def render_html(self, docids, data=None):
        docs = self.env['donate.single'].browse(docids)
        for line in docs:
            line.report_donate = line.donate_date
            if line.state == 'c':
                raise ValidationError(u'本捐款單已經作廢')
            elif line.state == 'a':
                # line.state = 2
                line.print_count+=1
                line.print_date = datetime.date.today()
                line.print_user = self.env.uid
            elif line.state == 'b':
                line.print_date = datetime.date.today()

        res_doc= []
        for line in docs:
            order_doc = []
            for order_line in line.donate_list:
                order_temp = {
                    'donate_id':order_line.donate_id,
                    'donate_member':order_line.donate_member.name,
                    'donate_type':dict(order_line.fields_get(allfields=['donate_type'])['donate_type']['selection'])[order_line.donate_type],
                    'donate':order_line.donate,
                }
                order_doc.append(order_temp)
            line.report_price_big = self.convert(line.donate_total)
            donor_code = ''
            if line.donate_member.w_id == False:
                donor_code = line.donate_member.new_coding
            else:
                donor_code = "%s (%s)" % (line.donate_member.new_coding, line.donate_member.w_id)
            temp = {
                'donate_id': line.donate_id,
                'donate_member': line.donate_member.name,
                'zip':line.zip,
                'rec_addr': line.rec_addr,
                'new_coding': donor_code,
                'donate_date': line.donate_date,
                'donate_total': line.donate_total,
                'key_in_user': line.key_in_user.name,
                'work_id': line.work_id.name,
                'report_price_big': line.report_price_big,
                'print_date': line.print_date,
                'state': line.state,
                'year_fee': line.year_fee,
                'rec_send':line.donate_member.rec_send,
                'order_line':order_doc
            }
            res_doc.append(temp)

        docargs = {
            'doc_ids': docids,
            'doc_model': 'donate.single',
            'docs': res_doc,
        }
        for row in docs:
            if row.state == 'a':
                row.state = 'b'
        return self.env['report'].render('test0704.donate_single_merge', values=docargs)

    def convert(self, n):
        units = ['', '萬', '億']
        nums = ['零', '壹', '貳', '參', '肆', '伍', '陸', '柒', '捌', '玖']
        decimal_label = ['角', '分']
        small_int_label = ['', '拾', '佰', '仟']
        int_part, decimal_part = str(int(n)), str(n - int(n))[2:]  # 分离整数和小数部分

        res = []
        if decimal_part:
            res.append(''.join([nums[int(x)] + y for x, y in zip(decimal_part, decimal_label) if x != '0']))

        if int_part != '0':
            while int_part:
                small_int_part, int_part = int_part[-4:], int_part[:-4]
                tmp = ''.join([nums[int(x)] + (y if x != '0' else '') for x, y in
                               zip(small_int_part[::-1], small_int_label)[::-1]])
                tmp = tmp.rstrip('零').replace('零零零', '零').replace('零零', '零')
                unit = units.pop(0)
                if tmp:
                    tmp += unit
                    res.append(tmp)
        return ''.join(res[::-1])
