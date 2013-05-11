from functools import partial

from openerp import SUPERUSER_ID

from osv import osv, fields


class res_users(osv.osv):
    _description = "User device Info"
    _name = "updis.device"

    _columns = {
        'device_id': fields.char("Device Identify ID", size=200),
    }


class res_users(osv.osv):
    _inherit = "res.users"

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
    }

    SELF_WRITEABLE_FIELDS = ['password', 'signature', 'action_id', 'company_id', 'email', 'name', 'image',
                             'image_medium', 'image_small', 'lang', 'tz', 'address_id', 'work_email', 'work_phone',
                             'mobile_phone', 'work_location', 'interest', 'practice', 'person_resume', 'home_phone']

    OTHER_WRITEABLE_FIELDS = ['address_id', 'work_email', 'work_phone',
                              'mobile_phone', 'work_location', 'interest', 'practice', 'person_resume', 'home_phone',
                              'devices']

    def write(self, cr, uid, ids, values, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        if ids == [uid]:
            for key in values.keys():
                if not (key in self.SELF_WRITEABLE_FIELDS or key.startswith('context_')):
                    break
            else:
                if 'company_id' in values:
                    if not (values['company_id'] in self.read(cr, SUPERUSER_ID, uid, ['company_ids'], context=context)[
                        'company_ids']):
                        del values['company_id']
                uid = 1 # safe fields only, so we write as super-user to bypass access rights
        else:
        #others can update user info, like hr manager
            #TODO: need add hr manager validate
            for key in values.keys():
                if not (key in self.OTHER_WRITEABLE_FIELDS or key.startswith('context_')):
                    break
                else:
                    uid = 1 # safe fields only, so we write as super-user to bypass access rights

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