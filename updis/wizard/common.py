# -*- coding: utf-8 -*-
from osv import osv,fields

class review_abstract(osv.AbstractModel):
	'''
	每一次流程审批我们要做下面的事情：
	1. 记录日志，谁提交的，审批了什么内容，审批者是谁，审批结果，审批时间
	2. 发送邮件通知
	3. 发送短信通知
	4. 更新对应项目信息
	'''
	_name = "project.review_abstract"	
	_columns = {	
		'send_email':fields.boolean(u"发送邮件通知"),
		'send_sms':fields.boolean(u"发送短信通知"),
		'comment':fields.text(u"Review Comment"),
		'reviewer_id':fields.many2one("res.users","Reviewer",required=True),
	}

	def _get_last_submitter(self,cr,uid,context=None):
		"""
		返回最近的提交人ID
		"""
		project_review_history = self.pool.get('project.review.history')
		return project_review_history.search(cr,uid,['result','=','submit'],limit=1)
review_abstract()