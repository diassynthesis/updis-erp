# -*- coding: utf-8 -*-
from osv import osv,fields

class suozhangshenpi(osv.osv_memory):
	"""suozhangshenpi"""
	_name="project.suozhangshenpi"
	_description="suozhangshenpi"
	_inherit=['project.review_abstract']
	_columns = {
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
suozhangshenpi()