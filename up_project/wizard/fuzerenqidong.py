# -*- coding: utf-8 -*-
from osv import osv, fields


class fuzerenqidong_form(osv.Model):
    """项目负责人启动项目"""
    _name = "project.review.fuzerenqidong.form"
    _description = u"经营室审批"
    _inherit = ['project.review.abstract']
    _columns = {
        'shizhengxietiaoren_id': fields.many2one("res.users", u"市政协调人"),
        'gongzuodagang': fields.boolean(u'有工作大纲（保存归档）'),
        'chuangyouxiangmu': fields.boolean(u'创优项目'),
        'zhuantihuozixiang': fields.boolean(u'专题或子项（详见工作大纲）'),
        'youfenbaofang': fields.boolean(u'有分包方（详见分包协议）'),
        'project_assignment_ids': fields.many2many("project.assignment", 'fuzerenqidong_assignment_rel',
                                                   "fuzerenqidong_form_id", "assignment_id", string="Assignments"),
        #'assignment_ids':fields.related('project_id','assignment_ids',relation="project.assignment", type="one2many",string="Assignment"),
    }
    _defaults = {
    }

    def fuzerenqidong_review_submit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'submitter_id': uid})
        project = self.pool.get('project.project')
        suozhangshenpi = self.browse(cr, uid, ids, context=None)
        if suozhangshenpi and suozhangshenpi[0].project_id:
            project._workflow_signal(cr, uid, [suozhangshenpi[0].project_id.id],
                                     'draft_submit')#TODO: this state need to impl
            return True
        else:
            return False


class updis_project(osv.Model):
    _inherit = 'project.project'
    _columns = {
        'shizhengxietiaoren_id': fields.many2one("res.users", u"市政协调人"),
        'fuzerenqidong_form_id': fields.many2one('project.review.fuzerenqidong.form', u'项目负责人启动项目',ondelete="cascade",),
    }

    def action_fuzerenqidong(self, cr, uid, ids, context=None):
        return self._get_action(cr, uid, ids, 'project.review.fuzerenqidong.form', u'项目负责人启动项目')