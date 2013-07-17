# -*- encoding:utf-8 -*-
import datetime
from osv import osv, fields


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
        'related_user_id': fields.many2one('res.users', string="Related Users ID"),
        'status_code': fields.integer(string='Status Code'),
        "shifoutoubiao": fields.boolean(u"是否投标项目"),
        "project_type": fields.many2one("project.type", string="Project Type", required=True),
        'project_logs': fields.one2many('project.log', 'project_id', string='Project Logs'),
        'create_date': fields.datetime('Created on', select=True),
        'create_uid': fields.many2one('res.users', 'Author', select=True),
        'write_date': fields.datetime('Modification date', select=True),
        'write_uid': fields.many2one('res.users', 'Last Contributor', select=True),
        'country_id': fields.many2one('res.country', 'Country'),
        "state_id": fields.many2one('res.country.state', 'State', domain="[('country_id','=',country_id)]"),
        "city": fields.char("City", size=128),


        'state': fields.selection([("project_active", u"Project Active"),
                                   ("project_processing", u"Project Processing"),
                                   ("project_stop", u"Project Stop"),
                                   ("project_pause", u"Project Pause"),
                                   ("project_filed", u"Project Filed"), ]),
        'project_log': fields.html(u"Project Log Info", readonly=True),
        "xiangmubianhao": fields.char(u"项目编号", select=True, size=128, ),
        "chenjiebumen_id": fields.many2one("hr.department", u"承接部门"),
        "guimo": fields.char(u"规模", size=64),
        "categories_id": fields.many2one("project.upcategory", u"项目类别"),
        "customer_contact": fields.many2one('res.partner', 'Customer Contact'),
        "guanlijibie": fields.selection([(u'院级', u'院级'), (u'所级', u'所级')], u'项目管理级别'),
        "toubiaoleibie": fields.selection([(u'商务标', u'商务标'), (u'技术标', u'技术标'), (u'综合标', u'综合标')], u"投标类别"),
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
    }

    def _get_default_country(self, cr, uid, context):
        id = self.pool.get('res.country').search(cr, uid, [('name', '=', u'中国')], context=context)
        return id

    _defaults = {
        'state': lambda *a: 'project_active',
        'user_id': None,
        'country_id': _get_default_country,
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
        domain = [('create_uid', '=', uid)]
        status_code = []
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_suozhang', context=context):
            domain = ['|', '&', ('status_code', '=', 10102), ('related_user_id', '=', uid)] + domain
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_jingyingshi', context=context):
            status_code += [10103]
        if self.user_has_groups(cr, uid, 'up_project.group_up_project_zongshishi', context=context):
            status_code += [10104]
        domain = ['|', ('status_code', 'in', status_code)] + domain

        other_domain = ['|', '&', ('status_code', '=', 10105), ('user_id', '=', uid)]
        domain = other_domain + domain

        return {
            'name': 'project test',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,kanban',
            'view_type': 'form',
            'res_model': 'project.project',
            'target': 'current',
            'domain': domain,
            'context': context,
        }


class project_profession(osv.Model):
    """Profession"""
    _name = "project.profession"
    _description = "Project Profession"
    _columns = {
        'name': fields.char("Name", required=1, size=64),
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
