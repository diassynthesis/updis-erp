# -*- encoding:utf-8 -*-
from osv import osv, fields


class project_project_inherit(osv.osv):
    _inherit = 'project.project'
    _name = 'project.project'

    _columns = {
        'state_active': fields.selection([
            ("project_active_tasking", u"Project Active Tasking"),
        ]),
    }

    _defaults = {
        'state_active': lambda *a: 'project_active_tasking',
    }