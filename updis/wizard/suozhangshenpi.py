# -*- coding: utf-8 -*-
from osv import osv,fields
from tools.translate import _
from . import common
from openerp import SUPERUSER_ID

class suozhangshenpi_form(osv.Model):
	"""所长审批单"""
	_name="project.review.suozhangshenpi.form"
	_description=u"所长审批任意人员提交的申请单"
	_inherit=['project.review.abstract']
	_columns={
		# 基础信息 
		"guimo":fields.char(u"规模",size=64),
		"waibao":fields.boolean(u"是否外包"),
		"shizhenpeitao":fields.boolean(u"市政配套"),
		"duofanghetong":fields.boolean(u"多方合同"),
		"jianyishejibumen_id":fields.many2one("hr.department",u"建议设计部门"),
		"jianyixiangmufuzeren_id":fields.many2one("res.users",u"建议项目负责人"),
		"jiafang_id":fields.many2one('res.partner', u"甲方"),		

		# 所长审批
		"yaoqiuxingchengwenjian":fields.selection([(u"已形成",u"已形成"),(u"未形成，但已确认",u"未形成，但已确认")],
			u"顾客要求形成文件否"),		
		"zhaobiaoshu":fields.boolean(u"有招标书"),# 明示要求
		"weituoshu":fields.boolean(u"有委托书"),# 明示要求
		"xieyicaoan":fields.boolean(u"有协议/合同草案"),# 明示要求
		"koutouyaoqiujilu":fields.boolean(u"有口头要求记录"),# 明示要求
		"yinhanyaoqiu":fields.selection([(u"有",u"有（需在评审记录一栏中标明记录）"),(u"无",u"无")],u"隐含要求"),
		"difangfagui":fields.selection([(u"有",u"有（需在评审记录一栏中标明记录）"),(u"无",u"无")],u"地方规范或特殊法律法规"),
		"fujiayaoqiu":fields.selection([(u"有",u"有（需在评审记录一栏中标明记录）"),(u"无",u"无")],u"附加要求"),
		"hetongyizhi":fields.selection([(u"合同/协议要求表述不一致已解决",u"合同/协议要求表述不一致已解决"),
			(u"没有出现不一致",u"没有出现不一致")],u"不一致是否解决"),	
		"ziyuan":fields.selection([(u'人力资源满足',u'人力资源满足'),(u'人力资源不足',u'人力资源不足')],u'人力资源'),#本院是否有能力满足规定要求
		"shebei":fields.selection([(u'设备满足','设备满足'),(u'设备不满足',u'设备不满足')],u"设备"),#本院是否有能力满足规定要求
		"gongqi":fields.selection([(u'工期可接受','工期可接受'),(u'工期太紧',u'工期太紧')],u"工期"),#本院是否有能力满足规定要求
		"shejifei":fields.selection([(u'设计费合理','设计费合理'),(u'设计费太低',u'设计费太低')],u'设计费'),#本院是否有能力满足规定要求
	}
	def update_project_suozhangshenpi_form(self,cr,uid,ids,*args):		
		return self._update_project_form(cr,uid,ids,'suozhangshenpi_form_id')
class updis_project(osv.Model):
	_inherit='project.project'	
	_columns={
		'suozhangshenpi_form_id':fields.many2one('project.review.suozhangshenpi.form',u'所长审批单'),
	}
	def action_suozhangshenpi(self, cr, uid, ids, context=None):
		return _get_action(cr,uid,ids,'project.review.suozhangshenpi.form',u'所长审批单')
	def test_suozhangform_accepted(self, cr, uid, ids, *args):
		return self._test_accepted(cr,uid,ids,'suozhangshenpi_form_id',*args)
	def suozhangform_get(self, cr, uid, ids, *args):
		return self._get_form(cr,uid,ids,'suozhangshenpi_form_id',*args)
