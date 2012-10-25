#-*- encoding: utf-8 -*-
from osv import fields,osv


class hr_employee_updis(osv.osv):
	_description = "Employee"
	_inherit = "hr.employee"
	_columns = {
		"folk": fields.char("Folk", size=32),
		# "degree": fields.selection([(u'学士',u'学士'), (u'理学学士',u'理学学士'),(u'文学学士',u'文学学士'),(u'工学学位',u'工学学位'),(u'工学学士',u'工学学士'),(u'硕士',u'硕士'), (u'理学硕士',u'理学硕士'),(u'工学硕士',u'工学硕士'),(u'建筑学学士',u'建筑学学士'),(u'建筑学硕士',u'建筑学硕士'),(u'法学硕士',u'法学硕士'),(u'博士',u'博士'),(u'理学博士',u'理学博士'),(u'工学博士',u'工学博士')], "Degree"),
		# "diploma": fields.selection([(u'高中',u'高中'),(u'大专',u'大专'),(u'本科',u'本科'),(u'大学本科',u'大学本科'),(u'大学',u'大学'),(u'研究生',u'研究生'),(u'中专',u'中专'),(u'博士',u'博士')],'Diploma'),   
		'degree': fields.char("Degree",size=128),
		'diploma': fields.char("Diploma",size=128),
		'academy': fields.char("Academy", size=128),
		'major': fields.char("Major", size=128),
        	'gender': fields.selection([(u'男', u'男'),(u'女', u'女')], 'Gender'),
	}
