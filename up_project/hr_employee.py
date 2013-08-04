__author__ = 'cysnake4713'

from openerp.osv import fields

from osv import osv


class hr_employee_inheirt(osv.osv):
    _inherit = "hr.employee"
    _name = "hr.employee"

    def _get_related_project_members(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        result_ids = set()
        for the_id in ids:
            cr.execute("""select project_members.project_id
            from project_members_vali_hr_employee, project_members
            where employee_id=%s
                and project_member_id =  project_members.id""", (the_id,))
            result_ids = result_ids | set([r[0] for r in cr.fetchall()])

            ##
            cr.execute("""select project_members.project_id
            from project_members_audit_hr_employee, project_members
            where employee_id=%s
                and project_member_id =  project_members.id""", (the_id,))
            result_ids = result_ids | set([r[0] for r in cr.fetchall()])

            result[the_id] = list(result_ids)

        return result

    _columns = {
        "related_project_members": fields.function(_get_related_project_members, type="many2many",
                                                   relation="project.project",
                                                   string="Related Projects"),
    }