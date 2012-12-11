# -*- encoding:utf-8 -*-
from osv import osv,fields
import time
from tools.translate import _

class project_upcategory(osv.osv):	
	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
				return []
		reads = self.read(cr,uid,ids,['name','parent_id'],context=context)
		res = []
		for record in reads:
			name = record['name']
			if record['parent_id']:
				name = record['parent_id'][1]+' / '+name
			res.append((record['id'],name))
		return res
	def _cate_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
		res = self.name_get(cr,uid,ids,context=context)
		return dict(res)
	_name = "project.upcategory"  
	_description = "Project Category"
	_columns = {
	"name":fields.char("Category",size=64,required=True),
	"complete_name":fields.function(_cate_name_get_fnc,type="char",string="Name"),
	'summary':fields.text("Summary"),
	'parent_id':fields.many2one('project.upcategory',"Parent Category", ondelete='set null',select=True),
	'child_ids':fields.one2many('project.upcategory','parent_id','Child Categories'),

	}
	_sql_constraints = [
		('name','unique(parent_id,name)','The name of the category must be unique')
	]
	_order = 'parent_id,name asc'
	_constraints = [
		(osv.osv._check_recursion,'Error! You cannot create recursive categories',['parent_id'])
	]
class updis_project(osv.osv):
	_inherit = "project.project"
	_columns = {
		# 基础信息
		"guimo":fields.char(u"规模",size=64),
		"waibao":fields.boolean(u"是否外包"),
		"shizhenpeitao":fields.boolean(u"市政配套"),
		"duofanghetong":fields.boolean(u"多方合同"),
		"jianyishejibumen_id":fields.many2one("hr.department",u"建议设计部门"),
		"jianyixiangmufuzeren_id":fields.many2one("res.users",u"建议项目负责人"),

		"jiafang_id":fields.many2one('res.partner', u"甲方"),
		
		# 所长审批
		"yaoqiuxingchengwenjian":fields.selection([
			("yiXingChen",u"已形成"),
			("weiXingChen",u"未形成，但已确认")],
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

		# 经营室
		"xiangmubianhao":fields.char(u"项目编号",select=True,size=128),
		"pingshenfangshi":fields.selection([(u'会议',u'会议'),(u'会签',u'会签'),(u'审批',u'审批')],u"评审方式"),
		"yinfacuoshi":fields.selection([(u'可以接受',u'可以接受'),(u'不接受',u'不接受'),(u'加班',u'加班'),
			(u'院内调配',u'院内调配'),(u'外协',u'外协'),(u'其它',u'其它')],u"引发措施记录"),
		"renwuyaoqiu":fields.selection([(u'见委托书',u'见委托书'),(u'见合同草案',u'见合同草案'),(u'见洽谈记录',u'见洽谈记录'),
			(u'见电话记录',u'见电话记录'),(u'招标文件',u'招标文件')],u"任务要求"),
		"chenjiebumen_id":fields.many2one("hr.department",u"承接部门"),

		# 总师室
		"categories_id":fields.many2many("project.upcategory","up_project_category_rel","project_id","category_id",u"项目类别"),
		"toubiaoleibie":fields.selection([(u'商务标',u'商务标'),(u'技术标',u'技术标'),(u'综合标',u'综合标')],u"投标类别"),
		"guanlijibie":fields.selection([
			(u'院级',u'院级'),
			(u'所级',u'所级')],u'项目管理级别'),
		"chenjiefuzeren_id":fields.many2one("res.users",u"承接项目负责人"),
		"zhuguanzongshi_id":fields.many2one("res.users",u"主管总师"),
		
		"state":fields.selection([
			# ("draft",u"New project"),
			("tianshenqingdan",u"任意人员填写申请单"),
			("suozhangshenpi",u"所长审批"),
			("zhidingbumen",u"经营室指定部门"),
			("zhidingfuzeren",u"总师室指定负责人"),
			("suozhangqianzi",u"所长签字"),
			("fuzerenqidong",u"启动项目"),
		],"State",readonly=True,help='When project is created, the state is \'tianshenqingdan\'')
	}
	_defaults = {
		'state': lambda *a: 'tianshenqingdan',
		# 'xiangmubianhao':lambda self, cr, uid, c=None: self.pool.get('ir.sequence').next_by_code(cr, uid, 'project.project', context=c)
	}
	def _get_action(self,cr,uid,ids,form_model_name,action_name,context=None):
		shenpi_form = self.pool.get(form_model_name)
		shenpi_form_id = False
		assert len(ids)==1
		ctx = (context or {}).copy()
		ctx['default_project_id']=ids[0]
		shenpi_form_ids=shenpi_form.search(cr,uid,[('project_id','=',ids[0]),('state','not in',('accepted','rejected'))])
		shenpi_form_id = shenpi_form_ids and shenpi_form_ids[0] or False
		return {
			'name': action_name,				
					'type':'ir.actions.act_window',
					'view_mode':'form',
					'res_model':form_model_name,
					'res_id':shenpi_form_id,
					'target':'new',
					'context':ctx
				}
	def _test_accepted(self,cr,uid,ids,form_field,*args):
		return all([(getattr(proj,form_field) and getattr(proj,form_field).state=='accepted') for proj in self.browse(cr,uid,ids)])
	def _get_form(self,cr,uid,ids,form_field,*args):
		return [getattr(proj,form_field) for proj in self.browse(cr,uid,ids) if getattr(proj,form_field)]
# class project_review_history(osv.Model):
# 	_name="project.review.history"
# 	_description="Keep every review of the project here."
# 	_columns = {
# 		'name':fields.text('Name',size=512),
# 		'submitter_id': fields.many2one('res.users', 'Submitter', readonly=True),
# 		'reviewer_id': fields.many2one('res.users', 'Reviewer', readonly=True),
# 		'fields':fields.char("Fields reviewed", size=512, readonly=True),		
# 		'result':fields.selection([
# 			('submit','Submit'),
# 			('accepted','Accepted'),
# 			('rejected','Rejected')],
# 			'Result'),
# 		'comment':fields.text('Comment')
# 	}
# 	_order="create_date desc,result"
# project_review_history()