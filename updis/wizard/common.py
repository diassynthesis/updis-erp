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
	def _get_comment(self, cr, uid, ids, field_name, arg, context):
		result = dict((id,False) for id in ids)
		return result
	def _add_comment(self, cr, uid, id, field_name, field_value, fnct_inv_arg=None, context=None):
		data = self.browse(cr,uid,id,context=context)
		log = u'''
		<div>
		%s %s:
		<p><strong>%s </strong></p>
		</div>		
		'''%(data.submitter_id.name,data.create_date,field_value)
		review_log = data.review_log and data.review_log or u''
		review_log += log;
		return self.write(cr,uid,id,{'review_log':review_log},context=context)
	_name = "project.review.abstract"	
	_columns = {
		'create_date':fields.datetime('Create Date'),
		'project_id':fields.many2one('project.project','Project'),
		'send_email':fields.boolean(u"发送邮件通知"),
		'send_sms':fields.boolean(u"发送短信通知"),
		'review_log':fields.html(u"Review Comment",readonly=True),
		'comment':fields.function(_get_comment,fnct_inv=_add_comment,type="char",size=256,string=u"附注"),
		'reviewer_id':fields.many2one("res.users","Reviewer",required=True),
		'submitter_id':fields.many2one("res.users","Submitter",required=True),
		'state':fields.selection([
			('draft','Draft'),
			('submitted','Submitted'),
			('accepted','Accepted'),
			('rejected','Rejected'),
			],"Status",readonly=True,select=True)
	}
	_defaults = {
		'state':'draft',
		'submitter_id':lambda self, cr, uid, c=None:uid,
	}
	def _update_project_form(self,cr,uid,ids,form_field_name,context=None):
		project = self.pool.get('project.project')
		for f in self.browse(cr,uid,ids):
			project.write(cr,uid,f.project_id.id,{
				form_field_name:f.id
				})
		return True
	
review_abstract()