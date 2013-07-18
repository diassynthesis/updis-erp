# -*- encoding:utf-8 -*-
from osv import osv, fields


class project_project_inherit(osv.osv):
    _inherit = 'project.project'
    _name = 'project.project'

    _columns = {
        'state_active': fields.selection([
            ("project_active_tasking", u"Project Active Tasking"),
            ("project_active_filed", u"Project Active Filed"),
        ]),
    }

    _defaults = {
        # 'state_active': lambda *a: 'project_active_tasking',
    }

    def act_active_workflow(self, cr, uid, ids, context=None):
        return ids[0]

    def action_end_active(self, cr, uid, ids, context=None):
        self.pool.get('project.project.active.tasking')
        self._workflow_signal(cr, uid, ids, 'temp_start_to_end', context=context)
        return True