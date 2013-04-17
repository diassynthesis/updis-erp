#-*- encoding: utf-8 -*-
from osv import fields, osv


class hr_employee_updis(osv.osv):
    _description = "Employee"
    _inherit = "hr.employee"

    def _get_user_rules(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        users = self.pool.get('res.users').read(cr, uid, uid, fields=['groups_id'])
        groups = self.pool.get('ir.model.data').search(cr, uid,
                                                       [('name', '=', 'group_user'), ('model', '=', 'res.groups')])
        if groups:
            re = self.pool.get('ir.model.data').read(cr, uid, groups[0])['res_id']
            if re in users['groups_id']:
                for obj in self.browse(cr, uid, ids, context=context):
                    result[obj.id] = obj.user_id.id == uid and 1 or 2
        return result

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
        'year_vac_days': fields.integer("Year Vacation Days"),
        'have_vac_days': fields.integer("Have Vacation Days"),
        'insurance': fields.char("Insurance", size=128),
        'awards': fields.text("Award"),
        'study_list': fields.text("Study List"),
        'interest': fields.char("Interest", size=100),
        'practice': fields.text("Practice"),
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
        'home_phone': fields.char('Home Phone', size=32, readonly=False),
        'current_user_rules': fields.function(_get_user_rules, type='integer',
                                              string="User rules"),
    }

