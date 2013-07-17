# -*- encoding:utf-8 -*-
from osv import osv, fields


class project_project_inherit(osv.osv):
    _inherit = 'project.project'
    _name = 'project.project'

    _columns = {
        'state_filed': fields.selection([
            ("start_file", u"Project Start File"),
            ("end_file", u"Project End File"),
        ]),
    }

    _defaults = {
        # 'state_active': lambda *a: 'project_active_tasking',
    }

    def act_filed_workflow(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'project_filed'}, context=context)
        return ids[0]