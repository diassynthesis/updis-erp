__author__ = 'cysnake4713'
# -*- encoding:utf-8 -*-
from openerp.osv import fields
from openerp.osv import osv
from up_tools import tools


class project_active_tasking_reject_log(osv.osv):
    _name = "project.project.active.tasking.reject.log"
    _description = "Project Active Tasking Reject Log"
    _order = "create_date desc"
    _columns = {
        "state": fields.selection([
                                      # ("draft",u"New project"),
                                      ("open", u"提出申请"),
                                      ("suozhangshenpi", u"所长审批"),
                                      ("zhidingbumen", u"经营室审批"),
                                      ("zhidingfuzeren", u"总师室审批"),
                                      ("suozhangqianzi", u"负责人签字"),
                                      ("end", u'表单归档'),
                                  ], "Reject State"),
        "comment": fields.text(string="Reject Reason"),
        'create_date': fields.datetime('Created on', select=True),
    }


class project_active_tasking_reject(osv.osv_memory):
    _name = "project.project.active.tasking.reject.wizard"
    _description = "Project Active Tasking Reject"
    _columns = {
        "comment": fields.text(string="Reject Reason"),
    }

    def reject_commit(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        tasking = self.pool.get("project.project.active.tasking").browse(cr, uid, record_id, context)
        self_record = self.browse(cr, uid, ids[0], context)
        tasking.write({
            'reject_logs': [(0, 0, {'comment': self_record.comment, 'state': tasking.state})],
        })

        if tasking.state == "suozhangshenpi":
            return tasking.draft_reject()
        if tasking.state == "zhidingbumen":
            return tasking.operator_reject()
        if tasking.state == "zhidingfuzeren":
            return tasking.engineer_reject()
        if tasking.state == "suozhangqianzi":
            return tasking.manager_reject()


class project_active_tasking_engineer(osv.osv_memory):
    _name = "project.project.active.tasking.engineer"
    _description = "Project Active Tasking"

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(project_active_tasking_engineer, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        tasking_pool = self.pool.get('project.project.active.tasking')
        tasking = tasking_pool.browse(cr, uid, record_id, context=context)

        if 'categories_id' in fields:
            res['categories_id'] = tasking.categories_id.id if tasking.categories_id else None
            # if 'category_name' in fields:
        #     res['category_name'] = tasking.category_name
        if 'guanlijibie' in fields:
            res['guanlijibie'] = tasking.guanlijibie
        if 'categories_else' in fields:
            res['categories_else'] = tasking.categories_else
        if 'tender_category' in fields:
            res['tender_category'] = tasking.tender_category
        if 'zhuguanzongshi_id' in fields:
            res['zhuguanzongshi_id'] = [z.id for z in tasking.zhuguanzongshi_id]
        if 'shifoutoubiao' in fields:
            res['shifoutoubiao'] = tasking.shifoutoubiao
        if 'user_id' in fields:
            user_ids = tasking_pool.read(cr, uid, record_id, ['user_id'], context=context)
            if user_ids['user_id']:
                res['user_id'] = [u.id for u in
                                  self.pool.get('res.users').browse(cr, 1, user_ids['user_id'], context=context)]
            else:
                res['user_id'] = None
        if 'project_type' in fields:
            res['project_type'] = tasking.project_type.id if tasking.project_type else None

        return res


    _columns = {
        "shifoutoubiao": fields.boolean(string="is Tender?"),
        "project_type": fields.many2one("project.type", string="Project Type", ),
        "categories_id": fields.many2one("project.upcategory", u"项目类别"),
        "category_name": fields.related('categories_id', 'name', type='char', string="Project Category Name"),
        "guanlijibie": fields.selection([('LH200307240001', u'院级'), ('LH200307240002', u'所级')], u'项目管理级别'),
        "categories_else": fields.char(size=128, string='Else Category'),
        "tender_category": fields.selection([('business', u'商务标'), ('technology', u'技术标'), ('complex', u'综合标')],
                                            u"投标类别"),
        'user_id': fields.many2many('res.users', 'wizard_tasking_user_id', 'project_user_id', 'res_user_id',
                                    string='Project Manager'),
        "zhuguanzongshi_id": fields.many2many("res.users", "tasking_zongshi_res_user", "tasking_id", "res_user_id",
                                              u"主管总师"),

    }

    def engineer_review_accept(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        tasking = self.pool.get("project.project.active.tasking").browse(cr, uid, record_id, context)
        self_record = self.browse(cr, uid, ids[0], context)
        tasking.write({
            'categories_id': self_record.categories_id.id if self_record.categories_id else None,
            # 'category_name': self_record.category_name,
            'guanlijibie': self_record.guanlijibie,
            'user_id': [(6, 0, [u.id for u in self_record.user_id])],
            'categories_else': self_record.categories_else,
            'tender_category': self_record.tender_category,
            'zhuguanzongshi_id': [(6, 0, [z.id for z in self_record.zhuguanzongshi_id])],
            'project_type': self_record.project_type.id if self_record.project_type else None,

        })
        return tasking.engineer_review_accept()

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        ret = {'value': {}}
        if category_id:
            category = self.pool.get('project.upcategory').browse(cr, uid, category_id)
            sms_vals = {
                'category_name': category.name,
            }
            ret['value'].update(sms_vals)
        return ret

    def onchange_type_id(self, cr, uid, ids, type_id, context=None):
        ret = {'value': {}}
        sms_vals = {
            'category_name': "",
            'categories_id': None,
        }
        ret['value'].update(sms_vals)
        return ret


class project_active_tasking_operator(osv.osv_memory):
    _name = "project.project.active.tasking.operator"

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(project_active_tasking_operator, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        tasking_pool = self.pool.get('project.project.active.tasking')
        tasking = tasking_pool.browse(cr, uid, record_id, context=context)

        if 'xiangmubianhao' in fields:
            res['xiangmubianhao'] = tasking.xiangmubianhao
        if 'pingshenfangshi' in fields:
            res['pingshenfangshi'] = tasking.pingshenfangshi
        if 'yinfacuoshi' in fields:
            res['yinfacuoshi'] = tasking.yinfacuoshi
        if 'renwuyaoqiu' in fields:
            res['renwuyaoqiu'] = tasking.renwuyaoqiu
        if 'chenjiebumen_id' in fields:
            res['chenjiebumen_id'] = tasking.chenjiebumen_id.id if tasking.chenjiebumen_id else None

        return res


    _columns = {
        ##Operator Room
        "xiangmubianhao": fields.char(u"项目编号", select=True, size=128, ),
        "pingshenfangshi": fields.selection([(u'会议', u'会议'), (u'会签', u'会签'), (u'审批', u'审批')], u"评审方式"),
        "yinfacuoshi": fields.selection([(u'可以接受', u'可以接受'), (u'不接受', u'不接受'), (u'加班', u'加班'),
                                         (u'院内调配', u'院内调配'), (u'外协', u'外协'), (u'其它', u'其它')], u"引发措施记录"),
        "renwuyaoqiu": fields.selection([(u'见委托书', u'见委托书'), (u'见合同草案', u'见合同草案'), (u'见洽谈记录', u'见洽谈记录'),
                                         (u'见电话记录', u'见电话记录'), (u'招标文件', u'招标文件')], u"任务要求"),
        "chenjiebumen_id": fields.many2one("hr.department", u"承接部门"),
    }

    def operator_review_accept(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        tasking = self.pool.get("project.project.active.tasking").browse(cr, uid, record_id, context)
        self_record = self.browse(cr, uid, ids[0], context)
        tasking.write({
            'xiangmubianhao': self_record.xiangmubianhao,
            'pingshenfangshi': self_record.pingshenfangshi,
            'yinfacuoshi': self_record.yinfacuoshi,
            'renwuyaoqiu': self_record.renwuyaoqiu,
            'chenjiebumen_id': self_record.chenjiebumen_id.id if self_record.chenjiebumen_id else None,

        })
        return tasking.operator_review_accept()


class project_active_tasking_config(osv.osv):
    _name = 'project.active.tasking.config'

    _columns = {
        'name': fields.char(size=50, string='Record Name'),
        'chief_engineer_config': fields.many2many("res.users", "active_tasking_config_chief_engineer", "config_id",
                                                  "res_user_id",
                                                  string="Chief Engineer"),
    }


class project_active_tasking_config_wizard(osv.osv_memory):
    _name = 'project.active.tasking.config.wizard'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(project_active_tasking_config_wizard, self).default_get(cr, uid, fields, context=context)
        record_id = tools.get_id_by_external_id(cr, self.pool, model='project.active.tasking.config',
                                                extends_id='project_active_tasking_config_record', context=context)
        origin_obj = self.pool.get('project.active.tasking.config')

        origin = origin_obj.browse(cr, uid, record_id, context=context)

        if 'chief_engineer_config' in fields:
            res['chief_engineer_config'] = [z.id for z in origin.chief_engineer_config]

        return res

    _columns = {
        'chief_engineer_config': fields.many2many("res.users", "active_tasking_config_chief_engineer_wizard",
                                                  "config_id",
                                                  "res_user_id",
                                                  string="Chief Engineer"),
    }

    def config_accept(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = tools.get_id_by_external_id(cr, self.pool, model='project.active.tasking.config',
                                                extends_id='project_active_tasking_config_record', context=context)
        target = self.pool.get('project.active.tasking.config').browse(cr, uid, record_id, context)
        self_record = self.browse(cr, uid, ids[0], context)
        target.write({
            'chief_engineer_config': [(6, 0, [z.id for z in self_record.chief_engineer_config])],
        })
        return True
