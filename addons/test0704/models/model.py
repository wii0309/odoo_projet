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

    # state = fields.Selection([('draft', "Draft"),('confirmed', "Confirmed"),('done', "Done"),], default='draft')

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)

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


class Readclass(models.Model):
    _name = 'read.class'
    date_order = fields.Datetime(string='Order Date')
    buyer = fields.Many2one(comodel_name='res.partner', string='客戶')
    relatep = fields.Many2one(comodel_name='sale.order', string='關聯訂單')
    checkp = fields.Many2one(comodel_name='product.product', string='簽到產品')
    account = fields.Float(string='數量')
    price = fields.Float(string='單價')
    total = fields.Float(string='總金額')
    color = fields.Integer()


class Gofor(models.Model):
    _name = 'openacademy.gofor'
    description = fields.Text()
    name = fields.Char(string="姓名", required=True)
    birth = fields.Date(string='生日')
    cellphone = fields.Char(string='手機')
    con_phone = fields.Char(string='連絡電話')
    zip = fields.Char(string='收據郵遞區號')
    rec_addr = fields.Char(string='收據寄送地址', required=True)
    description = fields.Char(string='', compute='compute_des', store=True)
    memo = fields.Char(string='備忘錄')
    show = fields.Char(string='I will call you later at ')
    amount = fields.Integer(string='數值', required=True)
    state = fields.Selection(selection=[('abc', '未審核'), ('abcd', '已審核')], string='Status', default='abc', index=True)

    is_donate = fields.Boolean(string='是否捐助', default=True)
    is_merge = fields.Boolean(string='是否合併收據', default=True)

    store_history = fields.Many2one(comodel_name='openacademy.gofor', string='戶長')
    history_data = fields.One2many(comodel_name='openacademy.gofor', inverse_name='store_history')

    w_id = fields.Char(string='舊團員編號')
    new_coding = fields.Char(string='捐款者編號')
    rec_send = fields.Boolean(string='收據寄送', default=True)

    def toggle_donate(self):
        self.is_donate = not self.is_donate

    def toggle_merge(self):
        self.is_merge = not self.is_merge

    @api.depends('name', 'rec_addr')
    def compute_des(self):
        for r in self:
            if r.name and r.rec_addr:
                r.description = r.name + r.rec_addr

    @api.onchange('cellphone')
    def on_change_show(self):
        for r in self:
            r.show = r.cellphone

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = "%s" % (record.name)
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        res_id = super(Gofor, self).create(vals)
        if res_id.name is False:
            raise ValidationError(u'請輸入姓名')

        if res_id.store_history.id is False:  # 如果新建的捐款者資料沒有選定戶長是誰, 那麼就由系統自動將該使用者設為戶長
            res_id.write({
                'store_history': res_id.id,
            })
            return res_id
        # elif res_id.parent.id:  # 如果有選定戶長
        #      old_member_code = self.search([('id', '=', res_id.parent.id)])  # 搜尋該戶長的資料
        #      if old_member_code.w_id:  # 如果該戶長有w_id, 則將捐款者的w_id 設為與戶長相同的w_id
        #           res_id.write({
        #                'w_id': old_member_code.w_id
        #           })
