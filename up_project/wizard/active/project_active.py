# -*- encoding:utf-8 -*-
from openerp.osv import osv, fields


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

    def action_active_cancel(self, cr, uid, ids, context=None):
        self.action_end_active(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'project_cancelled', 'status_code': 40101}, context=context)
        return True

    def action_end_active(self, cr, uid, ids, context=None):
        tasking = self.pool.get('project.project.active.tasking').search(cr, uid, [('project_id', '=', ids[0])],
                                                                         context=context)

        self.pool.get('project.project.active.tasking')._workflow_signal(cr, uid, tasking, 'temp_start_to_end',
                                                                         context=context)
        self.write(cr, uid, ids, {'is_import': True})
        return True