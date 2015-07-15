# -*- encoding: utf-8 -*-
import datetime
from operator import itemgetter
import random
import math
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from up_tools.oalib import client as oa_client


def monkey_create(self, cr, uid, data, context=None):
    employee_id = super(osv.Model, self).create(cr, uid, data, context=context)
    return employee_id


from openerp.addons.hr import hr

hr.hr_employee.create = monkey_create


class hr_employee_updis(osv.osv):
    _description = "Employee"
    _inherit = "hr.employee"

    def _get_total_vacations(self, cr, uid, ids, name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.enter_date and record.begin_work_date:
                enter_date = datetime.datetime.strptime(record.enter_date, "%Y-%m-%d").date()
                begin_work_date = datetime.datetime.strptime(record.begin_work_date, "%Y-%m-%d").date()
                today = datetime.date.today()

                if (today - enter_date).days < 366:
                    res[record.id] = 0
                elif (today - begin_work_date).days >= 365 * 20:
                    res[record.id] = 15
                elif 365 * 20 > (today - begin_work_date).days >= 365 * 10:
                    res[record.id] = 10
                else:
                    res[record.id] = 5
            else:
                res[record.id] = 0
        return res

    _columns = {
        'gender': fields.selection([(u'男', u'男'), (u'女', u'女')], 'Gender'),
        "folk": fields.char("Folk", size=32),
        "native_place": fields.char(u"Native Place", size=32),
        'diploma': fields.char("Diploma", size=128),
        'degree': fields.char("Degree", size=128),
        'academy': fields.char("Academy", size=128),
        'begin_work_date': fields.date("Begin Work Date"),
        'enter_date': fields.date("Enter Date"),
        'contract_date': fields.date("Contract Date"),
        'aptitude': fields.char("Aptitude", size=128),
        'major': fields.char("Major", size=128),
        'year_vac_days': fields.function(_get_total_vacations, type='integer', method=True, store=False,
                                         string="Year Vacation Days", readonly=1),
        'have_vac_days': fields.integer("Have Vacation Days"),
        'insurance': fields.char("Insurance", size=128),
        'awards': fields.text("Award"),
        'study_list': fields.text("Study List"),
        'go_abroad_list': fields.text("Go Abroad List"),
        'join_ploy': fields.text("Join Ploy"),
        'strong_point': fields.text("Strong Point"),
        'business': fields.char("Business", size=100),
        'business_date': fields.date("Business Date"),
        'duty': fields.char("Duty", size=100),
        'duty_date': fields.date("Duty Date"),
        'title': fields.char("Title Name", size=100),
        'title_date': fields.date("Title Date"),
        'reg_tax': fields.char("Reg Tax", size=100),
        'reg_tax_date': fields.date("RegTax Date"),
        'gra_date': fields.date('Graduate Date'),
        'out_date': fields.date('Out Date'),
        'reg_tax_no': fields.char('Reg Tax No', size=128),
        'person_resume': fields.related('user_id', 'person_resume', type="text",
                                        string="Personal Resume"),
        'mobile_phone': fields.related('user_id', 'mobile_phone', type="char",
                                       string="Work Mobile"),
        'work_phone': fields.related('user_id', 'work_phone', type="char",
                                     string="Work Phone"),
        'address_id': fields.related('user_id', 'address_id', type="many2one", relation='res.partner',
                                     string="Working Address"),
        'work_email': fields.related('user_id', 'work_email', type="char",
                                     string="Work Email"),
        'work_location': fields.related('user_id', 'work_location', type="char",
                                        string="Office Location"),
        'interest': fields.related('user_id', 'interest', type="char",
                                   string="Interest"),
        'practice': fields.related('user_id', 'practice', type="char",
                                   string="Practice"),
        'home_phone': fields.related('user_id', 'home_phone', type="char",
                                     string="Home Phone"),
        'gender_rel': fields.related('user_id', 'gender', type="selection", selection=[(u'男', u'男'), (u'女', u'女')], string='Gender'),

        'image': fields.related('user_id', 'image', type='binary', string='Employee Image'),
        'image_medium': fields.related('user_id', 'image_medium', type='binary', string='Employee Image Medium'),
        'image_small': fields.related('user_id', 'image_small', type='binary', string='Employee Image Small'),
        'has_image': fields.related('user_id', 'has_image', type='boolean', string='Employee Have Image'),
        'trains': fields.one2many('updis.hr.training.record', 'employee',
                                  # 'employee_training_rel', 'employee_id', 'training_id',
                                  'Trains'),
        'speciality_id': fields.many2many('hr.employee.speciality', 'hr_employee_with_special_rel', 'employee_id',
                                          'speciality_id',
                                          string='Specialities'),
    }

    def clear_have_vac_days(self, cr, uid, ids, context=None):
        cr.execute("update hr_employee set have_vac_days=0")
        return True

    def onchange_address_id(self, cr, uid, ids, address, context=None):
        return {'value': {}}

    def create_oa(self, cr, uid, employee_id, context=None):
        employee = self.browse(cr, 1, employee_id, context=context)
        json_params = {
            "iUserCode": employee.id,
            "sStaffDpt": employee.department_id.id or '',
            # "sStaffDpt": 99,
            "iMainUser": employee.user_id.id or '',
            "sStaffName": employee.name or '',
            "dStaffBirthday": employee.birthday or '',
            "sStaffIdentity": employee.identification_id or '',
            "sStaffSex": employee.gender or '',
            "sStaffProfession": employee.major or '',
            "sExp5": ','.join([s.name for s in employee.speciality_id]) or '',
            "sExp7": employee.person_resume or '',
            "sExp2": employee.practice or '',
            "dDutyTime": employee.duty_date or '',
            "dPostLevelTime": employee.business_date or '',
            "sStaffWageCard2": employee.otherid or '',
            "sStaffJobLocation": employee.work_location or '',
            "sStaffOfficePhone": employee.work_phone or '',
            "sStaffMobilePhone": employee.mobile_phone or '',
            "sStaffEmail": employee.work_email or '',
            "sExp1": employee.insurance or '',
            "dBargainEndTime": employee.contract_date or '',
            "sExp4": employee.go_abroad_list or '',
            "sExp6": employee.study_list or '',
            # "sStaffMarriage": "婚姻状况",
            "sStaffDegree": employee.degree or '',
            "sStaffPiploma": employee.diploma or '',
            "sStaffHomePhone": employee.home_phone or '',
            "iPayBand": employee.year_vac_days or '',
            "dStaffJoinWorkTime": employee.begin_work_date or '',
            "sPassportCode": employee.passport_id or '',
            "sStaffGraduateSchool": employee.academy or '',
            "dStaffGraduateTime": employee.gra_date or '',
            "sStaffNation": employee.folk or '',
            "dOffPostDate": employee.out_date or '',
            "sStaffNativePlace": employee.native_place or '',
            "sDuty": employee.duty or '',
            "sHonor": employee.job_id.name or '',
            "sPost": employee.title or '',
            "dPostTime": employee.title_date or '',
            "sPostLevel": employee.business or '',
            "sStaffWorkType": ','.join([t.name for t in employee.category_ids]) or '',
            "sPostName": employee.reg_tax or '',
            "sGetCertificate": employee.reg_tax_no or '',
            "dRegisterDate": employee.reg_tax_date or '',
        }
        oa_client.CreateEmployee(json=json_params)

    def write_oa(self, cr, uid, ids, context):
        employees = self.browse(cr, 1, ids, context=context)
        for employee in employees:
            json_params = {
                "iUserCode": employee.id,
                "sStaffDpt": employee.department_id.id or '',
                # "sStaffDpt": 99,
                "iMainUser": employee.user_id.id or '',
                "sStaffName": employee.name or '',
                "dStaffBirthday": employee.birthday or '',
                "sStaffIdentity": employee.identification_id or '',
                "sStaffSex": employee.gender or '',
                "sStaffProfession": employee.major or '',
                "sExp5": ','.join([s.name for s in employee.speciality_id]) or '',
                "sExp7": employee.person_resume or '',
                "sExp2": employee.practice or '',
                "dDutyTime": employee.duty_date or '',
                "dPostLevelTime": employee.business_date or '',
                "sStaffWageCard2": employee.otherid or '',
                "sStaffJobLocation": employee.work_location or '',
                "sStaffOfficePhone": employee.work_phone or '',
                "sStaffMobilePhone": employee.mobile_phone or '',
                "sStaffEmail": employee.work_email or '',
                "sExp1": employee.insurance or '',
                "dBargainEndTime": employee.contract_date or '',
                "sExp4": employee.go_abroad_list or '',
                "sExp6": employee.study_list or '',
                # "mRemark": "备注",
                # "sStaffMarriage": "婚姻状况",
                "sStaffDegree": employee.degree or '',
                "sStaffPiploma": employee.diploma or '',
                "sStaffHomePhone": employee.home_phone or '',
                "iPayBand": employee.year_vac_days or '',
                "dStaffJoinWorkTime": employee.begin_work_date or '',
                "sPassportCode": employee.passport_id or '',
                "sStaffGraduateSchool": employee.academy or '',
                "dStaffGraduateTime": employee.gra_date or '',
                "sStaffNation": employee.folk or '',
                "dOffPostDate": employee.out_date or '',
                "sStaffNativePlace": employee.native_place or '',
                "sDuty": employee.duty or '',
                "sHonor": employee.job_id.name or '',
                "sPost": employee.title or '',
                "dPostTime": employee.title_date or '',
                "sPostLevel": employee.business or '',
                "sStaffWorkType": ','.join([t.name for t in employee.category_ids]) or '',
                "sPostName": employee.reg_tax or '',
                "sGetCertificate": employee.reg_tax_no or '',
                "dRegisterDate": employee.reg_tax_date or '',
            }
            oa_client.UpdateEmployee(json=json_params)

    def unlink_oa(self, cr, uid, ids, context):
        for employee_id in ids:
            oa_client.DeleteEmployee(iUserCode=employee_id, hashcode=oa_client.HASH_CODE)

    def unlink(self, cr, uid, ids, context=None):
        self.unlink_oa(cr, uid, ids, context)
        return super(hr_employee_updis, self).unlink(cr, uid, ids, context)

    def create(self, cr, uid, vals, context=None):
        employee_id = super(hr_employee_updis, self).create(cr, uid, vals, context)
        self.create_oa(cr, uid, employee_id, context)
        return employee_id

    def write(self, cr, user, ids, vals, context=None):
        result = super(hr_employee_updis, self).write(cr, user, ids, vals, context=None)
        self.write_oa(cr, user, ids, context)
        return result


class EmployeeSpeciality(osv.osv):
    _description = "Employee Speciality"
    _name = 'hr.employee.speciality'

    _columns = {
        'name': fields.char(size=128, string='Name', required=1),
        'parent_id': fields.many2one('hr.employee.speciality', string='Parent Name'),
        'child_ids': fields.one2many('hr.employee.speciality', 'parent_id', string='Children Name'),

    }

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        ids = [ids] if isinstance(ids, int) else ids
        while len(ids):
            cr.execute('select distinct parent_id from hr_employee_speciality where id IN %s', (tuple(ids), ))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive Speciality.', ['parent_id'])
    ]

    _sql_constraints = [('speciality_name_unique', 'unique(name)', 'name must be unique !')]


