# -*- coding: utf-8 -*-
from osv import osv,fields
from tools.translate import _
from . import common

class jingyingshi_form(osv.Model):
	"""经营室审批单"""
	_name="project.review.jingyingshi.form"
	_description=u"经营室审批"
	_inherit=['project.review.abstract']
	_columns={
		"xiangmubianhao":fields.char(u"项目编号",select=True,size=128),
		"pingshenfangshi":fields.selection([(u'会议',u'会议'),(u'会签',u'会签'),(u'审批',u'审批')],u"评审方式"),
		"yinfacuoshi":fields.selection([(u'可以接受',u'可以接受'),(u'不接受',u'不接受'),(u'加班',u'加班'),
			(u'院内调配',u'院内调配'),(u'外协',u'外协'),(u'其它',u'其它')],u"引发措施记录"),
		"renwuyaoqiu":fields.selection([(u'见委托书',u'见委托书'),(u'见合同草案',u'见合同草案'),(u'见洽谈记录',u'见洽谈记录'),
			(u'见电话记录',u'见电话记录'),(u'招标文件',u'招标文件')],u"任务要求"),
		"chenjiebumen_id":fields.many2one("hr.department",u"承接部门"),	
	}
	def update_project_jingyingshi_form(self,cr,uid,ids,*args):
		for f in self.browse(cr,uid,ids):
			f.project_id.jingyingshi_form_id = f
		return True
class updis_project(osv.Model):
	_inherit='project.project'	
	_columns={
		'jingyingshi_form_id':fields.many2one('project.review.jingyingshi.form',u'经营室审批单'),
	}
	def action_jingyingshi(self, cr, uid, ids, context=None):
		jingyingshi_form = self.pool.get('project.review.jingyingshi.form')
		jingyingshi_form_id = False
		assert len(ids)==1
		ctx = (context or {}).copy()
		ctx['default_project_id']=ids[0]
		jingyingshi_form_ids=jingyingshi_form.search(cr,uid,[('project_id','=',ids[0]),('state','not in',('accepted','rejected'))])
		jingyingshi_form_id = jingyingshi_form_ids and jingyingshi_form_ids[0] or False
		return {
			'name': _('经营室审批'),				
					'type':'ir.actions.act_window',
					'view_mode':'form',
					'res_model':'project.review.jingyingshi.form',
					'res_id':jingyingshi_form_id,
					'target':'new',
					'context':ctx
				}
	def test_suozhangform_submitted(self, cr, uid, ids, *args):
		return all([jingyingshi_form_id.state=='submitted' for proj in self.browse(cr,uid,ids) if proj.jingyingshi_form_id])
	def suozhangform_get(self, cr, uid, ids, *args):
		return [jingyingshi_form_id.id for proj in self.browse(cr,uid,ids) if proj.jingyingshi_form_id]