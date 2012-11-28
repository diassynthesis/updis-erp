# -*- coding: utf-8 -*-
from osv import osv,fields

class review_abstract(osv.AbstractModel):
	_name = "project.review_abstract"
	_columns = {	
		'send_email':fields.boolean(u"发送邮件通知"),
		'send_sms':fields.boolean(u"发送短信通知"),
		'comment':fields.text(u"Review Comment"),
	}
	def accept(self,cr,uid,ids,context=None):
		return True
	def reject(self,cr,uid,ids,context=None):
		return True

review_abstract()