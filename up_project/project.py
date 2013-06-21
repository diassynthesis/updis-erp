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

    def _is_project_creater(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            review_id = obj.create_uid.id
            if review_id == uid:
                result[obj.id] = True
            else:
                result[obj.id] = False

        return result

    _columns = {
        # 基础信息
        #  'analytic_account_id': fields.boolean("Over Ride"),
        "project_type": fields.many2one("project.type", string="Project Type", required=True),
        'project_logs': fields.one2many('project.log', 'project_id', string='Project Logs'),
        'create_date': fields.datetime('Created on', select=True),
        'create_uid': fields.many2one('res.users', 'Author', select=True),
        'write_date': fields.datetime('Modification date', select=True),
        'write_uid': fields.many2one('res.users', 'Last Contributor', select=True),
        'country_id': fields.many2one('res.country', 'Country'),
        "state_id": fields.many2one('res.country.state', 'State', domain="[('country_id','=',country_id)]"),
        "city": fields.char("City", size=128),
        "customer_contact": fields.many2one('res.partner', 'Customer Contact'),
        "guimo": fields.char(u"规模", size=64),

        'gongzuodagang': fields.boolean(u'有工作大纲（保存归档）', ),
        'chuangyouxiangmu': fields.boolean(u'创优项目', ),
        'zhuantihuozixiang': fields.boolean(u'专题或子项（详见工作大纲）', ),
        'youfenbaofang': fields.boolean(u'有分包方（详见分包协议）', ),


        # 总师室
        "categories_id": fields.many2many("project.upcategory", "up_project_category_rel", "project_id", "category_id",
                                          u"项目类别", ),
        "guanlijibie": fields.selection([
                                            (u'院级', u'院级'),
                                            (u'所级', u'所级')], u'项目管理级别', ),
        "chenjiefuzeren_id": fields.many2one("res.users", u"承接项目负责人", ),
        "zhuguanzongshi_id": fields.many2one("res.users", u"主管总师", ),

        # 'assignment_ids': fields.one2many('project.assignment', 'project_id', 'Project Assignment', readonly=True),
        "state": fields.selection([
                                      # ("draft",u"New project"),
                                      ("open", u"提出申请"),
                                      ("suozhangshenpi", u"所长审批"),
                                      ("zhidingbumen", u"经营室指定部门"),
                                      ("zhidingfuzeren", u"总师室指定负责人"),
                                      ("suozhangqianzi", u"所长签字"),
                                      ("fuzerenqidong", u"启动项目"),
                                  ], "State", help='When project is created, the state is \'open\''),

        'states': fields.selection([("project_start", u"Project Start"),
                                    ("project_stop", u"Project End"), ]),
        'project_log': fields.html(u"Project Log Info", readonly=True),
        'is_project_creater': fields.function(_is_project_creater, type="boolean",
                                              string="Is Project Creater"),
    }

    def _get_default_country(self, cr, uid, context):
        id = self.pool.get('res.country').search(cr, uid, [('name', '=', u'中国')], context=context)
        return id

    _defaults = {
        'state': lambda *a: 'open',
        'states': lambda *a: 'project_start',
        'user_id': None,
        'country_id': _get_default_country,
        # 'xiangmubianhao':lambda self, cr, uid, c=None: self.pool.get('ir.sequence').next_by_code(cr, uid, 'project.project', context=c)
    }

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

    def init_form(self, cr, uid, ids, state, object, object_field):
        assert len(ids) == 1
        project_id = self.browse(cr, uid, ids, context=None)
        if project_id[0] and project_id[0][object_field]:
            self.write(cr, uid, ids, {'state': state})
            return project_id[0][object_field].id
        else:
            suozhangshenpi = self.pool.get(object)
            #by pass
            suozhangshenpi_id = suozhangshenpi.create(cr, 1, {'project_id': ids[0]}, None)
            self.write(cr, uid, ids, {'state': state, object_field: suozhangshenpi_id})
            return suozhangshenpi_id

    def act_project_start(self, cr, uid, ids):
        self.write(cr, uid, ids, {'states': "project_start"})
        return ids[0]


# class project_profession(osv.Model):
#     """Profession"""
#     _name = "project.profession"
#     _description = "Project Profession"
#     _columns = {
#         'name': fields.char("Name", size=64),
#         'active': fields.boolean("Active"),
#     }
#     _defaults = {
#         'active': True
#     }


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
