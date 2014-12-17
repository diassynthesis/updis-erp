__author__ = 'cysnake4713'

from openerp.osv import fields

from openerp.osv import osv


class hr_employee_inheirt(osv.osv):
    _inherit = "hr.employee"
    _name = "hr.employee"

    def _get_related_project_members(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        result_ids = set()
        for the_id in ids:
            #members
            project_members_obj = self.pool.get("project.members")
            members_id = project_members_obj.search(cr, uid,
                                                    ['|', '|', '|', '|', '|', ('validation_user_ids', '=', the_id),
                                                     ('audit_user_ids', '=', the_id),
                                                     ('profession_manager_user_ids', '=', the_id),
                                                     ('design_user_ids', '=', the_id),
                                                     ('proofread_user_ids', '=', the_id),
                                                     ('drawing_user_ids', '=', the_id), ], context=context)
            project_ids = project_members_obj.read(cr, uid, members_id, ["project_id"], context=context)
            result_ids = result_ids | set(p['project_id'][0] for p in project_ids)

            #manager and in charge
            employee = self.browse(cr, uid, the_id, context=context)
            project_ids = self.pool.get("project.project").search(cr, uid, ['|', '|',
                                                                            ('user_id', '=',
                                                                             employee.user_id.id if employee.user_id else None),
                                                                            ('zhuguanzongshi_id', '=',
                                                                             employee.user_id.id if employee.user_id else None),
                                                                            ('id', 'in', list(result_ids))],
                                                                  order="begin_date desc",
                                                                  context=context)
            # result_ids = result_ids | set(project_ids)

            result[the_id] = list(project_ids)

        return result

    _columns = {
        "related_project_members": fields.function(_get_related_project_members, type="many2many",
                                                   relation="project.project",
                                                   string="Related Projects", ),
    }