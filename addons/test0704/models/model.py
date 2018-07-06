# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import timedelta

class Course(models.Model):
     _name = 'openacademy.course'

     name = fields.Char(string="Title", required=True)
     description = fields.Text()
     responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True)
     session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")

     # 去改寫action的Duplicate
     @api.multi
     def copy(self, default=None):
          default = dict(default or {})

          copied_count = self.search_count([('name', '=like', u"Copy of {}%".format(self.name))])

          if not copied_count:
               new_name = u"Copy of {}".format(self.name)
          else:
               new_name = u"Copy of {} ({})".format(self.name, copied_count)

          default['name'] = new_name
          return super(Course, self).copy(default)

     # unlink 是 改寫Action的Delete

     _sql_constraints = [
          ('name_description_check',
           'CHECK(name != description)',
           "The title of the course should not be the description"),
          ('name_unique',
           'UNIQUE(name)',
           "The course title must be unique"),
     ]


class Session(models.Model):
     _name = 'openacademy.session'

     @api.depends('attendee_ids')
     def _get_attendees_count(self):
          for r in self:
               r.attendees_count = len(r.attendee_ids)

     name = fields.Char(required=True)
     start_date = fields.Date(default=fields.Date.today)
     duration = fields.Float(digits=(6, 2), help="Duration in days")
     seats = fields.Integer(string="Number of seats")
     active = fields.Boolean(default=True)
     color = fields.Integer()

     instructor_id = fields.Many2one('res.partner', string="Instructor",
                                     domain=['|', ('instructor', '=', True), ('category_id.name', 'ilike', "Teacher")])
     course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course", required=True)
     attendee_ids = fields.Many2many('res.partner', string="Attendees")
     taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
     end_date = fields.Date(string="End Date", store=True, compute='_get_end_date', inverse='_set_end_date')
     hours = fields.Float(string="Duration in hours", compute='_get_hours', inverse='_set_hours')
     attendees_count = fields.Integer(string="Attendees count", compute='_get_attendees_count', store=True)

     @api.depends('seats', 'attendee_ids')
     def _taken_seats(self):
          for r in self:
               if not r.seats:
                    r.taken_seats = 0.0
               else:
                    r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats



     @api.depends('duration')
     def _get_hours(self):
          for r in self:
               r.hours = r.duration * 24

     def _set_hours(self):
          for r in self:
               r.duration = r.hours / 24

     @api.depends('start_date', 'duration')
     def _get_end_date(self):
          for r in self:
               if not (r.start_date and r.duration):
                    r.end_date = r.start_date
                    continue
               start = fields.Datetime.from_string(r.start_date)
               duration = timedelta(days=r.duration, seconds=-1)
               r.end_date = start + duration

     def _set_end_date(self):
          for r in self:
               if not (r.start_date and r.end_date):
                    continue
               start_date = fields.Datetime.from_string(r.start_date)
               end_date = fields.Datetime.from_string(r.end_date)
               r.duration = (end_date - start_date).days + 1

     @api.onchange('seats', 'attendee_ids')
     def _verify_valid_seats(self):
          if self.seats < 0:
               return {
                    'warning': {
                         'title': "Incorrect 'seats' value",
                         'message': "The number of available seats may not be negative",
                    },
               }

          if self.seats < len(self.attendee_ids):
               return {
                    'warning': {
                         'title': "Too many attendees",
                         'message': "Increase seats or remove excess attendees",
                    },
               }

     @api.constrains('instructor_id', 'attendee_ids')
     def _check_instructor_not_in_attendees(self):
          for r in self:
               if r.instructor_id and r.instructor_id in r.attendee_ids:
                    raise exceptions.ValidationError("A session's instructor can't be an attendee")
class Gofor(models.Model):
     _name = 'openacademy.gofor'
     description = fields.Text()
     name = fields.Char(string="姓名",required=True)
     birth = fields.Date(string='生日')
     cellphone = fields.Char(string='手機')
     con_phone = fields.Char(string='連絡電話')
     zip = fields.Char(string='收據郵遞區號')
     rec_addr = fields.Char(string='收據寄送地址',required=True)
     description=fields.Char(string='',compute='compute_des',store=True)
     memo = fields.Char(string='備忘錄')
     show = fields.Char(string='I will call you later at ')
     amount=fields.Integer(string='數值',required=True)

     store_history=fields.Many2one(comodel_name='openacademy.gofor',string='儲存的')
     history_data = fields.One2many(comodel_name='openacademy.gofor', inverse_name='store_history')



     @api.depends('name', 'rec_addr')
     def compute_des(self):
          for r in self:
               if r.name and r.rec_addr:
                    r.description = r.name + r.rec_addr

     @api.onchange('cellphone')
     def on_change_show(self):
          for r in self:
               r.show=r.cellphone


