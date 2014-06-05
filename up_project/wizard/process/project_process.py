# -*- encoding:utf-8 -*-
from osv import osv, fields


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

    def button_process_finish(self, cr, uid, ids, context=None):
        self._workflow_signal(cr, uid, ids, 'process_finish', context=context)
        return self.button_filed_filing_form(cr, uid, ids, context)