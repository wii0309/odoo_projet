# -*- coding: utf-8 -*-
from odoo import models, fields,api
import datetime
class Sendbook(models.Model):
    _name = 'send.book'
    name = fields.Char(string='姓名')
    id_card=fields.Char(string='身分證')
    address=fields.Char(string='地址')
    send_ids=fields.One2many(comodel_name='send.system',inverse_name='person_id')
    person_type=fields.Selection(selection=[(1, '學生'),(2, '教師')],string='人員種類')

class Bookinfo(models.Model):
    _name = 'book.info'
    name = fields.Char(string='書名')
    isbn = fields.Char(string='ISBN')
    send_ids = fields.One2many(comodel_name='send.system', inverse_name='book_id')

class Sedsystem(models.Model):
    _name = 'send.system'
    name = fields.Char('標題',compute='set_default_name')
    person_id=fields.Many2one(comodel_name='send.book',String='借書人')
    book_id=fields.Many2one(comodel_name='book.info',String='借出書籍')
    ps=fields.Text('備註')

    def send_over(self):
        return_date = datetime.date.today().strftime('%Y-%m-%d')
        self.ps='已歸還'+return_date

    # @api.depends('book_id','person_id')
    # def set_default_name(self):
    #     for line in self:
    #         if (self.book_id is True and self.person_id is True)
    #          self.name=self.name +self.book_id.name
