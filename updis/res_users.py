# coding=utf-8
from functools import partial
from up_tools.bigantlib import BigAntClient

from openerp import SUPERUSER_ID

from openerp.osv import osv, fields
from up_tools import docguarder


class user_device(osv.osv):
    _description = "User device Info"
    _name = "updis.device"

    _columns = {
        'device_id': fields.char("Device Identify ID", size=200),
    }


class res_users(osv.osv):
    _inherit = "res.users"
    _bigAntClient = BigAntClient()
    _columns = {
        'sign_image': fields.binary("Sign Image",
                                    help="This field holds the image used as siganture for this contact"),
        'address_id': fields.many2one('res.partner', 'Working Address'),
        'work_email': fields.char('Work Email', size=240),
        'work_phone': fields.char('Work Phone', size=32, readonly=False),
        'mobile_phone': fields.char('Work Mobile', size=32, readonly=False),
        'work_location': fields.char('Office Location', size=32),
        'interest': fields.char("Interest", size=100),
        'practice': fields.text("Practice"),
        'person_resume': fields.text("Personal Resume"),
        'home_phone': fields.char('Home Phone', size=32, readonly=False),
        'devices': fields.many2many("updis.device", "res_users_device_rel", "res_users_id", "device_id",
                                    "User Device Relative"),
        'big_ant_login_name': fields.char('Docguarder & Big Ant User Name', size=128),
        'gender': fields.selection([(u'男', u'男'), (u'女', u'女')], 'Gender'),
    }

    SELF_WRITEABLE_FIELDS = ['password', 'signature', 'action_id', 'company_id', 'email', 'name', 'image',
                             'image_medium', 'image_small', 'lang', 'tz', 'address_id', 'work_email', 'work_phone',
                             'mobile_phone', 'work_location', 'interest', 'practice', 'person_resume', 'home_phone']

    OTHER_WRITEABLE_FIELDS = ['address_id', 'work_email', 'work_phone', 'image', 'image_medium', 'image_small',
                              'has_image',
                              'mobile_phone', 'work_location', 'interest', 'practice', 'person_resume', 'home_phone',
                              'devices', 'gender']

    def get_department_suzhang_ids(self, cr, uid, ids, context=None):
        employee_ids = self.pool['hr.employee'].search(cr, uid, [('user_id', 'in', ids)], context=context)
        department_ids = [e.department_id.id for e in self.pool['hr.employee'].browse(cr, uid, employee_ids, context) if e.department_id]
        department_user_ids = self.pool['hr.employee'].search(cr, uid, [('department_id', 'in', department_ids)], context=context)
        department_user_ids = [e.user_id.id for e in self.pool['hr.employee'].browse(cr, uid, department_user_ids, context) if e.user_id]
        suzhang_group = self.pool.get('ir.model.data').get_object(cr, 1, 'up_project', 'group_up_project_suozhang', context=context)
        suzhang_user_ids = [u.id for u in suzhang_group.users]
        return list(set(department_user_ids) & set(suzhang_user_ids))

    def write(self, cr, uid, ids, values, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        if ids == [uid]:
            for key in values.keys():
                if not (key in self.SELF_WRITEABLE_FIELDS or key.startswith('context_')):
                    break
            else:
                if 'company_id' in values:
                    if not (values['company_id'] in self.read(cr, SUPERUSER_ID, uid, ['company_ids'],
                                                              context=context)['company_ids']):
                        del values['company_id']
                uid = 1  # safe fields only, so we write as super-user to bypass access rights
        else:
            # others can update user info, like hr manager
            # TODO: need add hr manager validate
            for key in values.keys():
                if not (key in self.OTHER_WRITEABLE_FIELDS or key.startswith('context_')):
                    break
                else:
                    uid = 1  # safe fields only, so we write as super-user to bypass access rights

        res = super(res_users, self).write(cr, uid, ids, values, context=context)

        # clear caches linked to the users
        self.pool.get('ir.model.access').call_cache_clearing_methods(cr)
        clear = partial(self.pool.get('ir.rule').clear_cache, cr)
        map(clear, ids)
        db = cr.dbname
        if db in self._uid_cache:
            for id in ids:
                if id in self._uid_cache[db]:
                    del self._uid_cache[db][id]
        self.context_get.clear_cache(self)
        return res

    def create(self, cr, uid, vals, context=None):
        if self.user_has_groups(cr, uid, 'updis.group_res_user_manager'):
            return super(res_users, self).create(cr, 1, vals, context)
        else:
            return super(res_users, self).create(cr, uid, vals, context)

    # noinspection PyUnusedLocal
    def on_change_login(self, cr, uid, ids, login, big_ant_name, context=None):
        ret = {'value': {}}
        if not big_ant_name:
            vals = {
                'big_ant_login_name': login,
            }
            ret['value'].update(vals)
        return ret

    # noinspection PyUnusedLocal
    def _get_group(self, cr, uid, context=None):
        dataobj = self.pool.get('ir.model.data')
        result = []
        try:
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_user')
            result.append(group_id)
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'base', 'group_partner_manager')
            result.append(group_id)
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'project', 'group_project_user')
            result.append(group_id)
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID, 'up_project',
                                                           'group_up_project_common_user')
            result.append(group_id)
        except ValueError:
            # If these groups does not exists anymore
            pass
        return result

    _defaults = {
        'groups_id': _get_group,
    }

    def change_password(self, cr, uid, old_passwd, new_passwd, context=None):
        result = super(res_users, self).change_password(cr, uid, old_passwd, new_passwd, context=context)
        user = self.browse(cr, 1, uid, context)
        if user.big_ant_login_name and self.pool.get('ir.config_parameter').get_param(cr, 1, 'bigant.password_sync') == 'True':
            params = {
                'loginName': user.big_ant_login_name,
                'password': new_passwd,
            }
            self._bigAntClient.Employee___asmx.SetPassword2.post(**params)
        if self.pool.get('ir.config_parameter').get_param(cr, 1, 'docguarder.password_sync') == 'True':
            docguarder.change_password(user.big_ant_login_name, new_passwd)
        return result


class ChangePasswordUser(osv.TransientModel):
    _inherit = 'change.password.user'
    _bigAntClient = BigAntClient()

    def change_password_button(self, cr, uid, ids, context=None):
        for user in self.browse(cr, uid, ids, context=context):
            self.pool.get('res.users').write(cr, uid, user.user_id.id, {'password': user.new_passwd})
            res_user = self.pool.get('res.users').browse(cr, 1, user.user_id.id, context)
            if res_user.big_ant_login_name and self.pool.get('ir.config_parameter').get_param(cr, 1, 'bigant.password_sync') == 'True':
                params = {
                    'loginName': res_user.big_ant_login_name,
                    'password': user.new_passwd,
                }
                self._bigAntClient.Employee___asmx.SetPassword2.post(**params)
            if self.pool.get('ir.config_parameter').get_param(cr, 1, 'docguarder.password_sync') == 'True':
                docguarder.change_password(user.user_id.big_ant_login_name, user.new_passwd)
