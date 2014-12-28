# -*- encoding:utf-8 -*-
from openerp import exceptions
from openerp.osv import osv, fields


class project_project_inherit(osv.osv):
    _inherit = 'project.project'
    _name = 'project.project'

    _columns = {
        'state_process': fields.selection([
            ("add_member", u"Project Add Member"),
            ("process_filed", u"Project Process Filed"),
        ]),
    }

    _defaults = {
        # 'state_active': lambda *a: 'project_active_tasking',
    }

    def act_process_workflow(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'project_processing'}, context=context)
        self._workflow_signal(cr, uid, ids, 's_add_m_str', context=context)
        return ids[0]

    def action_process_stop(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'project_stop', 'status_code': 50101}, context=context)
        return True

    def action_process_pause(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'project_pause', 'status_code': 60101}, context=context)
        return True

    def action_process_pause_back(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'project_processing', 'status_code': 20101}, context=context)
        return True

    def action_process_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'project_process_cancel', 'status_code': 50101}, context=context)
        return True

    def button_process_finish(self, cr, uid, ids, context=None):
        # 如果没有项目负责人，或者项目负责人都离院，则不能归档
        project_users = self.read(cr, uid, ids[0], ['user_id'], context)['user_id']
        project_users = self.pool['res.users'].search(cr, uid, [('id', 'in', project_users), ("active", "=", True)], context=context)
        if not len(project_users):
            raise exceptions.Warning(u'本项目没有项目负责人,或者当前项目负责人已经离院。请在项目成员标签卡下，填写项目负责人或主管总师变更变更申请后再进行归档！')
        self._workflow_signal(cr, uid, ids, 'process_finish', context=context)
        self.write(cr, uid, ids, {'state': 'project_filed', 'status_code': 70101}, context=context)
        return self.button_filed_filing_form(cr, uid, ids, context)