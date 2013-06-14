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
    }

    def jingyinshi_review_submit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'submitter_id': uid})
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

        "xiangmubianhao": fields.related('jingyingshishenpi_form_id', 'xiangmubianhao', type="char",
                                         string=u"项目编号"),
        "pingshenfangshi": fields.related('jingyingshishenpi_form_id', 'pingshenfangshi', type="char",
                                          string=u"评审方式"),
        "yinfacuoshi": fields.related('jingyingshishenpi_form_id', 'yinfacuoshi', type="char",
                                      string=u"引发措施记录"),
        "renwuyaoqiu": fields.related('jingyingshishenpi_form_id', 'renwuyaoqiu', type="char",
                                      string=u"任务要求"),
        "chenjiebumen_id": fields.related('jingyingshishenpi_form_id', 'chenjiebumen_id', type="many2one",
                                          relation="hr.department",
                                          string=u"承接部门"),
        "jinyinshi_submitter_id": fields.related('jingyingshishenpi_form_id', 'submitter_id', type="many2one",
                                          relation="res.users",
                                          string=u"Submitter"),
    }

    def action_jingyingshishenpi(self, cr, uid, ids, context=None):
        return self._get_action(cr, uid, ids, 'project.review.jingyingshishenpi.form', u'经营室审批单')

    def init_jinyinshi_form(self, cr, uid, ids, state, obj, object_field):
        assert len(ids) == 1
        project_id = self.browse(cr, uid, ids, context=None)
        if project_id[0] and project_id[0][object_field]:
            self.write(cr, uid, ids, {'state': state})
            return project_id[0][object_field].id
        else:
            project_num = self.pool.get('ir.sequence').next_by_code(cr, uid, 'project.project')
            if project_id[0] and project_id[0].suozhangshenpi_form_id:
                department = project_id[0].suozhangshenpi_form_id.jianyishejibumen_id
            else:
                department = None
            suozhangshenpi = self.pool.get(obj)
            suozhangshenpi_id = suozhangshenpi.create(cr, 1,
                                                      {'project_id': ids[0], 'xiangmubianhao': project_num,
                                                       'chenjiebumen_id': department.id},
                                                      None)
            self.write(cr, uid, ids, {'state': state, object_field: suozhangshenpi_id})
            return suozhangshenpi_id