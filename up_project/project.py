# -*- encoding:utf-8 -*-
import datetime
from osv import osv, fields


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
            res['user_id'] = project.user_id.id if project.user_id else None
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
            res['zhuguanzongshi_id'] = project.zhuguanzongshi_id.id if project.zhuguanzongshi_id else None
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
        "user_id": fields.many2one('res.users', string="Project Manager"),
        "name": fields.char(size=256, string="Project Name"),
        "xiangmubianhao": fields.char(size=256, string="Project Num"),
        'country_id': fields.many2one('res.country', 'Country'),
        "state_id": fields.many2one('res.country.state', 'State', domain="[('country_id','=',country_id)]"),
        "city": fields.char("City", size=128),
        'city_type': fields.selection(
            [('CC200511210001', u'直辖市'), ('CC200511210002', u'省会城市'), ('CC200511210003', u'地级市'),
             ('CC200511210004', u'县级市'), ('CC200511210005', u'其它')], string="City Type"),
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
        "zhuguanzongshi_id": fields.many2one("res.users", u"主管总师"),
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
        project.write({
            'user_id': self_record.user_id.id if self_record.user_id.id else None,
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
            'zhuguanzongshi_id': self_record.zhuguanzongshi_id.id if self_record.zhuguanzongshi_id.id else None,
            'chenjiebumen_id': self_record.chenjiebumen_id.id if self_record.chenjiebumen_id.id else None,
            'guanlijibie': self_record.guanlijibie,
            'guimo': self_record.guimo,
            'waibao': self_record.waibao,
            'shizhenpeitao': self_record.shizhenpeitao,
        })
        return True


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


    _columns = {
        "name": fields.char("Category", size=64, required=True),
        "complete_name": fields.function(_cate_name_get_fnc, type="char", string="Name"),
        "project_type": fields.many2one("project.type", string="Project Type", ),
        'summary': fields.text("Summary"),
        'parent_id': fields.many2one('project.upcategory', "Parent Category", ondelete='set null', select=True),
        'child_ids': fields.one2many('project.upcategory', 'parent_id', 'Child Categories'),

    }
    _sql_constraints = [
        ('name', 'unique(parent_id,name)', 'The name of the category must be unique')
    ]
    _order = 'parent_id,name asc'
    _constraints = [
        (osv.osv._check_recursion, 'Error! You cannot create recursive categories', ['parent_id'])
    ]


