# -*- coding: utf-8 -*-
from osv import osv,fields
from . import common

class tijiaoshenqingdan(osv.osv_memory):
	"""tijiaoshenqingdan"""
	_name="project.tijiaoshenqingdan"
	_description="tijiaoshenqingdan"
	_inherit=['project.review_abstract']
	_columns = {	
		"guimo":fields.char(u"规模",size=64),
		"waibao":fields.boolean(u"是否外包"),
		"shizhenpeitao":fields.boolean(u"市政配套"),
		"duofanghetong":fields.boolean(u"多方合同"),
		"jianyishejibumen_id":fields.many2one("hr.department",u"建议设计部门"),
		"jianyixiangmufuzeren_id":fields.many2one("hr.employee",u"建议项目负责人"),
		"jiafang_id":fields.many2one('res.partner', u"甲方"),

		'send_email':fields.boolean(u"发送邮件通知"),
		'send_sms':fields.boolean(u"发送短信通知"),
	}
tijiaoshenqingdan()