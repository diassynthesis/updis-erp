# -*- encoding:utf-8 -*-
'''
Created on 2012-10-10

@author: Zhou Guangwen
'''
from osv import osv,fields

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
	'summary':fields.text("Summary")
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
		"name":fields.char("Name",size=256),
		'fuzeren':fields.many2one('res.users','项目负责人'),
		"guimo":fields.char("Guimo",size=64),
		"date_start":fields.datetime("Start Date"),
		"state":fields.selection([
			("cehua","策划"),
			("shuru","输入"),
			("pingshen","评审"),
			("yanzheng","验证"),
			("queren","确认"),
			("shuchu","输出"),
			("genggai","更改"),
			("fuwu","服务"),
		])
	}
	_defaults = {
		"date_start":lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': lambda *a: 'cehua',
	}
project()