# class suozhangshenpi(osv.Model):
# 	"""
# 	所长审批任意人员提交的申请单
# 	"""
# 	_name="project.suozhangshenpi"
# 	_description=u"所长审批任意人员提交的申请单"
# 	_inherit=['project.review_abstract']
# 	_columns={
# 		"guimo":fields.char(u"规模",size=64,readonly=True),
# 		"waibao":fields.boolean(u"是否外包",readonly=True),
# 		"shizhenpeitao":fields.boolean(u"市政配套",readonly=True),
# 		"duofanghetong":fields.boolean(u"多方合同",readonly=True),
# 		"jianyishejibumen_id":fields.many2one("hr.department",u"建议设计部门",readonly=True),
# 		"jianyixiangmufuzeren_id":fields.many2one("res.users",u"建议项目负责人",readonly=True),
# 		"jiafang_id":fields.many2one('res.partner', u"甲方",readonly=True),
# 	}

# 	def accept(self,cr,uid,ids,context=None):
# 		review_histories = self.pool.get("project.review.history")
# 		project_project = self.pool.get("project.project")
# 		sms_sms = self.pool.get("sms.sms")
# 		mail_mail = self.pool.get('mail.mail')
# 		#Create review history.
# 		for data in self.browse(cr,uid,ids,context=context):
# 			for project in project_project.browse(cr,uid,context['active_ids'],context=context):
# 				reviewer = self.pool.get('res.users').browse(cr,uid,uid,context=context)
# 				submitter = self._get_last_submitter(cr,uid,context=context)
# 				history={
# 					'fields':','.join(self._columns.keys()),
# 					'result':'accepted',
# 					'comment':data.comment,
# 					'name':u'所长审批已经通过',
# 					'reviewer_id':data.reviewer_id.id,
# 				}
# 				history_id = review_histories.create(cr,SUPERUSER_ID,history,context=context)
				
# 				if data.send_sms:			
# 					sms_sms.create(cr,uid,{
# 							'from':submitter.mobile,
# 							'to':reviewer.mobile,
# 							'content':data.comment,	
# 							'model':'project.review.history',
# 							'res_id':history_id,		
# 						},context=context)
# 				if data.send_email:
# 					mail_id = mail_mail.create(cr, uid, {
# 							'subject': u'请审批项目%s' % project.name,
# 							'body_html': '%s' % data.comment,
# 							'auto_delete': False,
# 							}, context=context)
# 					mail_mail.send(cr, uid, [mail_id], recipient_ids=[reviewer.id], context=context)
# 				project_project.write(cr,uid,project.id,{
# 					'guimo':data.guimo,
# 					'waibao':data.waibao,
# 					'shizhenpeitao':data.shizhenpeitao,
# 					'duofanghetong':data.duofanghetong,
# 					'jianyishejibumen_id':data.jianyishejibumen_id.id,
# 					'jianyixiangmufuzeren_id':data.jianyixiangmufuzeren_id.id,
# 					'jiafang_id':data.jiafang_id.id,
# 					'state':'suozhangshenpi',
# 					},context=context)
# 		return {'type': 'ir.actions.act_window_close'}
# 	def reject(self,cr,uid,ids,context=None):
# 		pass
# suozhangshenpi()
# class tijiaojingyingshi(osv.osv_memory):
# 	"""
# 	所长提交经营室审批
# 	"""
# 	_name="project.tijiaojingyingshi"
# 	_description=u"所长提交经营室审批"
# 	_inherit=['project.review_abstract']
# 	_columns = {
# 		"yaoqiuxingchengwenjian":fields.selection([(u"已形成",u"已形成"),(u"未形成，但已确认",u"未形成，但已确认")],
# 			u"顾客要求形成文件否"),	
# 		"zhaobiaoshu":fields.boolean(u"有招标书"),# 明示要求
# 		"weituoshu":fields.boolean(u"有委托书"),# 明示要求
# 		"xieyicaoan":fields.boolean(u"有协议/合同草案"),# 明示要求
# 		"koutouyaoqiujilu":fields.boolean(u"有口头要求记录"),# 明示要求
# 		"yinhanyaoqiu":fields.selection([(u"有",u"有（需在评审记录一栏中标明记录）"),(u"无",u"无")],u"隐含要求"),
# 		"difangfagui":fields.selection([(u"有",u"有（需在评审记录一栏中标明记录）"),(u"无",u"无")],u"地方规范或特殊法律法规"),
# 		"fujiayaoqiu":fields.selection([(u"有",u"有（需在评审记录一栏中标明记录）"),(u"无",u"无")],u"附加要求"),
# 		"hetongyizhi":fields.selection([(u"合同/协议要求表述不一致已解决",u"合同/协议要求表述不一致已解决"),
# 			(u"没有出现不一致",u"没有出现不一致")],u"不一致是否解决"),	
# 		"ziyuan":fields.selection([(u'人力资源满足',u'人力资源满足'),(u'人力资源不足',u'人力资源不足')],u'人力资源'),#本院是否有能力满足规定要求
# 		"shebei":fields.selection([(u'设备满足',u'设备满足'),(u'设备不满足',u'设备不满足')],u"设备"),#本院是否有能力满足规定要求
# 		"gongqi":fields.selection([(u'工期可接受',u'工期可接受'),(u'工期太紧',u'工期太紧')],u"工期"),#本院是否有能力满足规定要求
# 		"shejifei":fields.selection([(u'设计费合理',u'设计费合理'),(u'设计费太低',u'设计费太低')],u'设计费'),#本院是否有能力满足规定要求

