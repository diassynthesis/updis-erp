# -*- coding: utf-8 -*-
from osv import osv, fields


class jingyingshishenpi_form(osv.Model):
    """经营室审批单"""
    _name = "project.review.jingyingshishenpi.form"
    _description = u"经营室审批"
    _inherit = ['project.review.abstract']
    _columns = {
        "xiangmubianhao": fields.char(u"项目编号", select=True, size=128, readonly=True),
        "pingshenfangshi": fields.selection([(u'会议', u'会议'), (u'会签', u'会签'), (u'审批', u'审批')], u"评审方式"),
        "yinfacuoshi": fields.selection([(u'可以接受', u'可以接受'), (u'不接受', u'不接受'), (u'加班', u'加班'),
                                         (u'院内调配', u'院内调配'), (u'外协', u'外协'), (u'其它', u'其它')], u"引发措施记录"),
        "renwuyaoqiu": fields.selection([(u'见委托书', u'见委托书'), (u'见合同草案', u'见合同草案'), (u'见洽谈记录', u'见洽谈记录'),
                                         (u'见电话记录', u'见电话记录'), (u'招标文件', u'招标文件')], u"任务要求"),
        "chenjiebumen_id": fields.many2one("hr.department", u"承接部门"),
    }
    _defaults = {
        'xiangmubianhao': lambda self, cr, uid, c=None: self.pool.get('ir.sequence').next_by_code(cr, uid,
                                                                                                  'project.project',
                                                                                                  context=c)
    }

    def jingyinshi_review_submit(self, cr, uid, ids, context=None):
        project = self.pool.get('project.project')
        current_record = self.browse(cr, uid, ids, context=None)
        if current_record and current_record[0].project_id:
            project._workflow_signal(cr, uid, [current_record[0].project_id.id], 'jingyinshi_submit')
            return True
        else:
            return False


class updis_project(osv.Model):
    _inherit = 'project.project'
    _columns = {
        'jingyingshishenpi_form_id': fields.many2one('project.review.jingyingshishenpi.form', u'经营室审批单'),
    }

    def action_jingyingshishenpi(self, cr, uid, ids, context=None):
        return self._get_action(cr, uid, ids, 'project.review.jingyingshishenpi.form', u'经营室审批单')

