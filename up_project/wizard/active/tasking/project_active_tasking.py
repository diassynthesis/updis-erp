# -*- encoding:utf-8 -*-
import datetime
from openerp import SUPERUSER_ID
from openerp.osv import fields
from openerp.osv import osv
from up_tools import tools

__author__ = 'cysnake4713'


class project_active_tasking(osv.osv):
    _log_access = True
    _name = "project.project.active.tasking"
    _inherits = {'project.project': "project_id"}
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _form_name = u'产品要求评审及任务下达记录'

    _rec_name = 'form_name'

    _track = {
        'state': {},
    }

    def workflow_signal(self, cr, uid, ids, signal):
        return self._workflow_signal(cr, uid, ids, signal)

    def _is_display_button(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            review_id = obj.director_reviewer_id
            if review_id and review_id.id == uid:
                result[obj.id] = True
            else:
                result[obj.id] = False
        return result

    def _is_project_director(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
            if hr_id and self.user_has_groups(cr, uid, "up_project.group_up_project_suozhang", context=context):
                hr_record = self.pool.get('hr.employee').browse(cr, 1, hr_id[0], context=context)
                user_department_id = hr_record.department_id.id if hr_record.department_id else "-1"
                project_department_id = obj.chenjiebumen_id.id if obj.chenjiebumen_id else None
                job_name = hr_record.job_id.name if hr_record.job_id else None
                if user_department_id == project_department_id and (job_name == u"所长" or job_name == u"分院院长"):
                    result[obj.id] = True
                else:
                    result[obj.id] = False
            else:
                result[obj.id] = False
            if obj.director_reviewer_id.id == uid:
                result[obj.id] = True

        return result

    def _is_wait_user_process(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        if context is None:
            context = {}
        current_uid = context and context.get('uid', False) or False
        for obj in self.browse(cr, uid, ids, context=context):
            result_flag = False
            if obj.state == 'open':
                if obj.create_uid and current_uid == obj.create_uid.id:
                    result_flag = True
            if obj.state == 'suozhangshenpi':
                if obj.director_reviewer_id and current_uid == obj.director_reviewer_id.id:
                    result_flag = True
            if obj.state == 'zhidingbumen':
                if self.user_has_groups(cr, uid, 'up_project.group_up_project_jingyingshi', context=context):
                    result_flag = True
            if obj.state == 'zhidingfuzeren':
                if self.user_has_groups(cr, uid, 'up_project.group_up_project_zongshishi', context=context):
                    result_flag = True
            if obj.state == 'suozhangqianzi':
                hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', current_uid)], context=context)
                if hr_id:
                    hr_record = self.pool.get('hr.employee').browse(cr, 1, hr_id[0], context=context)
                    user_department_id = hr_record.department_id.id if hr_record.department_id else "-1"
                    project_department_id = obj.chenjiebumen_id.id if obj.chenjiebumen_id else None
                    job_name = hr_record.job_id.name if hr_record.job_id else None
                    if user_department_id == project_department_id and (job_name == u"所长" or job_name == u"分院院长"):
                        result_flag = True

                    config_group_id = tools.get_id_by_external_id(cr, self.pool,
                                                                  extends_id="project_active_tasking_config_record",
                                                                  model="project.active.tasking.config")
                    config_group = self.pool.get('project.active.tasking.config').browse(cr, 1, config_group_id,
                                                                                         context=context)
                    config_group_ids = [z.id for z in config_group.cover_director_config]
                    if user_department_id == project_department_id and current_uid in config_group_ids:
                        result_flag = True

            result[obj.id] = result_flag
        return result

    def _get_director_group(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)

        director_group_id = tools.get_id_by_external_id(cr, self.pool,
                                                        extends_id="group_up_project_suozhang",
                                                        model="res.groups", context=context)
        director_group = self.pool.get("res.groups").browse(cr, 1, director_group_id, context=context)
        director_ids = [u.id for u in director_group.users]

        config_group_id = tools.get_id_by_external_id(cr, self.pool, extends_id="project_active_tasking_config_record",
                                                      model="project.active.tasking.config")
        config_group = self.pool.get('project.active.tasking.config').browse(cr, 1, config_group_id, context=context)
        config_group_ids = [z.id for z in config_group.cover_director_config]
        final_group = set(director_ids) | set(config_group_ids)
        for the_id in ids:
            result[the_id] = list(final_group)

        return result

    def _is_cover_sign(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        config_group_id = tools.get_id_by_external_id(cr, self.pool, extends_id="project_active_tasking_config_record",
                                                      model="project.active.tasking.config")
        config_group = self.pool.get('project.active.tasking.config').browse(cr, 1, config_group_id, context=context)
        config_group_ids = [z.id for z in config_group.cover_director_config]

        for obj in self.browse(cr, uid, ids, context=context):
            if obj.director_reviewer_id.id in config_group_ids:
                result[obj.id] = True
            else:
                result[obj.id] = False
        return result

    def _is_cover_sign_final(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        config_group_id = tools.get_id_by_external_id(cr, self.pool, extends_id="project_active_tasking_config_record",
                                                      model="project.active.tasking.config")
        config_group = self.pool.get('project.active.tasking.config').browse(cr, 1, config_group_id, context=context)
        config_group_ids = [z.id for z in config_group.cover_director_config]

        for obj in self.browse(cr, uid, ids, context=context):
            if obj.director_approve.id in config_group_ids:
                result[obj.id] = True
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
                                      ("end", u'表单归档'),
                                  ], "State", help='When project is created, the state is \'open\'', track_visibility='onchange'),

        "partner_address": fields.related('partner_id', "street", type="char", string='Custom Address'),


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
        "shebei": fields.selection([(u'设备满足', u'设备满足'), (u'设备不满足', u'设备不满足')], u"设备", ),  #本院是否有能力满足规定要求
        "gongqi": fields.selection([(u'工期可接受', u'工期可接受'), (u'工期太紧', u'工期太紧')], u"工期", ),  #本院是否有能力满足规定要求
        "shejifei": fields.selection([(u'设计费合理', u'设计费合理'), (u'设计费太低', u'设计费太低')], u'设计费', ),  #本院是否有能力满足规定要求


        "duofanghetong": fields.boolean(u"多方合同"),
        "jianyishejibumen_id": fields.many2one("hr.department", u"建议设计部门"),
        "jianyixiangmufuzeren_id": fields.many2many("res.users", "tasking_jianyi_manager_user_id", "tasking_user_id",
                                                    "res_user_id", u"建议项目负责人"),

        'director_reviewer_groups': fields.function(_get_director_group, type="many2many", relation="res.users",
                                                    string="Is User is The Project Director"),
        'is_cover_sign': fields.function(_is_cover_sign, type="boolean",
                                         string="Is Sign by Cover Director"),
        'is_cover_sign_final': fields.function(_is_cover_sign_final, type="boolean",
                                               string="Is Sign by Cover Director Final"),
        'director_reviewer_apply_id': fields.many2one('res.users', string=u'Review Apply By'),
        'director_reviewer_apply_image': fields.related('director_reviewer_apply_id', "sign_image", type="binary",
                                                        string=u'Review Image'),
        'director_reviewer_apply_time': fields.datetime(string="Director Reviewer Approve Time"),

        'director_approve': fields.many2one('res.users', string="Director Approve"),
        'director_approve_image': fields.related('director_approve', "sign_image", type="binary",
                                                 string=u'Review Image'),
        'director_approve_time': fields.datetime(string="Director Approve Time"),

        ##Operator Room

        "pingshenfangshi": fields.selection([(u'会议', u'会议'), (u'会签', u'会签'), (u'审批', u'审批')], u"评审方式"),
        "yinfacuoshi": fields.selection([(u'可以接受', u'可以接受'), (u'不接受', u'不接受'), (u'加班', u'加班'),
                                         (u'院内调配', u'院内调配'), (u'外协', u'外协'), (u'其它', u'其它')], u"引发措施记录"),
        "renwuyaoqiu": fields.selection([(u'见委托书', u'见委托书'), (u'见合同草案', u'见合同草案'), (u'见洽谈记录', u'见洽谈记录'),
                                         (u'见电话记录', u'见电话记录'), (u'招标文件', u'招标文件')], u"任务要求"),


        "jinyinshi_submitter_id": fields.many2one('res.users', string=u"Operator Room Submitter"),
        "jinyinshi_submitter_id_image": fields.related('jinyinshi_submitter_id', "sign_image", type="binary",
                                                       string=u'Review Image'),
        "jinyinshi_submitter_datetime": fields.datetime(string=u"Operator Room Submit Date"),

        #Engineer Room
        # 'is_tender_project': fields.related('project_id', 'shifoutoubiao', type='boolean', string=u'is Tender Project'),

        "category_name": fields.related("categories_id", 'name', type="char", string="Category Name"),

        "categories_else": fields.char(size=128, string='Else Category'),
        "tender_category": fields.selection([('business', u'商务标'), ('technology', u'技术标'), ('complex', u'综合标')],
                                            u"投标类别"),
        "zongshishi_submitter_id": fields.many2one("res.users", string=u"Zongshishi Submitter"),
        "zongshishi_submitter_id_image": fields.related('zongshishi_submitter_id', "sign_image", type="binary",
                                                        string=u'Review Image'),
        "zongshishi_submit_datetime": fields.datetime(string=u"Zongshishi Submit Date"),

        'is_wait_user_process': fields.function(_is_wait_user_process, type="boolean",
                                                string="Is User is The Project Manager"),

        'else_attachments': fields.many2many("ir.attachment", "project_tasking_attachments", "tasking_id",
                                             "attachment_id",
                                             string="Related files"),
        'reject_logs': fields.many2many("project.project.active.tasking.reject.log", "project_tasking_reject_log",
                                        "tasking_id", "log_id", string="Reject Log"),

        'is_project_director': fields.function(_is_project_director, type="boolean",
                                               string="Is User is The Project Director"),

    }

    _defaults = {
        'form_name': _form_name,
        'state': 'open',

    }


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
            self.write(cr, uid, ids, {submitter_id_field_name: uid, submit_date_field_name: datetime.datetime.now()},
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
        groups = self.pool.get('ir.model.data').get_object(cr, uid, 'up_project', 'group_up_project_jingyingshi', context=None)
        if groups:
            user_ids = [u.id for u in groups.users]
            self.message_subscribe_users(cr, uid, ids, user_ids=user_ids, context=context)
        return self._send_workflow_signal(cr, uid, ids, log_info, 'suozhangshenpi_submit')

    def draft_reject(self, cr, uid, ids, context=None):
        # self._sign_form(cr, uid, ids, 'director_reviewer_apply_id', 'director_reviewer_apply_time', is_clean=True,
        #                 context=context)
        log_info = u'所长打回申请单'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'draft_reject')


    def operator_review_accept(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'jinyinshi_submitter_id', 'jinyinshi_submitter_datetime', context=context)
        groups = self.pool.get('ir.model.data').get_object(cr, uid, 'up_project', 'group_up_project_zongshishi', context=None)
        if groups:
            user_ids = [u.id for u in groups.users]
            self.message_subscribe_users(cr, uid, ids, user_ids=user_ids, context=context)
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

    def _update_attachments(self, cr, uid, ids, context=None):
        attachment_obj = self.pool.get('ir.attachment')
        dummy, trash_dir_id = self.pool.get('ir.model.data').get_object_reference(cr, 1, 'up_project', 'dir_up_project_trash')
        dummy, actived_dir_id = self.pool.get('ir.model.data').get_object_reference(cr, 1, 'up_project', 'dir_up_project_active')
        for tasking in self.browse(cr, uid, ids, context):
            all_attachments = attachment_obj.search(cr, uid, [('res_model', '=', 'project.project'), ('res_id', '=', tasking.project_id)], context)
            saved_attachment_ids = [a.id for a in tasking.project_id.attachments] + [a.id for a in tasking.else_attachments]
            trash_attachment_ids = set(all_attachments) - set(saved_attachment_ids)
            if saved_attachment_ids: attachment_obj.write(cr, 1, saved_attachment_ids, {'parent_id': actived_dir_id}, context)
            if trash_attachment_ids: attachment_obj.write(cr, 1, list(trash_attachment_ids), {'parent_id': trash_dir_id}, context)


    def manager_review_accept(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'director_approve', 'director_approve_time', context=context)
        self._update_attachments(cr, uid, ids, context=None)
        log_info = u'负责人确认,启动项目'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'fuzeren_submit')

    def manager_reject(self, cr, uid, ids, context=None):
        self._sign_form(cr, uid, ids, 'zongshishi_submitter_id', 'zongshishi_submit_datetime', is_clean=True,
                        context=context)
        log_info = u'负责人打回申请单'
        return self._send_workflow_signal(cr, uid, ids, log_info, 'zongshishi_reject')


    def workflow_director_submit(self, cr, uid, ids, context=None):
        tasking = self.browse(cr, 1, ids[0], context=context)
        self.write(cr, 1, ids,
                   {'state': 'suozhangshenpi', 'status_code': 10102,
                    'related_user_id': tasking.director_reviewer_id.id},
                   context=context)
        return True


    def workflow_operator_room(self, cr, uid, ids, context=None):
        tasking = self.browse(cr, 1, ids[0], context=context)
        self.write(cr, 1, ids,
                   {'chenjiebumen_id': tasking.jianyishejibumen_id.id, 'state': 'zhidingbumen', 'status_code': 10103, },
                   context=context)
        return True

    def workflow_engineer_room(self, cr, uid, ids, context=None):
        tasking = self.browse(cr, 1, ids[0], context=context)
        self.write(cr, 1, ids, {'tender_category': tasking.toubiaoleibie,
                                'user_id': [(6, 0, [j.id for j in tasking.jianyixiangmufuzeren_id])],
                                'state': 'zhidingfuzeren',
                                'status_code': 10104},
                   context=context)
        return True

    def workflow_manager_room(self, cr, uid, ids, context=None):
        tasking = self.browse(cr, 1, ids[0], context=context)
        if not tasking.is_import:
            self.write(cr, 1, ids, {'state': 'end', 'status_code': 10106, 'begin_date': datetime.date.today()},
                       context=context)
        else:
            self.write(cr, 1, ids, {'state': 'end', 'status_code': 10106, },
                       context=context)

        return True

    def write(self, cr, uid, ids, vals, context=None):
        if 'attachments' in vals:
            val = ((6, 0, [attach[1] for attach in vals['attachments']],),)
            vals['attachments'] = val
        if 'else_attachments' in vals:
            val = ((6, 0, [attach[1] for attach in vals['else_attachments']],),)
            vals['else_attachments'] = val
        return super(project_active_tasking, self).write(cr, uid, ids, vals, context=context)

    def _message_get_auto_subscribe_fields(self, cr, uid, updated_fields,
                                           auto_follow_fields=['zhuguanzongshi_id', 'director_reviewer_id', 'user_id'],
                                           context=None):
        """ Returns the list of relational fields linking to res.users that should
            trigger an auto subscribe. The default list checks for the fields
            - called 'user_id'
            - linking to res.users
            - with track_visibility set
            In OpenERP V7, this is sufficent for all major addon such as opportunity,
            project, issue, recruitment, sale.
            Override this method if a custom behavior is needed about fields
            that automatically subscribe users.
        """
        user_field_lst = []
        for name, column_info in self._all_columns.items():
            if name in auto_follow_fields and name in updated_fields \
                    and column_info.column._obj == 'res.users':
                user_field_lst.append(name)
        return user_field_lst

    def reject_commit_phone(self, cr, uid, id, comment, context=None):
        if context is None:
            context = {}
        record_id = id
        tasking = self.pool.get("project.project.active.tasking").browse(cr, uid, record_id, context)
        tasking.write({
            'reject_logs': [(0, 0, {'comment': comment, 'state': tasking.state})],
        })
        if tasking.state == "suozhangshenpi":
            return tasking.draft_reject()
        if tasking.state == "zhidingbumen":
            return tasking.operator_reject()
        if tasking.state == "zhidingfuzeren":
            return tasking.engineer_reject()
        if tasking.state == "suozhangqianzi":
            return tasking.manager_reject()


class project_project_inherit(osv.osv):
    _inherit = 'project.project'
    _name = 'project.project'

    _columns = {
        'active_tasking': fields.many2one("project.project.active.tasking", string='Active Tasking Form',
                                          ondelete="cascade"),
        'active_tasking_is_wait_user_process': fields.related('active_tasking', 'is_wait_user_process', type='boolean',
                                                              string="Active Tasking Is Waiting User"),
        'active_tasking_state': fields.related('active_tasking', 'state', type='selection', selection=[
            # ("draft",u"New project"),
            ("open", u"提出申请"),
            ("suozhangshenpi", u"所长审批"),
            ("zhidingbumen", u"经营室审批"),
            ("zhidingfuzeren", u"总师室审批"),
            ("suozhangqianzi", u"负责人签字"),
            ("end", u'归档'),
        ], string='Tasking State'),
    }

    def act_active_tasking(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'project_active', 'state_active': 'project_active_tasking'})
        return self.init_form(cr, uid, ids, "project.project.active.tasking", 'active_tasking', context=context)


