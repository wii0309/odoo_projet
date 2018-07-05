# -*- coding: utf-8 -*-
from odoo import models, fields
class Course(models.Model):
     _name = 'openacademy.course'

     name = fields.Char(string="Title", required=True)
     description = fields.Text()