class EmployeeBirthdayWish(osv.osv):
    _description = "Birthday Wish"
    _name = 'hr.birthday.wish'
    _columns = {
        'name': fields.text('Wish'),
    }

    def get_today_birthday(self, cr, uid):
        total_wish = self.search(cr, 1, [])
        no = int(len(total_wish) * random.random()) if total_wish else None
        if no:
            random_wish = total_wish[no]
        else:
            random_wish = None
        wishes = self.browse(cr, SUPERUSER_ID, random_wish).name if random_wish else ''
        cr.execute(
            "select DISTINCT h.id as id from hr_employee as h , resource_resource as r " +
            "Where date_part('day', h.birthday) = date_part('day', CURRENT_DATE) And " +
            "date_part('MONTH', h.birthday) = date_part('MONTH', CURRENT_DATE) AND " +
            "r.active is true and h.resource_id = r.id")
        employees = self.pool.get('hr.employee').browse(cr, uid, map(itemgetter(0), cr.fetchall()))
        return [e.name for e in employees], wishes

    def cron_birthday_notify(self, cr, uid, context=None):
        system_notify = self.pool['ir.config_parameter'].get_param(cr, uid, 'birthday.nofity', context)
        cr.execute("""
            select DISTINCT h.id as id from hr_employee as h , resource_resource as r
            Where date_part('day', h.birthday) = date_part('day', CURRENT_DATE + interval '1' day) And
            date_part('MONTH', h.birthday) = date_part('MONTH', CURRENT_DATE + interval '1' day) AND
            r.active is true and h.resource_id = r.id
            """)
        employees = self.pool.get('hr.employee').browse(cr, uid, map(itemgetter(0), cr.fetchall()))
        for employee in employees:
            notify = system_notify.format(name=employee.name)
            self.pool['sms.sms'].send_sms_to_users(cr, uid, 'hr.birthday.wish', notify, 'hr.birthday.wish', '', employee.user_id.id, context=context)