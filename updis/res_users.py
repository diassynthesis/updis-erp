# coding=utf-8
from functools import partial
from up_tools.bigantlib import BigAntClient

from openerp import SUPERUSER_ID

from openerp.osv import osv, fields
from up_tools.rtxlib import RtxClient
from openerp.tools.translate import _


class user_device(osv.osv):
    _description = "User device Info"
    _name = "updis.device"

    _columns = {
        'device_id': fields.char("Device Identify ID", size=200),
    }


class res_users(osv.osv):
    _inherit = "res.users"
    _bigAntClient = BigAntClient()
    _rtx_client = RtxClient()
    _base_dep = u'全院'
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
        'big_ant_login_name': fields.char('Big Ant Login Name', size=128),
    }

    SELF_WRITEABLE_FIELDS = ['password', 'signature', 'action_id', 'company_id', 'email', 'name', 'image',
                             'image_medium', 'image_small', 'lang', 'tz', 'address_id', 'work_email', 'work_phone',
                             'mobile_phone', 'work_location', 'interest', 'practice', 'person_resume', 'home_phone', ]

    OTHER_WRITEABLE_FIELDS = ['address_id', 'work_email', 'work_phone', 'image', 'image_medium', 'image_small',
                              'has_image',
                              'mobile_phone', 'work_location', 'interest', 'practice', 'person_resume', 'home_phone',
                              'devices', ]

    def _is_need_rtx_sync(self, cr, uid, context):
        return self.pool.get('ir.config_parameter').get_param(cr, 1, 'bigant.password_sync') == 'True'

    def _is_rtx_user_exist(self, name):
        return self._rtx_client.get_client().IsUserExist(userName=name, key=self._rtx_client.rtx_key)

    def write_rtx_user(self, cr, uid, ids, vals, context=None):
        if self._is_need_rtx_sync(cr, uid, context):
            client = self._rtx_client.get_client()
            for user in self.browse(cr, uid, ids, context):
                params = {'userName': user.login,
                          # 'userPwd':1,
                          'DeptName': self._base_dep,
                          'ChsName': user.name or '',
                          'IGender': 0,
                          'Cell': user.work_phone or '',
                          'Email': user.work_email or '',
                          'Phone': user.mobile_phone or '',
                          # 'Position': '',
                          'AuthTYpe': 0,
                          'key': self._rtx_client.rtx_key}
                client.EditUser(**params)
                if user.active is False:
                    self.unlink_rtx_user(cr, uid, ids, context)
                elif not self._is_rtx_user_exist(user.login):
                    values = {
                        'login': user.login or '',
                        'name': user.name or '',
                        'work_phone': user.work_phone or '',
                        'work_email': user.work_email or '',
                        'mobile_phone': user.mobile_phone or '',
                    }
                    self.add_rtx_user(cr, uid, values, context)

    def add_rtx_user(self, cr, uid, vals, context=None):
        if self._is_need_rtx_sync(cr, uid, context):
            params = {'userName': vals.get('login', ''),
                      # 'userPwd':1,
                      'DeptName': self._base_dep,
                      'ChsName': vals.get('name', ''),
                      'IGender': 1,
                      'Cell': vals.get('work_phone', ''),
                      'Email': vals.get('work_email', ''),
                      'Phone': vals.get('mobile_phone', ''),
                      # 'Position':'',
                      'AuthTYpe': 0,
                      'key': self._rtx_client.rtx_key}
            if self._is_rtx_user_exist(vals.get('login')):
                raise osv.except_osv(_('Warning!'), _('当前登录名已经在RTX中使用.'))
            else:
                self._rtx_client.get_client().AddUser(**params)

    def unlink_rtx_user(self, cr, uid, ids, context):
        if self._is_need_rtx_sync(cr, uid, context):
            client = self._rtx_client.get_client()
            for user in self.browse(cr, uid, ids, context):
                try:
                    client.DeleteUser(userName=user.login, key=self._rtx_client.rtx_key)
                except Exception:
                    pass

    def unlink(self, cr, uid, ids, context=None):
        self.unlink_rtx_user(cr, uid, ids, context)
        return super(res_users, self).unlink(cr, uid, ids, context)

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
        if not (len(values) == 1 and 'password' in values):
            self.write_rtx_user(cr, 1, ids, values, context)
        return res

    def create(self, cr, uid, vals, context=None):
        self.add_rtx_user(cr, uid, vals, context)
        if self.user_has_groups(cr, uid, 'updis.group_res_user_manager'):
            return super(res_users, self).create(cr, 1, vals, context)
        else:
            return super(res_users, self).create(cr, uid, vals, context)

    def on_change_login(self, cr, uid, ids, login, big_ant_name, context=None):
        ret = {'value': {}}
        if not big_ant_name:
            vals = {
                'big_ant_login_name': login,
            }
            ret['value'].update(vals)
        return ret

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
        if self.pool.get('ir.config_parameter').get_param(cr, 1, 'bigant.password_sync') == 'True' and self._is_rtx_user_exist(user.login):
            params = {
                'userName': user.login,
                'pwd': new_passwd,
                'key': self._rtx_client.rtx_key,
            }
            self._rtx_client.get_client().SetUserPwd(**params)
        return result


class ChangePasswordUser(osv.TransientModel):
    _inherit = 'change.password.user'
    _bigAntClient = BigAntClient()
    _rtx_client = RtxClient()

    def change_password_button(self, cr, uid, ids, context=None):
        for user in self.browse(cr, uid, ids, context=context):
            self.pool.get('res.users').write(cr, uid, user.user_id.id, {'password': user.new_passwd})
            if self.pool.get('ir.config_parameter').get_param(cr, 1, 'bigant.password_sync') == 'True' and \
                    self._rtx_client.get_client().IsUserExist(userName=user.user_id.login, key=self._rtx_client.rtx_key):
                params = {
                    'userName': user.user_id.login,
                    'pwd': user.new_passwd,
                    'key': self._rtx_client.rtx_key,
                }
                self._rtx_client.get_client().SetUserPwd(**params)