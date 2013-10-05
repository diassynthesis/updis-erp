__author__ = 'cysnake4713'


def is_project_user_same_department(self, cr, uid, department_id, context=None):
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


def get_user_department(self, cr, uid, context=None):
    hr_id = self.pool.get('hr.employee').search(cr, uid, [("user_id", '=', uid)], context=context)
    if hr_id:
        hr_record = self.pool.get('hr.employee').browse(cr, uid, hr_id[0], context=context)
        return hr_record.department_id.id if hr_record.department_id else None
    else:
        return None
