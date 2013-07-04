# -*- encoding:utf-8 -*-
from datetime import datetime
from openerp.osv import fields
from openerp.osv import osv

__author__ = 'cysnake4713'


class project_active_tasking_engineer(osv.osv_memory):
    _name = "project.project.active.tasking.engineer"

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
        if 'chenjiefuzeren_id' in fields:
            res['chenjiefuzeren_id'] = tasking.chenjiefuzeren_id.id if tasking.chenjiefuzeren_id else None
        if 'categories_else' in fields:
            res['categories_else'] = tasking.categories_else
        if 'tender_category' in fields:
            res['tender_category'] = tasking.tender_category
        if 'zhuguanzongshi_id' in fields:
            res['zhuguanzongshi_id'] = tasking.zhuguanzongshi_id.id if tasking.zhuguanzongshi_id else None
        if 'shifoutoubiao' in fields:
            res['shifoutoubiao'] = tasking.shifoutoubiao
        if 'user_id' in fields:
            res['user_id'] = tasking.user_id.id if tasking.user_id else None

        return res


    _columns = {
        "shifoutoubiao": fields.boolean(string="is Tender?"),
        "categories_id": fields.many2one("project.upcategory", u"项目类别"),
        "category_name": fields.related('categories_id', 'name', type='char', string="Project Category Name"),
        "guanlijibie": fields.selection([(u'院级', u'院级'), (u'所级', u'所级')], u'项目管理级别'),
        "chenjiefuzeren_id": fields.many2one("res.users", u"承接项目负责人"),
        "categories_else": fields.char(size=128, string='Else Category'),
        "tender_category": fields.selection([(u'商务标', u'商务标'), (u'技术标', u'技术标'), (u'综合标', u'综合标')], u"投标类别"),
        # "chenjiefuzeren_id": fields.related("project_id", "user_id", type="many2one", relation="res.users",
        #                                     string=u"承接项目负责人"),
        'user_id': fields.many2one('res.users', string='Project Manager'),
        "zhuguanzongshi_id": fields.many2one("res.users", u"主管总师"),
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
            'chenjiefuzeren_id': self_record.chenjiefuzeren_id.id if self_record.chenjiefuzeren_id else None,
            'categories_else': self_record.categories_else,
            'tender_category': self_record.tender_category,
            'zhuguanzongshi_id': self_record.zhuguanzongshi_id.id if self_record.zhuguanzongshi_id else None,

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


class project_active_tasking(osv.osv):
    _log_access = True
    _name = "project.project.active.tasking"
    _inherits = {'project.project': "project_id"}
    _form_name = u'产品要求评审及任务下达记录'

    _rec_name = 'form_name'

    def _is_display_button(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            review_id = obj.director_reviewer_id
            if review_id and review_id.id == uid:
                result[obj.id] = True
            else:
                result[obj.id] = False
        return result

    def _is_user_in_operator_group(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = self.user_has_groups(cr, uid, 'up_project.group_up_project_jingyingshi', context=context)
        return result

    def _is_user_in_engineer_group(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = self.user_has_groups(cr, uid, 'up_project.group_up_project_zongshishi', context=context)
        return result

    def _is_user_is_project_manager(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.user_id:
                result[obj.id] = (obj.user_id.id == uid)
            else:
                result[obj.id] = False
        return result


    _columns = {
        'is_display_button': fields.function(_is_display_button, type="boolean",
                                             string="Is Display Button"),
        'form_name': fields.char(size=128, string="Form Name"),
        "project_id": fields.many2one('project.project', string='Related Project', ondelete="cascade",
                                      required=True),
        "state": fields.selection([
                                      # ("draft",u"New project"),
                                      ("open", u"提出申请"),
                                      ("suozhangshenpi", u"所长审批"),
                                      ("zhidingbumen", u"经营室审批"),
                                      ("zhidingfuzeren", u"总师室审批"),
                                      ("suozhangqianzi", u"负责人签字"),
                                      ("end", u'归档'),
                                  ], "State", help='When project is created, the state is \'open\''),

        "partner_address": fields.related('partner_id', "street", type="char", string='Custom Address'),
        "customer_contact": fields.many2one('res.partner', 'Customer Contact'),
        "guimo": fields.char(u"规模", size=64),


        #Director apply
        "yaoqiuxingchengwenjian": fields.selection([
                                                       (u"已形成", u"已形成"),
                                                       (u"未形成，但已确认", u"未形成，但已确认")],
                                                   u"顾客要求形成文件否"),
        "express_requirement": fields.selection([(u"有招标书", u"有招标书"), (u"有委托书", u"有委托书"),
                                                 (u"有协议/合同草案", u"有协议/合同草案"), (u"有口头要求记录", u"有口头要求记录")],
                                                string="Express Requirement"),

        "yinhanyaoqiu": fields.selection([(u"有", u"有（需在评审记录一栏中标明记录）"), (u"无", u"无")], u"隐含要求"),
        "difangfagui": fields.selection([(u"有", u"有（需在评审记录一栏中标明记录）"), (u"无", u"无")], u"地方规范或特殊法律法规", ),
        "fujiayaoqiu": fields.selection([(u"有", u"有（需在评审记录一栏中标明记录）"), (u"无", u"无")], u"附加要求", ),
        "hetongyizhi": fields.selection([(u"合同/协议要求表述不一致已解决", u"合同/协议要求表述不一致已解决"),
                                         (u"没有出现不一致", u"没有出现不一致")], u"不一致是否解决", ),
        "ziyuan": fields.selection([(u'人力资源满足', u'人力资源满足'), (u'人力资源不足', u'人力资源不足')], u'人力资源', ),
        "shebei": fields.selection([(u'设备满足', '设备满足'), (u'设备不满足', u'设备不满足')], u"设备", ), #本院是否有能力满足规定要求
        "gongqi": fields.selection([(u'工期可接受', '工期可接受'), (u'工期太紧', u'工期太紧')], u"工期", ), #本院是否有能力满足规定要求
        "shejifei": fields.selection([(u'设计费合理', '设计费合理'), (u'设计费太低', u'设计费太低')], u'设计费', ), #本院是否有能力满足规定要求

        "waibao": fields.boolean(u"是否外包"),
        "shizhenpeitao": fields.boolean(u"市政配套"),
        "duofanghetong": fields.boolean(u"多方合同"),
        "jianyishejibumen_id": fields.many2one("hr.department", u"建议设计部门"),
        "jianyixiangmufuzeren_id": fields.many2one("res.users", u"建议项目负责人"),
        "shifoutoubiao": fields.boolean(u"是否投标项目"),
        "toubiaoleibie": fields.selection([(u'商务标', u'商务标'), (u'技术标', u'技术标'), (u'综合标', u'综合标')], u"投标类别"),

        'director_reviewer_id': fields.many2one('res.users', string=u'Review Director'),

        'director_reviewer_apply_id': fields.many2one('res.users', string=u'Review Apply By'),
        'director_reviewer_apply_time': fields.datetime(string="Director Reviewer Approve Time"),

        'director_approve': fields.many2one('res.users', string="Director Approve"),
        'director_approve_time': fields.datetime(string="Director Approve Time"),

        ##Operator Room
        "xiangmubianhao": fields.char(u"项目编号", select=True, size=128, ),
        "pingshenfangshi": fields.selection([(u'会议', u'会议'), (u'会签', u'会签'), (u'审批', u'审批')], u"评审方式"),
        "yinfacuoshi": fields.selection([(u'可以接受', u'可以接受'), (u'不接受', u'不接受'), (u'加班', u'加班'),
                                         (u'院内调配', u'院内调配'), (u'外协', u'外协'), (u'其它', u'其它')], u"引发措施记录"),
        "renwuyaoqiu": fields.selection([(u'见委托书', u'见委托书'), (u'见合同草案', u'见合同草案'), (u'见洽谈记录', u'见洽谈记录'),
                                         (u'见电话记录', u'见电话记录'), (u'招标文件', u'招标文件')], u"任务要求"),
        "chenjiebumen_id": fields.many2one("hr.department", u"承接部门"),

        "jinyinshi_submitter_id": fields.many2one('res.users', string=u"Operator Room Submitter"),
        "jinyinshi_submitter_datetime": fields.datetime(string=u"Operator Room Submit Date"),
        'is_user_in_operator_group': fields.function(_is_user_in_operator_group, type="boolean",
                                                     string="Is User In Operator Room"),

        #Engineer Room
        # 'is_tender_project': fields.related('project_id', 'shifoutoubiao', type='boolean', string=u'is Tender Project'),
        "categories_id": fields.many2one("project.upcategory", u"项目类别"),
        "category_name": fields.related("categories_id", 'name', type="char", string="Category Name"),
        "guanlijibie": fields.selection([(u'院级', u'院级'), (u'所级', u'所级')], u'项目管理级别'),
        "chenjiefuzeren_id": fields.many2one("res.users", u"承接项目负责人"),
        "categories_else": fields.char(size=128, string='Else Category'),
        "tender_category": fields.selection([(u'商务标', u'商务标'), (u'技术标', u'技术标'), (u'综合标', u'综合标')], u"投标类别"),
        # "chenjiefuzeren_id": fields.related("project_id", "user_id", type="many2one", relation="res.users",
        #                                     string=u"承接项目负责人"),
        "zhuguanzongshi_id": fields.many2one("res.users", u"主管总师"),
        "zongshishi_submitter_id": fields.many2one("res.users", string=u"Zongshishi Submitter"),
        "zongshishi_submit_datetime": fields.datetime(string=u"Zongshishi Submit Date"),
        'is_user_in_engineer_group': fields.function(_is_user_in_engineer_group, type="boolean",
                                                     string="Is User In Engineer Room"),

        'is_user_is_project_manager': fields.function(_is_user_is_project_manager, type="boolean",
                                                      string="Is User is The Project Manager"),
    }

    _defaults = {
        'form_name': _form_name,
        'state': 'open',

    }
    _sql_constraints = [('xiangmubianhao_uniq', 'unique(xiangmubianhao)', 'xiangmubianhao must be unique !')]

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        ret = {'value': {}}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            state_name = partner.state_id and partner.state_id.name or ""
            country_name = partner.country_id and partner.country_id.name or ""
            city = partner.city and partner.city or ""
            street = partner.street and partner.street or ""
            street2 = partner.street2 and partner.street2 or ""
            if country_name == "China":
                country_name = u"中国"

            sms_vals = {
                'partner_address': "%s" % (street)
            }
            ret['value'].update(sms_vals)
        else:
            sms_vals = {
                'partner_address': ""
            }
            ret['value'].update(sms_vals)
        return ret

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        ret = {'value': {}}
        if category_id:
            category = self.pool.get('project.upcategory').browse(cr, uid, category_id)
            sms_vals = {
                'category_name': category.name,
            }
            ret['value'].update(sms_vals)
        return ret

    def _sign_form(self, cr, uid, ids, submitter_id_field_name, submit_date_field_name, is_clean=False, context=None):
        if not is_clean:
            self.write(cr, uid, ids, {submitter_id_field_name: uid, submit_date_field_name: datetime.now()},
                       context=context)
        else:
            self.write(cr, uid, ids, {submitter_id_field_name: None, submit_date_field_name: None},
                       context=context)

    def _send_workflow_signal(self, cr, uid, ids, log_info, signal, context=None):
        project = self.pool.get('project.project')
        suozhangshenpi = self.browse(cr, uid, ids, context=None)
        if suozhangshenpi and suozhangshenpi[0].project_id:
            project.write(cr, uid, suozhangshenpi[0].project_id.id,
                          {'project_logs': [(0, 0, {'project_id': suozhangshenpi[0].project_id.id,
                                                    'log_user': uid,
                                                    'log_info': log_info})]})
            self._workflow_signal(cr, uid, ids, signal)
            return True
        else:
            return False


    def director_review_submit(self, cr, uid, ids, context=None):
        suozhangshenpi = self.browse(cr, uid, ids, context=None)
        log_info = u'提交所长审批请求到--> %s' % suozhangshenpi[0].director_reviewer_id.name
        return self._send_workflow_signal(cr, uid, ids, log_info, 'draft_submit')

    def director_review_accept(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'director_reviewer_apply_id', 'director_reviewer_apply_time', context=context)
        log_info = u'所长审批通过,提交请求到经营室'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'suozhangshenpi_submit')

    def draft_reject(self, cr, uid, ids, context=None):
        # self._sign_form(cr, uid, ids, 'director_reviewer_apply_id', 'director_reviewer_apply_time', is_clean=True,
        #                 context=context)
        log_info = u'所长打回申请单'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'draft_reject')


    def operator_review_accept(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'jinyinshi_submitter_id', 'jinyinshi_submitter_datetime', context=context)
        log_info = u'经营室审批通过,提交申请到总师室'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'jingyinshi_submit')

    def operator_reject(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'director_reviewer_apply_id', 'director_reviewer_apply_time', is_clean=True,
                        context=context)
        log_info = u'经营室打回申请单'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'suozhangshenpi_reject')


    def engineer_review_accept(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'zongshishi_submitter_id', 'zongshishi_submit_datetime', context=context)
        log_info = u'总师室审批通过,提交请求到负责人'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'zongshishi_submit')

    def engineer_reject(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'jinyinshi_submitter_id', 'jinyinshi_submitter_datetime', is_clean=True,
                        context=context)
        log_info = u'总师室打回申请单'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'jingyinshi_reject')


    def manager_review_accept(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'director_approve', 'director_approve_time', context=context)
        log_info = u'负责人确认,启动项目'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'fuzeren_submit')

    def manager_reject(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'zongshishi_submitter_id', 'zongshishi_submit_datetime', is_clean=True,
                        context=context)
        log_info = u'负责人打回申请单'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'zongshishi_reject')


    def workflow_operator_room(self, cr, uid, ids, context=None):
        tasking = self.browse(cr, 1, ids[0], context=context)
        self.write(cr, 1, ids, {'chenjiebumen_id': tasking.jianyishejibumen_id.id, 'state': 'zhidingbumen'},
                   context=context)
        return True

    def workflow_engineer_room(self, cr, uid, ids, context=None):
        tasking = self.browse(cr, 1, ids[0], context=context)
        self.write(cr, 1, ids, {'tender_category': tasking.toubiaoleibie,
                                'user_id': tasking.jianyixiangmufuzeren_id.id, 'state': 'zhidingfuzeren'},
                   context=context)
        return True


    def action_operator_wizard(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()
        ctx['default_project_id'] = ids[0]


class project_project_inherit(osv.osv):
    _inherit = 'project.project'
    _name = 'project.project'

    _columns = {
        'active_tasking': fields.many2one("project.project.active.tasking", string='Active Tasking Form',
                                          ondelete="cascade"),
    }

    def act_active_tasking(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'project_active', 'state_active': 'project_active_tasking'})
        return self.init_form(cr, uid, ids, "project.project.active.tasking", 'active_tasking', context=context)