class project_log(osv.osv):
    _log_access = True
    _name = "project.log"
    _order = "log_date desc"
    _columns = {
        'log_date': fields.datetime('Created on'),
        'project_id': fields.many2one('project.project', "related Project"),
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
    _order = "begin_date desc"

    def _is_project_creater(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            review_id = obj.create_uid.id
            if review_id == uid:
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
        # 基础信息
        #  'analytic_account_id': fields.boolean("Over Ride"),
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
        "state_id": fields.many2one('res.country.state', string='State', domain="[('country_id','=',country_id)]"),
        "city": fields.char(size=128, string="City"),
        'state': fields.selection([("project_active", u"Project Active"),
                                   ("project_cancelled", u"Project Cancelled"),
                                   ("project_processing", u"Project Processing"),
                                   ("project_stop", u"Project Stop"),
                                   ("project_pause", u"Project Pause"),
                                   ("project_filed", u"Project Filed"),
                                  ], string="State"),
        'project_log': fields.html(u"Project Log Info", readonly=True),
        "xiangmubianhao": fields.char(u"Project Num", select=True, size=128, ),
        "chenjiebumen_id": fields.many2one("hr.department", u"In Charge Department"),
        "guimo": fields.char(u"Scale", size=64),
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

        'is_user_is_project_manager': fields.function(_is_user_is_project_manager, type="boolean",
                                                      string="Is User is The Project Manager"),

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
             ('CC200511210004', u'县级市'), ('CC200511210005', u'其它')], string="City Type"),
        "zhuguanzongshi_id": fields.many2one("res.users", u"主管总师"),
        'import_is_hidden': fields.char(size=8, string="Import Is Hidden"),
        'import_sum_up_flag': fields.char(size=8, string="Import Sum Up Flag"),
        'import_flag': fields.char(size=8, string="Import Flag"),
        'import_schedule': fields.char(size=64, string='Import Schedule'),
        'import_proxy_name': fields.char(size=256, string='Import Proxy Name'),
        'import_aaddress': fields.char(size=256, string='Import AAddress'),
        'import_alinkman': fields.char(size=256, string='Import Alinkman'),
        'import_proejct_number': fields.char(size=256, string='Import Project Num'),
        'temp_status': fields.char(size=56, string="Temp Status"),

    }

    def _get_default_country(self, cr, uid, context):
        id = self.pool.get('res.country').search(cr, uid, [('name', '=', u'中国')], context=context)
        return id

    _defaults = {
        'state': lambda *a: 'project_active',
        'user_id': None,
        'country_id': _get_default_country,
        'is_import': False,
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
        project_id = self.browse(cr, 1, ids, context=None)
        if project_id[0] and project_id[0][project_form_field]:
            return project_id[0][project_form_field].id
        else:
            suozhangshenpi = self.pool.get(form_name)
            #by pass
            suozhangshenpi_id = suozhangshenpi.create(cr, 1, {'project_id': ids[0]}, context=context)
            self.write(cr, 1, ids, {project_form_field: suozhangshenpi_id})
            return suozhangshenpi_id

    def create(self, cr, uid, args, context=None):
        ids = super(updis_project, self).create(cr, uid, args, context=None)
        self._workflow_signal(cr, uid, [ids], 'start_to_active', context=context)
        return ids


    def related_to_me_action(self, cr, uid, context=None):
        domain = ['&', ('create_uid', '=', uid), ('status_code', '=', 10101)]
        status_code = []
        #director
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_suozhang', context=context):
            domain = ['|', '&', ('status_code', '=', 10102), ('related_user_id', '=', uid)] + domain
            #Operator Room
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_jingyingshi', context=context):
            status_code += [10103]
            #Engineer Room
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_zongshishi', context=context):
            status_code += [10104]

        #Manager
        manager_domain = ['|', '&', ('status_code', 'in', [10105, 20101, 50101, 60101]), ('user_id', '=', uid)]

        #Filed Manager
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_filed_manager', context=context):
            status_code += [30101]

        domain = ['|', ('status_code', 'in', status_code)] + domain
        domain = manager_domain + domain

        return {
            'name': u'待处理项目',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.project',
            'target': 'current',
            'domain': domain,
            'context': context,
        }

    def all_projects_action(self, cr, uid, context=None):
        domain = ['|', ('state', 'not in', ['project_active', 'project_cancelled']), ('create_uid', '=', uid)]
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_suozhang', context=context):
            domain = ['|', '&', ('state', 'in', ['project_active', 'project_cancelled']),
                      ('director_reviewer_id', '=', uid)] + domain
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_jingyingshi', context=context):
            domain = ['|', ('state', 'in', ['project_active', 'project_cancelled'])] + domain
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_zongshishi', context=context):
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

    def workflow_signal(self, cr, uid, ids, signal):
        self._workflow_signal(cr, uid, ids, signal)
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
        'project_id': fields.many2one('project.project', string="Project"),
    }
    _defaults = {
    }


    # class project_duty(osv.Model):
    #     """Duty"""
    #     _name = "project.duty"
    #     _description = "Project Duty"
    #     _columns = {
    #         'name': fields.char("Name", size=64),
    #         'active': fields.boolean("Active"),
    #     }
    #     _defaults = {
    #         'active': True
    #     }


    # class project_assignment(osv.Model):
    #     """docstring for project_assignment"""
    #     _name = "project.assignment"
    #     _description = "Project Assignment"
    #
    #     def _get_project(self, cr, uid, *args, **kwargs):
    #         #import pdb;pdb.set_trace()
    #         pass
    #
    #     _columns = {
    #         'duty_id': fields.many2one('project.duty', 'Duty'),
    #         'profession_id': fields.many2one('project.profession', 'Profession'),
    #         'project_id': fields.many2one('project.project', 'Project'),
    #     }
    #     _defaults = {
    #         'project_id': _get_project,
    #     }
