#-*- encoding: utf-8 -*-
from osv import fields,osv


class hr_employee_updis(osv.osv):
	_description = "Employee"
	_inherit = "hr.employee"
	_columns = {
		"folk": fields.char("Folk", size=32),
		"degree": fields.selection([(u'学士',u'学士'),(u'硕士',u'硕士'),(u'博士',u'博士')], "Degree"),
		"diploma": fields.selection([(u'大专',u'大专'),(u'本科',u'本科')],'Diploma'),   
		'academy': fields.char("Academy", size=128),
		'major': fields.char("Major", size=128),		
	}
