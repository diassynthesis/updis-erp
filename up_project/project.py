# -*- encoding:utf-8 -*-
'''
Created on 2012-10-10

@author: Zhou Guangwen
'''
from osv import osv,fields
import time

class project_category(osv.osv):	
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
	_name = "up.project.project_category"  
	_description = "Project Category"
	_columns = {
	"name":fields.char("Category",size=64,required=True),
	"complete_name":fields.function(_cate_name_get_fnc,type="char",string="Name"),
	'summary':fields.text("Summary"),
	'parent_id':fields.many2one('up.project.project_category',"Parent Category", ondelete='set null',select=True),
	'child_ids':fields.one2many('up.project.project_category','parent_id','Child Categories'),

	}
	_sql_constraints = [
		('name','unique(parent_id,name)','The name of the category must be unique')
	]
	_order = 'parent_id,name asc'
	_constraints = [
		(osv.osv._check_recursion,'Error! You cannot create recursive categories',['parent_id'])
	]

project_category()

class project(osv.osv):
	_name = "up.project.project"
	_date_name = "date_start"
	_columns = {
		# 基础信息
		"name":fields.char("项目名称",size=256,required=True),
		"guimo":fields.char("规模",size=64),
		"waibao":fields.boolean("是否外包"),
		"shizhenpeitao":fields.boolean("市政配套"),
		"duofanghetong":fields.boolean("多方合同"),
		"jianyishejibumen":fields.many2one("hr.department","建议设计部门"),
		"jianyixiangmufuzeren":fields.many2one("res.users","建议项目负责人"),

		"jiafang_id":fields.many2one('res.partner', "甲方")
		'fuzeren_id':fields.many2one('res.users','项目负责人'),
		
		# 所长审批
		"yaoqiuxingchengwenjian":fields.selection([("已形成","已形成"),("未形成，但已确认","未形成，但已确认")],
			"顾客要求形成文件否"),		
		"zhaobiaoshu":fields.boolean("有招标书"),# 明示要求
		"weituoshu":fields.boolean("有委托书"),# 明示要求
		"xieyicaoan":fields.boolean("有协议/合同草案"),# 明示要求
		"koutouyaoqiujilu":fields.boolean("有口头要求记录"),# 明示要求
		"yinhanyaoqiu":fields.selection([("有","有（需在评审记录一栏中标明记录）"),("无","无")],"隐含要求"),
		"difangfagui":fields.selection([("有","有（需在评审记录一栏中标明记录）"),("无","无")],"地方规范或特殊法律法规"),
		"fujiayaoqiu":fields.selection([("有","有（需在评审记录一栏中标明记录）"),("无","无")],"附加要求"),
		"hetongyizhi":fields.selection([("合同/协议要求表述不一致已解决","合同/协议要求表述不一致已解决"),
			("没有出现不一致","没有出现不一致")],"与以前表述不一致的合同 / 协议要求是否解决"),	
		"ziyuan":fields.selection([('人力资源满足','人力资源满足'),('人力资源不足','人力资源不足')],'人力资源'),#本院是否有能力满足规定要求
		"shebei":fields.selection([('设备满足','设备满足'),('设备不满足','设备不满足')],"设备"),#本院是否有能力满足规定要求
		"gongqi":fields.selection([('工期可接受','工期可接受'),('工期太紧','工期太紧')],"工期"),#本院是否有能力满足规定要求
		"shejifei":fields.selection([('设计费合理','设计费合理'),('设计费太低','设计费太低')],'设计费'),#本院是否有能力满足规定要求

		# 经营室
		"xiangmubianhao":fields.char("项目编号",select=True,readonly=True,size=128),
		"pingshenfangshi":fields.selection([('会议','会议'),('会签','会签'),('审批','审批')],"评审方式"),
		"yinfacuoshi":fields.selection([('可以接受','可以接受'),('不接受','不接受'),('加班','加班'),
			('院内调配','院内调配'),('院内调配','院内调配'),('其它','其它')],"引发措施记录"),
		"renwuyaoqiu":fields.selection([('见委托书','见委托书'),('见合同草案','见合同草案'),('见洽谈记录','见洽谈记录'),
			('见电话记录','见电话记录'),('招标文件','招标文件')],"任务要求"),
		"chenjiebumen_id":fields.many2one("hr.department","承接部门"),

		# 总师室
		"category_id":fields.many2many("up.project.project_category","up_project_category_rel","project_id","category_id","项目类别"),
		"toubiaoleibie":fields.selection([('商务标','商务标'),('技术标','技术标'),('综合标','综合标')],"投标类别"),
		"guanlijibie":fields.selection([('院级','院级'),('所级','所级')],'项目管理级别'),
		"chenjiefuzeren":fields.many2one("res.users","承接项目负责人"),
		"zhuguanzongshi":fields.many2one("res.users","主管总师"),
		
		"date_start":fields.datetime("Start Date"),
		"state":fields.selection([
			("tianshenqingdan","任意人员填写申请单"),
			("suozhangshenpi","所长审批"),
			("zhidingbumen","经营室指定部门"),
			("zhidingfuzeren","总师室指定负责人"),
			("suozhangqianzi","所长签字"),
			("fuzerenqidong","启动项目"),
		],"State",readonly=True,help='When project is created, the state is \'tianshenqingdan\'')
	}
	_defaults = {
		"date_start":lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'state': lambda *a: 'tianshenqingdan',
	}
	def project_tianshenqingdan(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state': 'tianshenqingdan' })
		return True
	def project_suozhangshenpi(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state': 'suozhangshenpi' })
		return True
	def project_zhidingbumen(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state': 'zhidingbumen' })
		return True
	def project_zhidingfuzeren(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state': 'zhidingfuzeren' })
		return True
	def project_suozhangqianzi(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state': 'suozhangqianzi' })
		return True
	def project_fuzerenqidong(self, cr, uid, ids):
		self.write(cr, uid, ids, { 'state': 'fuzerenqidong' })
		return True
project()
