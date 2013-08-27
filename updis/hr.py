#-*- encoding: utf-8 -*-
import datetime
from osv import fields, osv


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

        'image': fields.related('user_id', 'image', type='binary', string='Employee Image'),
        'image_medium': fields.related('user_id', 'image_medium', type='binary', string='Employee Image Medium'),
        'image_small': fields.related('user_id', 'image_small', type='binary', string='Employee Image Small'),
        'has_image': fields.related('user_id', 'has_image', type='boolean', string='Employee Have Image'),
        'trains': fields.one2many('updis.hr.training.record', 'employee',
                                  # 'employee_training_rel', 'employee_id', 'training_id',
                                  'Trains'),
    }

    def onchange_address_id(self, cr, uid, ids, address, context=None):
        return {'value': {}}