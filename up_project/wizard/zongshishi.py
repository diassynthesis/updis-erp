# -*- coding: utf-8 -*-
from osv import osv, fields


class zongshishishenpi_form(osv.Model):
    """总师室审批单"""
    _name = "project.review.zongshishishenpi.form"
    _description = u"总师室审批"
    _inherit = ['project.review.abstract']
    _columns = {
        "categories_id": fields.many2many("project.upcategory", "up_zongshishishenpi_category_rel",
                                          "zongshishishenpi_id",
                                          "category_id", u"项目类别"),
        "toubiaoleibie": fields.selection([(u'商务标', u'商务标'), (u'技术标', u'技术标'), (u'综合标', u'综合标')], u"投标类别"),
        "guanlijibie": fields.selection([(u'院级', u'院级'), (u'所级', u'所级')], u'项目管理级别'),
        "chenjiefuzeren_id": fields.many2one("res.users", u"承接项目负责人"),
        "zhuguanzongshi_id": fields.many2one("res.users", u"主管总师"),
    }

    def zongshishi_review_submit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'submitter_id': uid})
        project = self.pool.get('project.project')
        suozhangshenpi = self.browse(cr, uid, ids, context=None)
        if suozhangshenpi and suozhangshenpi[0].project_id:
            project._workflow_signal(cr, uid, [suozhangshenpi[0].project_id.id], 'zongshishi_submit')
            return True
        else:
            return False


class updis_project(osv.Model):
    _inherit = 'project.project'
    _columns = {
        'zongshishishenpi_form_id': fields.many2one('project.review.zongshishishenpi.form', u'总师室审批单'),
    }

    def action_zongshishishenpi(self, cr, uid, ids, context=None):
        return self._get_action(cr, uid, ids, 'project.review.zongshishishenpi.form', u'总师室审批单')
