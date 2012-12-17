# -*- coding: utf-8 -*-
from osv import osv,fields
from tools.translate import _
from . import common

class fuzerenqidong_form(osv.Model):
	"""经营室审批单"""
	_name="project.review.fuzerenqidong.form"
	_description=u"经营室审批"
	_inherit=['project.review.abstract']
	_columns={
		'duty_id':fields.many2one('project.duty','Duty'),
		'profession_id':fields.many2one('project.profession','Profession'),
		'project_id':fields.many2one('project.project','Project'),
		'state':fields.selection([
			(u'项目负责人创建',u'项目负责人创建'),
			(u'设计部门负责人签字',u'设计部门负责人签字'),
			(u'配合部门负责人签字',u'配合部门负责人签字')],'State',readonly=True)
	}
	_defaults={
		'state':u'项目负责人创建',
	}
	def update_project_fuzerenqidong_form(self,cr,uid,ids,*args):		
		return self._update_project_form(cr,uid,ids,'fuzerenqidong_form_id')
class updis_project(osv.Model):
	_inherit='project.project'	
	_columns={
		'fuzerenqidong_form_id':fields.many2one('project.review.fuzerenqidong.form',u'经营室审批单'),
	}
	def action_fuzerenqidong(self, cr, uid, ids, context=None):
		return self._get_action(cr,uid,ids,'project.review.fuzerenqidong.form',u'经营室审批单')
	def test_fuzerenqidong_accepted(self, cr, uid, ids, *args):
		return self._test_accepted(cr,uid,ids,'fuzerenqidong_form_id',*args)
	def fuzerenqidong_get(self, cr, uid, ids, *args):
		return self._get_form(cr,uid,ids,'fuzerenqidong_form_id',*args)
