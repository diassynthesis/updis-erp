# -*- coding: utf-8 -*-
from osv import osv,fields
from . import common
from openerp import SUPERUSER_ID

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
		"jianyixiangmufuzeren_id":fields.many2one("res.users",u"建议项目负责人"),
		"jiafang_id":fields.many2one('res.partner', u"甲方"),
	}
	def submit(self,cr,uid,ids,context=None):
		review_histories = self.pool.get("project.review.history")
		project_project = self.pool.get("project.project")
		sms_sms = self.pool.get("sms.sms")
		mail_mail = self.pool.get('mail.mail')
		#Create review history.
		for data in self.browse(cr,uid,ids,context=context):
			for project in project_project.browse(cr,uid,context['active_ids'],context=context):
				submitter = self.pool.get('res.users').browse(cr,uid,uid,context=context)
				reviewer = data.reviewer_id
				history={
					'fields':','.join(self._columns.keys()),
					'result':'submit',
					'comment':data.comment,
					'name':'填申请单提交所长审批',
					'submitter_id':submitter.id,
				}
				history_id = review_histories.create(cr,SUPERUSER_ID,history,context=context)
				
				if data.send_sms:			
					sms_sms.create(cr,uid,{
							'from':submitter.mobile,
							'to':reviewer.mobile,
							'content':data.comment,	
							'model':'project.review.history',
							'res_id':history_id,		
						},context=context)
				if data.send_email:
					mail_id = mail_mail.create(cr, uid, {
							'subject': u'请审批项目%s' % project.name,
							'body_html': '%s' % data.comment,
							'auto_delete': False,
							}, context=context)
					mail_mail.send(cr, uid, [mail_id], recipient_ids=[reviewer.id], context=context)
				project_project.write(cr,uid,project.id,{
					'guimo':data.guimo,
					'waibao':data.waibao,
					'shizhenpeitao':data.shizhenpeitao,
					'duofanghetong':data.duofanghetong,
					'jianyishejibumen_id':data.jianyishejibumen_id.id,
					'jianyixiangmufuzeren_id':data.jianyixiangmufuzeren_id.id,
					'jiafang_id':data.jiafang_id.id,
					'state':'suozhangshenpi',
					},context=context)
		return {'type': 'ir.actions.act_window_close'}
tijiaoshenqingdan()
