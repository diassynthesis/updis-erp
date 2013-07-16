# -*- encoding:utf-8 -*-
from osv import osv, fields


class project_project_inherit(osv.osv):
    _inherit = 'project.project'
    _name = 'project.project'

    _columns = {
        'state_temp_process': fields.selection([
            ("project_temp_process_add_member", u"Project Add Member"),
            ("project_temp_process_filed", u"Project Process Filed"),
        ]),
    }

    _defaults = {
        # 'state_active': lambda *a: 'project_active_tasking',
    }

    def act_temp_process_workflow(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'project_processing'}, context=context)
        return ids[0]