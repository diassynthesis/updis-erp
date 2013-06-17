# -*- coding: utf-8 -*-
from osv import osv, fields


class suozhangqianzishenpi_form(osv.Model):
    """所长签字审批单"""
    _name = "project.review.suozhangqianzishenpi.form"
    _description = u"所长签字审批"
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

    def suozhangqianzi_review_submit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'submitter_id': uid})
        project = self.pool.get('project.project')
        suozhangshenpi = self.browse(cr, uid, ids, context=None)
        if suozhangshenpi and suozhangshenpi[0].project_id:
            project._workflow_signal(cr, uid, [suozhangshenpi[0].project_id.id], 'fuzeren_submit')
            return True
        else:
            return False


class updis_project(osv.Model):
    _inherit = 'project.project'
    _columns = {
        'suozhangqianzishenpi_form_id': fields.many2one('project.review.suozhangqianzishenpi.form', ondelete="cascade",
                                                        string=u'所长签字审批单', ),
    }

    def action_suozhangqianzishenpi(self, cr, uid, ids, context=None):
        return self._get_action(cr, uid, ids, 'project.review.suozhangqianzishenpi.form', u'所长签字审批单')

    def init_director_sign_form(self, cr, uid, ids, state, obj, object_field):
        assert len(ids) == 1
        project_id = self.browse(cr, uid, ids, context=None)

        if project_id[0] and project_id[0].suozhangshenpi_form_id:
            manager_id = project_id[0].zongshishishenpi_form_id.chenjiefuzeren_id.id
        else:
            manager_id = None

        if project_id[0] and project_id[0][object_field]:
            self.write(cr, uid, ids, {'state': state, 'user_id': manager_id})
            return project_id[0][object_field].id
        else:

            suozhangshenpi = self.pool.get(obj)
            suozhangshenpi_id = suozhangshenpi.create(cr, 1,
                                                      {'project_id': ids[0]},
                                                      None)
            self.write(cr, uid, ids, {'state': state, object_field: suozhangshenpi_id, 'user_id': manager_id})
            return suozhangshenpi_id

