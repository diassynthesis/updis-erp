# -*- coding: utf-8 -*-
from osv import osv,fields
from tools.translate import _
from . import common
import netsvc


class suozhangqianzishenpi_form(osv.Model):
	"""所长签字审批单"""
	_name="project.review.suozhangqianzishenpi.form"
	_description=u"所长签字审批"
	_inherit=['project.review.abstract']
	_columns={
		"xiangmubianhao":fields.char(u"项目编号",select=True,size=128,readonly=True),
		"pingshenfangshi":fields.selection([(u'会议',u'会议'),(u'会签',u'会签'),(u'审批',u'审批')],u"评审方式"),
		"yinfacuoshi":fields.selection([(u'可以接受',u'可以接受'),(u'不接受',u'不接受'),(u'加班',u'加班'),
			(u'院内调配',u'院内调配'),(u'外协',u'外协'),(u'其它',u'其它')],u"引发措施记录"),
		"renwuyaoqiu":fields.selection([(u'见委托书',u'见委托书'),(u'见合同草案',u'见合同草案'),(u'见洽谈记录',u'见洽谈记录'),
			(u'见电话记录',u'见电话记录'),(u'招标文件',u'招标文件')],u"任务要求"),
		"chenjiebumen_id":fields.many2one("hr.department",u"承接部门"),	
	}
	_defaults = {
		'xiangmubianhao':lambda self, cr, uid, c=None: self.pool.get('ir.sequence').next_by_code(cr, uid, 'project.project', context=c)
	}
	def update_project_suozhangqianzishenpi_form(self,cr,uid,ids,*args):		
		return self._update_project_form(cr,uid,ids,'suozhangqianzishenpi_form_id')
	def trg_project_write(self,cr,uid,ids,context=None):
		wkf_service = netsvc.LocalService('workflow')
		for frm in self.browse(cr,uid,ids,context=context):
			wkf_service.trg_write(uid,'project.project',frm.project_id.id,cr)
		return True
class updis_project(osv.Model):
	_inherit='project.project'	
	_columns={
		'suozhangqianzishenpi_form_id':fields.many2one('project.review.suozhangqianzishenpi.form',u'所长签字审批单'),
	}
	def action_suozhangqianzishenpi(self, cr, uid, ids, context=None):
		return self._get_action(cr,uid,ids,'project.review.suozhangqianzishenpi.form',u'所长签字审批单')
	def test_suozhangqianzishenpi_accepted(self, cr, uid, ids, *args):
		return self._test_accepted(cr,uid,ids,'suozhangqianzishenpi_form_id',*args)
	def suozhangqianzishenpi_get(self, cr, uid, ids, *args):
		return self._get_form(cr,uid,ids,'suozhangqianzishenpi_form_id',*args)
