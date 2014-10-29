# -*- encoding:utf-8 -*-
import datetime
from operator import itemgetter
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.osv.orm import browse_record, browse_null
from up_tools import tools


class project_project_wizard(osv.osv_memory):
    _name = "project.project.wizard"
    _description = "Project Wizard"


    def default_get(self, cr, uid, fields, context=None):
        res = super(project_project_wizard, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        project_pool = self.pool.get('project.project')
        project = project_pool.browse(cr, uid, record_id, context=context)

        if 'user_id' in fields:
            res['user_id'] = [u.id for u in project.user_id]
        if 'name' in fields:
            res['name'] = project.name
        if 'xiangmubianhao' in fields:
            res['xiangmubianhao'] = project.xiangmubianhao
        if 'country_id' in fields:
            res['country_id'] = project.country_id.id if project.country_id else None
        if 'state_id' in fields:
            res['state_id'] = project.state_id.id if project.state_id else None
        if 'city' in fields:
            res['city'] = project.city
        if 'city_type' in fields:
            res['city_type'] = project.city_type
        if 'partner_type' in fields:
            res['partner_type'] = project.partner_type
        if 'partner_id' in fields:
            res['partner_id'] = project.partner_id.id if project.partner_id else None
        if 'customer_contact' in fields:
            res['customer_contact'] = project.customer_contact.id if project.customer_contact else None
        if 'project_type' in fields:
            res['project_type'] = project.project_type.id if project.project_type else None
        if 'categories_id' in fields:
            res['categories_id'] = project.categories_id.id if project.categories_id else None
        if 'shifoutoubiao' in fields:
            res['shifoutoubiao'] = project.shifoutoubiao
        if 'toubiaoleibie' in fields:
            res['toubiaoleibie'] = project.toubiaoleibie
        if 'zhuguanzongshi_id' in fields:
            res['zhuguanzongshi_id'] = [z.id for z in project.zhuguanzongshi_id]
        if 'chenjiebumen_id' in fields:
            res['chenjiebumen_id'] = project.chenjiebumen_id.id if project.chenjiebumen_id else None
        if 'guanlijibie' in fields:
            res['guanlijibie'] = project.guanlijibie
        if 'guimo' in fields:
            res['guimo'] = project.guimo
        if 'waibao' in fields:
            res['waibao'] = project.waibao
        if 'shizhenpeitao' in fields:
            res['shizhenpeitao'] = project.shizhenpeitao

        return res

    _columns = {
        "user_id": fields.many2many('res.users', 'wizard_project_user_id_res_user', 'project_user_id', 'res_user_id',
                                    string="Project Manager"),
        "name": fields.char(size=256, string="Project Name"),
        "xiangmubianhao": fields.char(size=256, string="Project Num"),
        'country_id': fields.many2one('res.country', 'Country'),
        "state_id": fields.many2one('res.country.state', 'State', ),
        "city": fields.char("City", size=128),
        'city_type': fields.selection(
            [('CC200511210001', u'直辖市'), ('CC200511210002', u'省会城市'), ('CC200511210003', u'地级市'),
             ('CC200511210004', u'县级市'), ('CC200511210005', u'其它'), ('plan_city', u'计划单列市')], string="City Type"),
        'partner_type': fields.selection([("WT200508180001", u"深圳规划局"),
                                          ("WT200508180002", u"深圳市其他"),
                                          ("WT200508180003", u"市外"),
                                          ("WT200509020001", u"其它"), ], string="Partner Type"),
        "partner_id": fields.many2one('res.partner', 'Customer'),
        "customer_contact": fields.many2one('res.partner', 'Customer Contact'),
        "project_type": fields.many2one("project.type", string="Project Type", ),
        "categories_id": fields.many2one("project.upcategory", u"项目类别"),
        "shifoutoubiao": fields.boolean("Is Tender"),
        "toubiaoleibie": fields.selection([('business', u'商务标'), ('technology', u'技术标'), ('complex', u'综合标')],
                                          "Tender Type"),
        "zhuguanzongshi_id": fields.many2many("res.users", "wizard_project_zhuangguan_res_user", "project_id",
                                              "res_user_id",
                                              u"主管总师"),
        "chenjiebumen_id": fields.many2one("hr.department", u"In Charge Department"),
        "guanlijibie": fields.selection([('LH200307240001', u'院级'), ('LH200307240002', u'所级')], u'Project Level'),
        "guimo": fields.char(u"Scale", size=64),
        "waibao": fields.boolean("Is Outsourcing"),
        "shizhenpeitao": fields.boolean("Is City"),
    }

    def project_admin_change_accept(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        project = self.pool.get("project.project").browse(cr, uid, record_id, context)
        self_record = self.browse(cr, uid, ids[0], context)
        tasking_obj = self.pool['project.project.active.tasking']
        tasking_id = tasking_obj.search(cr, uid, [('project_id', '=', record_id)], context=context)
        project.write({
            'user_id': [(6, 0, [r.id for r in self_record.user_id])],
            'name': self_record.name,
            'xiangmubianhao': self_record.xiangmubianhao,
            'country_id': self_record.country_id.id if self_record.country_id.id else None,
            'state_id': self_record.state_id.id if self_record.state_id.id else None,
            'city': self_record.city,
            'city_type': self_record.city_type,
            'partner_type': self_record.partner_type,
            'partner_id': self_record.partner_id.id if self_record.partner_id.id else None,
            'customer_contact': self_record.customer_contact.id if self_record.customer_contact.id else None,
            'project_type': self_record.project_type.id if self_record.project_type.id else None,
            'categories_id': self_record.categories_id.id if self_record.categories_id.id else None,
            'shifoutoubiao': self_record.shifoutoubiao,
            'toubiaoleibie': self_record.toubiaoleibie,
            'zhuguanzongshi_id': [(6, 0, [z.id for z in self_record.zhuguanzongshi_id])],
            'chenjiebumen_id': self_record.chenjiebumen_id.id if self_record.chenjiebumen_id.id else None,
            'guanlijibie': self_record.guanlijibie,
            'guimo': self_record.guimo,
            'waibao': self_record.waibao,
            'shizhenpeitao': self_record.shizhenpeitao,
        })
        tasking_obj.write(cr, uid, tasking_id, {'tender_category': self_record.toubiaoleibie, }, context=context)

        return True

    def onchange_country_id(self, cr, uid, ids, type_id, context=None):
        ret = {'value': {}}
        sms_vals = {
            'state_id': None,
        }
        ret['value'].update(sms_vals)
        return ret


class project_type(osv.osv):
    _name = "project.type"
    _description = "Project Type"
    _columns = {
        'name': fields.char(size=128, string="Project Type Name"),
    }


class project_upcategory(osv.osv):
    _name = "project.upcategory"
    _description = "Project Category"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def _cate_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _get_sequence(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        SQL = "SELECT count(*) FROM project_project WHERE categories_id = %d"
        for obj in self.browse(cr, uid, ids, context=context):
            cr.execute(SQL % obj.id)
            result[obj.id] = map(itemgetter(0), cr.fetchall())[0]
        return result

    _columns = {
        "name": fields.char("Category", size=64, required=True),
        "complete_name": fields.function(_cate_name_get_fnc, type="char", string="Name"),
        "project_type": fields.many2one("project.type", string="Project Type", ),
        'summary': fields.text("Summary"),
        'parent_id': fields.many2one('project.upcategory', "Parent Category", ondelete='set null', select=True),
        'child_ids': fields.one2many('project.upcategory', 'parent_id', 'Child Categories'),
        'index': fields.function(_get_sequence, type='integer', store=True, string='Sequence'),

    }
    _sql_constraints = [
        ('name', 'unique(parent_id,name)', 'The name of the category must be unique')
    ]
    _order = 'index desc'
    _constraints = [
        (osv.osv._check_recursion, 'Error! You cannot create recursive categories', ['parent_id'])
    ]


class project_log(osv.osv):
    _log_access = True
    _name = "project.log"
    _order = "log_date desc"
    _columns = {
        'log_date': fields.datetime('Created on'),
        'project_id': fields.many2one('project.project', "related Project", ondelete="cascade"),
        'log_user': fields.many2one('res.users', 'Log User'),
        'log_info': fields.char(size=256, string="Log Info"),
    }

    _defaults = {
        'log_date': lambda *a: datetime.datetime.now()
    }


class updis_project(osv.osv):
    _log_access = True
    _inherit = "project.project"
    _name = "project.project"
    _order = "id desc"

    _track = {
        'user_id': {},
        'zhuguanzongshi_id': {},
        'state': {},
    }

    def _is_project_creater(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            review_id = obj.create_uid.id
            if review_id == context.get('uid', 1):
                result[obj.id] = True
            else:
                result[obj.id] = False

        return result

    def _is_project_created(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = True
        return result

    def _is_user_in_operator_group(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = self.user_has_groups(cr, context.get('uid', 1), 'up_project.group_up_project_jingyingshi', context=context)
        return result

    def _is_user_in_engineer_group(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = self.user_has_groups(cr, context.get('uid', 1), 'up_project.group_up_project_zongshishi', context=context)
        return result

    def _is_chief(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = self.user_has_groups(cr, context.get('uid', 1), 'up_project.group_up_project_chief', context=context)
        return result

    def _is_admin(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = self.user_has_groups(cr, context.get('uid', 1), 'up_project.group_up_project_admin', context=context)
        return result

    def _is_user_is_project_manager(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if context.get('uid', 1) in [r.id for r in obj.user_id]:
                result[obj.id] = True
            else:
                result[obj.id] = False
        return result

    def _get_project_manager_name(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            project_manager_name = [m.name for m in obj.user_id]
            result[obj.id] = ','.join(project_manager_name)
        return result

    def _get_project_sub_state(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.state == 'project_active':
                result[obj.id] = obj.active_tasking.state
            elif obj.state == 'project_filed':
                result[obj.id] = self._get_filing_state(cr, uid, [obj.id], field_name, args, context=None)[obj.id]
        return result

    def is_project_member(self, cr, uid, project_id, context):
        project = self.browse(cr, uid, project_id, context=context)
        # Is project director?
        hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
        if hr_id and self.user_has_groups(cr, uid, "up_project.group_up_project_suozhang", context=context):
            hr_record = self.pool.get('hr.employee').browse(cr, 1, hr_id[0], context=context)
            user_department_id = hr_record.department_id.id if hr_record.department_id else "-1"
            project_department_id = project.chenjiebumen_id.id if project.chenjiebumen_id else None
            job_name = hr_record.job_id.name if hr_record.job_id else None
            if user_department_id == project_department_id and (job_name == u"所长" or job_name == u"分院院长"):
                return True
        # Is Project Operator
        if project.guanlijibie == 'LH200307240001' and uid in [z.id for z in project.zhuguanzongshi_id]:
            return True
        # Is Project Manager
        user_id = self.read(cr, uid, project_id, ['user_id'], context=context)['user_id']
        if uid in user_id:
            return True
        # Is Project common member
        common_member = []
        for member_job in project.member_ids:
            common_member += [u.user_id.id for u in member_job.validation_user_ids if u.user_id]
            common_member += [u.user_id.id for u in member_job.audit_user_ids if u.user_id]
            common_member += [u.user_id.id for u in member_job.profession_manager_user_ids if u.user_id]
            common_member += [u.user_id.id for u in member_job.design_user_ids if u.user_id]
            common_member += [u.user_id.id for u in member_job.proofread_user_ids if u.user_id]
            common_member += [u.user_id.id for u in member_job.drawing_user_ids if u.user_id]
        if uid in set(common_member):
            return True
        # Not a Member
        return False

    def _is_project_member(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if self.is_project_member(cr, context.get('uid', 1), obj.id, context=context):
                result[obj.id] = True
            else:
                result[obj.id] = False
        return result

    def get_sub_state(self, cr, uid, context):
        return self.pool['project.project.active.tasking'].SELECTION + self.pool['project.project.filed.filing'].FILING_STATE

    _columns = {
        # 基础信息
        # 'analytic_account_id': fields.boolean("Over Ride"),

        'user_id': fields.many2many('res.users', 'project_user_id_res_user', 'project_user_id', 'res_user_id',
                                    string='Project Manager',
                                    domain=['|', ("active", "=", True), ("active", "=", False)], track_visibility='onchange'),
        'director_reviewer_id': fields.many2one('res.users', string=u'Review Director'),
        'related_user_id': fields.many2one('res.users', string="Related Users ID"),
        'status_code': fields.integer(string='Status Code'),
        "shifoutoubiao": fields.boolean("Is Tender"),
        "project_type": fields.many2one("project.type", string="Project Type", ),
        'project_logs': fields.one2many('project.log', 'project_id', string='Project Logs'),
        'create_date': fields.datetime('Created on', select=True),
        'create_uid': fields.many2one('res.users', 'Author', select=True),
        'write_date': fields.datetime('Modification date', select=True),
        'write_uid': fields.many2one('res.users', 'Last Contributor', select=True),
        'country_id': fields.many2one('res.country', string='Country'),
        "state_id": fields.many2one('res.country.state', string='State'),
        "city": fields.char(size=128, string="City"),
        'state': fields.selection([("project_active", u"Project Active"),
                                   ("project_cancelled", u"Project Cancelled"),
                                   ("project_processing", u"Project Processing"),
                                   ("project_stop", u"Project Stop"),
                                   ("project_pause", u"Project Pause"),
                                   ("project_filed", u"Project Filing"),
                                   ("project_finish", u"Project Filed"),
                                  ], string="State", track_visibility='onchange'),
        'project_log': fields.html(u"Project Log Info", readonly=True),
        "xiangmubianhao": fields.char(u"Project Num", select=True, size=128, ),
        "chenjiebumen_id": fields.many2one("hr.department", u"In Charge Department"),
        "guimo": fields.char(u"Scale", size=64),
        # Second type
        "categories_id": fields.many2one("project.upcategory", u"项目类别"),
        "customer_contact": fields.many2one('res.partner', 'Customer Contact'),
        "guanlijibie": fields.selection([('LH200307240001', u'院级'), ('LH200307240002', u'所级')], u'Project Level'),
        "toubiaoleibie": fields.selection([('business', u'商务标'), ('technology', u'技术标'), ('complex', u'综合标')],
                                          "Tender Type"),
        "waibao": fields.boolean("Is Outsourcing"),
        'is_project_creater': fields.function(_is_project_creater, type="boolean",
                                              string="Is Project Creater"),
        'is_project_created': fields.function(_is_project_created, type="boolean",
                                              string="Is Project Created"),
        'member_ids': fields.one2many('project.members', 'project_id', string="Members"),
        'is_user_in_operator_group': fields.function(_is_user_in_operator_group, type="boolean",
                                                     string="Is User In Operator Room"),

        'is_user_in_engineer_group': fields.function(_is_user_in_engineer_group, type="boolean",
                                                     string="Is User In Engineer Room"),
        'is_chief': fields.function(_is_chief, type="boolean",
                                    string="Is User is in Chief"),
        'is_admin': fields.function(_is_admin, type="boolean",
                                    string="Is User is in Admin"),
        'is_user_is_project_manager': fields.function(_is_user_is_project_manager, type="boolean",
                                                      string="Is User is The Project Manager"),
        'is_project_member': fields.function(_is_project_member, type="boolean",
                                             string="Is User is The Project Member"),

        'partner_type': fields.selection([("WT200508180001", u"深圳规划局"),
                                          ("WT200508180002", u"深圳市其他"),
                                          ("WT200508180003", u"市外"),
                                          ("WT200509020001", u"其它"), ], string="Partner Type"),
        'is_import': fields.boolean(string="Is import Data"),
        'comment': fields.text(string='Project Comment'),
        'begin_date': fields.date(string='Begin Date'),
        'plan_finish_date': fields.date(string='Plan Finish Date'),
        "shizhenpeitao": fields.boolean("Is City"),
        'questions': fields.text(string="Questions"),
        'next_work_plan': fields.text(string="Next Work Plan"),
        'primary_work': fields.text(string="Primary Work"),
        'city_type': fields.selection(
            [('CC200511210001', u'直辖市'), ('CC200511210002', u'省会城市'), ('CC200511210003', u'地级市'),
             ('CC200511210004', u'县级市'), ('CC200511210005', u'其它'), ('plan_city', u'计划单列市')], string="City Type"),
        "zhuguanzongshi_id": fields.many2many("res.users", "project_zhuangguan_res_user", "project_id", "res_user_id",
                                              string=u"主管总师",
                                              domain=['|', ("active", "=", True), ("active", "=", False)]),
        'import_is_hidden': fields.char(size=8, string="Import Is Hidden"),
        'import_sum_up_flag': fields.char(size=8, string="Import Sum Up Flag"),
        'import_flag': fields.char(size=8, string="Import Flag"),
        'import_schedule': fields.char(size=64, string='Import Schedule'),
        'import_proxy_name': fields.char(size=256, string='Import Proxy Name'),
        'import_aaddress': fields.char(size=256, string='Import AAddress'),
        'import_alinkman': fields.char(size=256, string='Import Alinkman'),
        'import_proejct_number': fields.char(size=256, string='Import Project Num'),
        'temp_status': fields.char(size=56, string="Temp Status"),
        'attachments': fields.many2many("ir.attachment", "project_attachments", "project_id", "attachment_id",
                                        string="related_files"),
        'project_manager_name': fields.function(_get_project_manager_name, type='char', readonly=True,
                                                string="Project Manager Name For export"),
        'project_sub_state': fields.function(_get_project_sub_state, type='selection', selection=get_sub_state,
                                             string='Sub State'),
    }

    def _get_default_country(self, cr, uid, context):
        return self.pool.get('res.country').search(cr, uid, [('name', '=', u'中国')], context=context)

    _defaults = {
        'state': lambda *a: 'project_active',
        'user_id': None,
        'country_id': _get_default_country,
        'is_import': False,
        'privacy_visibility': 'public',
        # 'xiangmubianhao':lambda self, cr, uid, c=None: self.pool.get('ir.sequence').next_by_code(cr, uid, 'project.project', context=c)
    }

    _sql_constraints = [('xiangmubianhao_uniq', 'unique(xiangmubianhao)', 'xiangmubianhao must be unique !')]

    def _get_action(self, cr, uid, ids, form_model_name, action_name, context=None):
        shenpi_form = self.pool.get(form_model_name)
        assert len(ids) == 1
        ctx = (context or {}).copy()
        ctx['default_project_id'] = ids[0]
        shenpi_form_ids = shenpi_form.search(cr, uid, [('project_id', '=', ids[0])])
        shenpi_form_id = shenpi_form_ids and shenpi_form_ids[0] or False
        return {
            'name': action_name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': form_model_name,
            'res_id': shenpi_form_id,
            'target': 'new',
            'context': ctx
        }

    def on_change_country(self, cr, uid, ids, country_id, context=None):
        return {}

    def init_form(self, cr, uid, ids, form_name, project_form_field, context=None):
        assert len(ids) == 1
        project_id = self.browse(cr, uid, ids, context=context)
        if project_id[0] and project_id[0][project_form_field]:
            return project_id[0][project_form_field].id
        else:
            suozhangshenpi = self.pool.get(form_name)
            # by pass
            suozhangshenpi_id = suozhangshenpi.create(cr, 1, {'project_id': ids[0]}, context=context)
            self.pool['project.project.active.tasking'].message_unsubscribe_users(cr, 1, [suozhangshenpi_id], [1], context=context)
            self.write(cr, 1, ids, {project_form_field: suozhangshenpi_id})
            return suozhangshenpi_id

    def create(self, cr, uid, args, context=None):
        if context:
            context.update({'mail_create_nolog': True})
        else:
            context = {'mail_create_nolog': True}
        ids = super(updis_project, self).create(cr, uid, args, context=context)
        self._workflow_signal(cr, uid, [ids], 'start_to_active', context=context)
        return ids


    def action_projects_related_to_me(self, cr, uid, context=None):
        domain = [('create_uid', '=', uid)]
        domain = ['|', ('user_id', '=', uid)] + domain
        domain = ['|', ('zhuguanzongshi_id', '=', uid)] + domain
        domain = ['|', ('director_reviewer_id', '=', uid)] + domain
        project_members_obj = self.pool.get("project.members")
        members_id = project_members_obj.search(cr, uid,
                                                ['|', '|', '|', '|', '|', ('validation_user_ids.user_id', '=', uid),
                                                 ('audit_user_ids.user_id', '=', uid),
                                                 ('profession_manager_user_ids.user_id', '=', uid),
                                                 ('design_user_ids.user_id', '=', uid),
                                                 ('proofread_user_ids.user_id', '=', uid),
                                                 ('drawing_user_ids.user_id', '=', uid), ], context=context)
        project_ids = project_members_obj.read(cr, uid, members_id, ["project_id"], context=context)
        result_ids = set(p['project_id'][0] for p in project_ids)
        domain = ['|', ('id', 'in', list(result_ids))] + domain

        return {
            'name': u'与我相关项目',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.project',
            'target': 'current',
            'domain': domain,
            'context': context,
        }

    def get_need_process_action_domain(self, cr, uid, context=None):
        domain = ['&', ('create_uid', '=', uid), ('status_code', '=', 10101)]
        status_code = []

        # director
        hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
        if hr_id:
            hr_record = self.pool.get('hr.employee').browse(cr, 1, hr_id[0], context=context)
            user_department_id = hr_record.department_id.id if hr_record.department_id else "-1"
        else:
            user_department_id = -1
        domain = ['|', '&', ('status_code', '=', 10102), ('related_user_id', '=', uid)] + domain
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_suozhang', context=context):
            # is True Director In HR
            if hr_id:
                hr_record = self.pool.get('hr.employee').browse(cr, 1, hr_id[0], context=context)
                job_name = hr_record.job_id.name if hr_record.job_id else None
                if job_name == u"所长" or job_name == u"分院院长":
                    domain = ['|', '&', ('status_code', '=', 10105),
                              ('chenjiebumen_id', '=', user_department_id)] + domain
        else:
            config_group_id = tools.get_id_by_external_id(cr, self.pool,
                                                          extends_id="project_active_tasking_config_record",
                                                          model="project.active.tasking.config")
            config_group = self.pool.get('project.active.tasking.config').browse(cr, 1, config_group_id,
                                                                                 context=context)
            config_group_ids = [z.id for z in config_group.cover_director_config]
            if uid in config_group_ids:
                domain = ['|', '&', ('status_code', '=', 10105),
                          ('chenjiebumen_id', '=', user_department_id)] + domain

        # Operator Room
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_jingyingshi', context=context):
            status_code += [10103]
        # Engineer Room
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_zongshishi', context=context):
            status_code += [10104]

        # Manager
        manager_domain = ['|', '&', ('status_code', 'in', [20101, 50101, 60101, 30101, 30104]), ('user_id', '=', uid)]

        # Filed Manager
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_filed_manager,up_project.group_up_project_filed_elec_manager', context=context):
            status_code += [30103]

        domain = ['|', ('status_code', 'in', status_code)] + domain
        return manager_domain + domain

    def project_need_process_action(self, cr, uid, context=None):
        domain = self.get_need_process_action_domain(cr, uid, context=context)
        view_form_id = tools.get_id_by_external_id(cr, self.pool,
                                                   extends_id="edit_project_inherit",
                                                   model="ir.ui.view")
        view_tree_id = tools.get_id_by_external_id(cr, self.pool,
                                                   extends_id="view_project_tree_need_process",
                                                   model="ir.ui.view")

        return {
            'name': u'待处理项目',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.project',
            'target': 'current',
            'domain': domain,
            'context': context,
            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
        }

    def all_projects_action(self, cr, uid, context=None):
        domain = ['|', ('state', 'not in', ['project_active', 'project_cancelled']), ('create_uid', '=', uid)]
        # if self.user_has_groups(cr, uid, 'up_project.group_up_project_suozhang', context=context):
        domain = ['|', '&', ('state', 'in', ['project_active', 'project_cancelled']),
                  ('director_reviewer_id', '=', uid)] + domain
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_jingyingshi', context=context):
            domain = ['|', ('state', 'in', ['project_active', 'project_cancelled'])] + domain
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_zongshishi', context=context):
            domain = ['|', ('state', 'in', ['project_active', 'project_cancelled'])] + domain
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_admin', context=context):
            domain = ['|', ('state', 'in', ['project_active', 'project_cancelled'])] + domain

        return {
            'name': u'所有项目',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.project',
            'target': 'current',
            'domain': domain,
            'context': context,
        }

    def all_filed_projects_action(self, cr, uid, context=None):
        context['search_default_filed-project'] = 1
        return self.all_projects_action(cr, uid, context=context)

    def workflow_signal(self, cr, uid, ids, signal):
        self._workflow_signal(cr, uid, ids, signal)
        return True

    def message_get_suggested_recipients(self, cr, uid, ids, context=None):
        """ Returns suggested recipients for ids. Those are a list of
            tuple (partner_id, partner_name, reason), to be managed by Chatter. """
        result = dict.fromkeys(ids, list())
        if self._all_columns.get('user_id'):
            for obj in self.browse(cr, SUPERUSER_ID, ids, context=context):  # SUPERUSER because of a read on res.users that would crash otherwise
                if not obj.user_id or not [u.partner_id for u in obj.user_id]:
                    continue
                for partner_id in [u.partner_id for u in obj.user_id]:
                    self._message_add_suggested_recipient(cr, uid, result, obj, partner=partner_id,
                                                          reason=self._all_columns['user_id'].column.string, context=context)
        return result

    def add_log(self, cr, uid, ids, log_user=None, log_info=None, context=None):
        for project_id in ids:
            self.write(cr, uid, project_id,
                       {'project_logs': [(0, 0, {'project_id': project_id,
                                                 'log_user': log_user,
                                                 'log_info': log_info})]}, context=context)
        return True


class project_profession(osv.Model):
    """Profession"""
    _name = "project.profession"
    _description = "Project Profession"
    _order = 'order_num'
    _columns = {
        'name': fields.char("Name", required=1, size=64),
        'order_num': fields.integer(size=10, string="Profession Order Num"),
        'short_name': fields.char("Short Name", size=64),
        'code': fields.char("Code", size=64),
        'active': fields.boolean("Active"),
    }
    _defaults = {
        'active': True
    }


class project_members(osv.osv):
    _name = "project.members"
    _description = "Project Members"
    _columns = {
        'profession': fields.many2one('project.profession', required=True, string="Profession"),
        'validation_user_ids': fields.many2many('hr.employee', 'project_members_vali_hr_employee', 'project_member_id',
                                                'employee_id', string="Validation Members"),

        'audit_user_ids': fields.many2many('hr.employee', 'project_members_audit_hr_employee', 'project_member_id',
                                           'employee_id', string="Audit Members"),
        'profession_manager_user_ids': fields.many2many('hr.employee', 'project_members_profession_manager_hr_employee',
                                                        'project_member_id',
                                                        'employee_id', string="Profession Manager Members"),
        'design_user_ids': fields.many2many('hr.employee', 'project_members_design_hr_employee', 'project_member_id',
                                            'employee_id', string="Design/Write Members"),
        'proofread_user_ids': fields.many2many('hr.employee', 'project_members_proofread_hr_employee',
                                               'project_member_id',
                                               'employee_id', string="Proofread Members"),
        'drawing_user_ids': fields.many2many('hr.employee', 'project_members_drawing_hr_employee', 'project_member_id',
                                             'employee_id', string="Drawing/Writing Members"),
        'project_id': fields.many2one('project.project', string="Project", ondelete="cascade"),
    }
    _defaults = {
    }