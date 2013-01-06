# -*- coding: utf-8 -*-
from osv import osv,fields
from tools.translate import _
from . import common

class zongshishishenpi_form(osv.Model):
	"""总师室审批单"""
	_name="project.review.zongshishishenpi.form"
	_description=u"总师室审批"
	_inherit=['project.review.abstract']
	_columns={
		"categories_id":fields.many2many("project.upcategory","up_zongshishishenpi_category_rel","zongshishishenpi_id","category_id",u"项目类别"),
		"toubiaoleibie":fields.selection([(u'商务标',u'商务标'),(u'技术标',u'技术标'),(u'综合标',u'综合标')],u"投标类别"),
		"guanlijibie":fields.selection([(u'院级',u'院级'),(u'所级',u'所级')],u'项目管理级别'),
		"chenjiefuzeren_id":fields.many2one("res.users",u"承接项目负责人"),
		"zhuguanzongshi_id":fields.many2one("res.users",u"主管总师"),
	}
	def update_project_zongshishishenpi_form(self,cr,uid,ids,*args):			
		return self._update_project_form(cr,uid,ids,'zongshishishenpi_form_id')
	def update_project_categories(self,cr,uid,ids,context=None):
		project = self.pool.get("project.project")
		for frm in self.browse(cr,uid,ids,context=context):
			cat_ids = [cat.id for cat in frm.categories_id]
			project.write(cr,uid,frm.project_id.id,{
				'categories_id':[(6,0,cat_ids)],
				})
		return True
class updis_project(osv.Model):
	_inherit='project.project'	
	_columns={
		'zongshishishenpi_form_id':fields.many2one('project.review.zongshishishenpi.form',u'总师室审批单'),
	}
	def action_zongshishishenpi(self, cr, uid, ids, context=None):
		return self._get_action(cr,uid,ids,'project.review.zongshishishenpi.form',u'总师室审批单')
	def test_zongshishishenpi_accepted(self, cr, uid, ids, *args):
		return self._test_accepted(cr,uid,ids,'zongshishishenpi_form_id',*args)
	def zongshishishenpi_get(self, cr, uid, ids, *args):
		return self._get_form(cr,uid,ids,'zongshishishenpi_form_id',*args)