# 	}
# 	def submit(self,cr,uid,ids,context=None):
# 		review_histories = self.pool.get("project.review.history")
# 		project_project = self.pool.get("project.project")
# 		sms_sms = self.pool.get("sms.sms")
# 		mail_mail = self.pool.get('mail.mail')
# 		#Create review history.
# 		for data in self.browse(cr,uid,ids,context=context):
# 			for project in project_project.browse(cr,uid,context['active_ids'],context=context):
# 				reviewer = data.reviewer_id
# 				submitter = self.pool.get('res.users').browse(cr,uid,uid,context=context)
# 				history={
# 					'fields':'guimo,waibao,shizhenpeitao,duofanghetong,jianyishejibumen_id,jianyixiangmufuzeren_id,jiafang_id',
# 					'result':'accepted',
# 					'comment':data.comment,
# 					'name':u'填申请单提交所长审批',
# 					'reviewer_id':data.reviewer_id.id,
# 				}
# 				history_id = review_histories.create(cr,SUPERUSER_ID,history,context=context)
				
# 				if data.send_sms:			
# 					sms_sms.create(cr,uid,{
# 							'from':submitter.mobile,
# 							'to':reviewer.mobile,
# 							'content':data.comment,	
# 							'model':'project.review.history',
# 							'res_id':history_id,		
# 						},context=context)
# 				if data.send_email:
# 					mail_id = mail_mail.create(cr, uid, {
# 							'subject': u'请审批项目%s' % project.name,
# 							'body_html': '%s' % data.comment,
# 							'auto_delete': False,
# 							}, context=context)
# 					mail_mail.send(cr, uid, [mail_id], recipient_ids=[reviewer.id], context=context)
# 				project_project.write(cr,uid,project.id,{
# 					'guimo':data.guimo,
# 					'waibao':data.waibao,
# 					'shizhenpeitao':data.shizhenpeitao,
# 					'duofanghetong':data.duofanghetong,
# 					'jianyishejibumen_id':data.jianyishejibumen_id.id,
# 					'jianyixiangmufuzeren_id':data.jianyixiangmufuzeren_id.id,
# 					'jiafang_id':data.jiafang_id.id,
# 					'state':'suozhangshenpi',
# 					},context=context)
# 		return {'type': 'ir.actions.act_window_close'}
# tijiaojingyingshi()