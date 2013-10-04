# -*- encoding:utf-8 -*-
import datetime
from openerp.osv import fields
from openerp.osv import osv


class updis_project_project(osv.osv):
    _inherit = "project.project"
    _name = 'project.project'

    def __is_project_user_same_department(self, cr, uid, department_id, context):
        hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
        if hr_id:
            hr_record = self.pool.get('hr.employee').browse(cr, uid, hr_id[0], context=context)
            user_department_id = hr_record.department_id.id if hr_record.department_id else "sdfsdf"
            if department_id == user_department_id:
                return True
            else:
                return False
        else:
            return False

    def _is_user_contract_visible(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            is_same_department = self.__is_project_user_same_department(cr, uid,
                                                                        obj.chenjiebumen_id.id if obj.chenjiebumen_id else None,
                                                                        context=context)
            result[obj.id] = False
            user_id = self.read(cr, uid, obj.id, ['user_id'], context=context)['user_id']
            if uid in user_id:
                result[obj.id] = True
            elif self.user_has_groups(cr, uid,
                                      'up_contract.group_up_contract_user,\
                                      up_contract.group_up_contract_manager,\
                                      up_contract.group_up_contract_admin',
                                      context=context):
                if self.user_has_groups(cr, uid, 'up_contract.group_up_contract_all_limit'):
                    result[obj.id] = True
                else:
                    if is_same_department:
                        result[obj.id] = True
                    else:
                        result[obj.id] = False
        return result

    _columns = {
        'contract_ids': fields.one2many('project.contract.contract', 'project_id',
                                        string='Project Contracts'),
        'can_see_contract': fields.function(_is_user_contract_visible, type="boolean",
                                            string="Is User Can See Contract"),
    }


class project_active_tasking_inherit(osv.osv):
    _name = "project.project.active.tasking"
    _inherit = "project.project.active.tasking"

    def workflow_manager_room(self, cr, uid, ids, context=None):
        contract_obj = self.pool.get("project.contract.contract")
        project = self.browse(cr, uid, ids[0], context=context)
        if project and not project.is_import:
            if not project.shifoutoubiao:
                cid = contract_obj.create(cr, 1, {"name": project.name, 'project_id': project.project_id.id,
                                                  "number": project.xiangmubianhao,
                                                  "customer": [
                                                      (6, 0, [project.partner_id.id] if project.partner_id else [])],
                                                  "customer_contact": [(6, 0, [
                                                      project.customer_contact.id] if project.customer_contact else [])]},
                                          context=context)
            else:
                cid = contract_obj.create(cr, 1, {"name": project.name, 'project_id': project.project_id.id,
                                                  "type": 'tender',
                                                  "number": project.xiangmubianhao,
                                                  "customer": [
                                                      (6, 0, [project.partner_id.id] if project.partner_id else [])],
                                                  "customer_contact": [(6, 0, [
                                                      project.customer_contact.id] if project.customer_contact else [])]},
                                          context=context)
        tasking = self.browse(cr, 1, ids[0], context=context)
        if not tasking.is_import:
            self.write(cr, 1, ids, {'state': 'end', 'status_code': 10106, 'begin_date': datetime.date.today()},
                       context=context)
        else:
            self.write(cr, 1, ids, {'state': 'end', 'status_code': 10106, },
                       context=context)

        return True