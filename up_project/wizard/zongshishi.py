# -*- coding: utf-8 -*-
from osv import osv, fields


class zongshishishenpi_form(osv.Model):
    """总师室审批单"""
    _name = "project.review.zongshishishenpi.form"
    _description = u"总师室审批"
    _inherit = ['project.review.abstract']
    _columns = {
        'is_tender_project': fields.related('project_id', 'shifoutoubiao', type='boolean', string=u'is Tender Project'),
        "categories_id": fields.many2one("project.upcategory", u"项目类别"),
        "category_name": fields.char(size=128, string="Category Name"),
        "guanlijibie": fields.selection([(u'院级', u'院级'), (u'所级', u'所级')], u'项目管理级别'),
        "chenjiefuzeren_id": fields.many2one("res.users", u"承接项目负责人"),
        "categories_else": fields.char(size=128, string='Else Category'),
        # "chenjiefuzeren_id": fields.related("project_id", "user_id", type="many2one", relation="res.users",
        #                                     string=u"承接项目负责人"),
        "zhuguanzongshi_id": fields.many2one("res.users", u"主管总师"),
    }

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        ret = {'value': {}}
        if category_id:
            category = self.pool.get('project.upcategory').browse(cr, uid, category_id)
            sms_vals = {
                'category_name': category.name,
            }
            ret['value'].update(sms_vals)
        return ret

    def zongshishi_review_submit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'submitter_id': uid})
        project = self.pool.get('project.project')
        suozhangshenpi = self.browse(cr, uid, ids, context=None)
        if suozhangshenpi and suozhangshenpi[0].project_id:
            project.write(cr, uid, suozhangshenpi[0].project_id.id,
                          {'project_logs': [(0, 0, {'project_id': suozhangshenpi[0].project_id.id,
                                                    'log_user': uid,
                                                    'log_info': u'总师室审批通过,提交请求到所长'})]})
            project._workflow_signal(cr, uid, [suozhangshenpi[0].project_id.id], 'zongshishi_submit')
            return True
        else:
            return False


class updis_project(osv.Model):
    _inherit = 'project.project'
    _columns = {
        'zongshishishenpi_form_id': fields.many2one('project.review.zongshishishenpi.form', u'总师室审批单',
                                                    ondelete="cascade", ),

        "categories_id": fields.related('zongshishishenpi_form_id', 'categories_id', type="many2one",
                                        relation='project.upcategory', string=u"项目类别"),
        "categories_else": fields.related('zongshishishenpi_form_id', 'categories_else', type='char',
                                          string='Else Category'),
        "category_name": fields.related("categories_id", "name", type="char", string="Category Name"),
        "guanlijibie": fields.related('zongshishishenpi_form_id', 'guanlijibie', type="char", string=u"项目管理级别"),
        # "chenjiefuzeren_id": fields.related('zongshishishenpi_form_id', 'chenjiefuzeren_id', type="many2one",
        #                                     relation="hr.employee", string=u"承接项目负责人"),
        "zhuguanzongshi_id": fields.related('zongshishishenpi_form_id', 'zhuguanzongshi_id', type="many2one",
                                            relation="res.users", string=u"主管总师"),
        "zongshishi_submitter_id": fields.related('zongshishishenpi_form_id', 'submitter_id', type="many2one",
                                                  relation="res.users",
                                                  string=u"Zongshishi Submitter"),

    }

    def action_zongshishishenpi(self, cr, uid, ids, context=None):
        return self._get_action(cr, uid, ids, 'project.review.zongshishishenpi.form', u'总师室审批单')

    def init_zongshishi_form(self, cr, uid, ids, state, obj, object_field):
        assert len(ids) == 1
        project_id = self.browse(cr, uid, ids, context=None)
        if project_id[0] and project_id[0].suozhangshenpi_form_id:
            user_id = project_id[0].suozhangshenpi_form_id.jianyixiangmufuzeren_id.id
        else:
            user_id = None

        if project_id[0] and project_id[0][object_field]:
            suozhangshenpi = self.pool.get(obj)
            suozhangshenpi_id = suozhangshenpi.write(cr, 1, project_id[0].zongshishishenpi_form_id.id,
                                                     {'chenjiefuzeren_id': user_id})
            self.write(cr, uid, ids, {'state': state})
            return project_id[0][object_field].id
        else:

            suozhangshenpi = self.pool.get(obj)
            suozhangshenpi_id = suozhangshenpi.create(cr, 1,
                                                      {'project_id': ids[0], 'chenjiefuzeren_id': user_id},
                                                      None)
            self.write(cr, uid, ids, {'state': state, object_field: suozhangshenpi_id})
            return suozhangshenpi_id

    def jingyinshi_reject(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,
                   {'project_logs': [(0, 0, {'project_id': ids,
                                             'log_user': uid,
                                             'log_info': u'总师室打回申请单'})]})
        self._workflow_signal(cr, uid, ids, 'jingyinshi_reject')
        return True