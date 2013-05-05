#encoding:UTF-8
import time
import datetime
from osv import osv, fields
import tools
import openerp.pooler as pooler
from openerp.tools.safe_eval import safe_eval as eval


class Env(dict):
    def __init__(self, cr, uid, model, ids):
        self.cr = cr
        self.uid = uid
        self.model = model
        self.ids = ids
        self.obj = pooler.get_pool(cr.dbname).get(model)
        self.columns = self.obj._columns.keys() + self.obj._inherit_fields.keys()

    def __getitem__(self, key):
        if (key in self.columns) or (key in dir(self.obj)):
            res = self.obj.browse(self.cr, self.uid, self.ids[0])
            return res[key]
        else:
            return super(Env, self).__getitem__(key)


class MessageCategory(osv.Model):
    _name = "message.category"
    _description = 'UPDIS Message Category'
    _order = "name"
    _columns = {
        'name': fields.char("Title", size=128),
        'default_message_count': fields.integer('Default message count',
                                                help="How many messages should be displayed in front door for this category?"),
        'message_meta': fields.char('Meta',
                                    help="this meta is used to show the message meta info for a categor, all message fields are available",
                                    size=1024),
        'category_message_title_size': fields.integer('Message title length', help='-1 means no shorten at all'),
        'category_message_title_meta': fields.char('Category meta',
                                                   help="This meta is used to display the message title in internal home page for a category,all message fields are available.",
                                                   size=1024),
        'sequence': fields.integer("Display Sequence"),
        'is_anonymous_allowed': fields.boolean('Allow publish messages anonymously?'),
        #'is_display_fbbm':fields.boolean('Display fbbm?'),
        #'is_display_read_times':fields.boolean('Display read times?'),
        'display_position': fields.selection(
            [("shortcut", "Shortcuts"), ("content_left", "Content Left"), ("content_right", "Content Right")]
            , "Display Position"),
        'display_in_departments': fields.many2many("hr.department", string="Display in Departments",
                                                   domain="[('deleted','=',False)]"),
        'is_allow_send_sms': fields.boolean('Allow send SMS?'),
        'is_allow_sms_receiver': fields.boolean('Allow specify sms receiver?'),
        'default_sms_receiver_ids': fields.many2many("hr.employee", "message_category_hr_employee_rel",
                                                     "message_category_id", "hr_employee_id",
                                                     string='Default SMS Receivers'),
        'is_in_use': fields.boolean('Is in use?'),
        'category_manager': fields.many2many('res.users', String="Category Manager"),
        'is_public': fields.boolean('Is public category?'),
        'is_allowed_edit_sms_text': fields.boolean('Is Allowed Edit SMS Text?'),
    }
    _defaults = {
        #'is_display_fbbm':True,
        'is_anonymous_allowed': False,
        'category_message_title_size': 10,
        'is_in_use': False,
        'is_public': False,
        'is_allowed_edit_sms_text': True,
        #'is_display_read_times':True,
    }

    def onchange_is_allow_send_sms(self, cr, uid, ids, is_allow_send_sms, context=None):
        return {}

    def onchange_is_in_use(self, cr, uid, ids, is_allow_send_sms, context=None):
        pass


class Message(osv.Model):
    #TODO: turn off for data import only
    _log_access = True
    _name = "message.message"
    _order = "sequence,write_date desc"
    _description = 'UPDIS Message'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _default_fbbm(self, cr, uid, context=None):
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)])
        if employee_ids:
            return self.pool.get('hr.employee').browse(cr, uid, employee_ids[0]).department_id.name

    def _default_department(self, cr, uid, context=None):
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)])
        if employee_ids:
            return self.pool.get('hr.employee').browse(cr, uid, employee_ids[0]).department_id.id

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, field_name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    def _get_name_display(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.is_display_name and obj.create_uid.name or u'匿名用户'
        return result

    def _get_message_meta_display(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            message_meta = ''
            if obj.category_id.message_meta:
                env = Env(cr, uid, 'message.message', [obj.id])
                message_meta = eval(obj.category_id.message_meta, env, nocopy=True)
            result[obj.id] = message_meta
        return result

    def _get_category_message_title_meta_display(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            category_message_title_meta = ''
            if obj.category_id.category_message_title_meta:
                env = Env(cr, uid, 'message.message', [obj.id])
                category_message_title_meta = eval(obj.category_id.category_message_title_meta, env, nocopy=True)
            result[obj.id] = category_message_title_meta
        return result


    def _get_create_date_display(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):

            if obj.create_date:
                create_date_display = datetime.datetime.strptime(obj.create_date,
                                                                 '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
                result[obj.id] = create_date_display.strftime('%Y-%m-%d %H:%M:%S')
        return result

    def _get_write_date_display(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):

            if obj.write_date:
                write_date_display = datetime.datetime.strptime(obj.write_date,
                                                                '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
                result[obj.id] = write_date_display.strftime('%Y-%m-%d %H:%M:%S')
        return result

    def _get_shorten_name(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            size = obj.category_id.category_message_title_size
            title = len(obj.name) > size and obj.name[:size] + '...' or obj.name
            result[obj.id] = title
        return result

    _columns = {
        'name': fields.char("Title", size=128, required=True),
        'shorten_name': fields.function(_get_shorten_name, type="char", size=256, string="Shorten title"),
        'message_meta_display': fields.function(_get_message_meta_display, type="char", size=256, string="Meta"),
        'category_message_title_meta_display': fields.function(_get_category_message_title_meta_display, type="char",
                                                               size=256, string="Category meta"),
        'category_id': fields.many2one('message.category', 'Category', required=True, change_default=True),
        'content': fields.text("Content"),
        'sequence': fields.integer("Display Sequence"),
        'is_display_name': fields.boolean('Display name?'),
        'fbbm': fields.char('Publisher', size=128),
        'read_times': fields.integer("Read Times"),
        'expire_date': fields.date('Expire Date'),
        'create_date': fields.datetime('Created on', select=True),
        'department_id': fields.many2one("hr.department", "Department", domain=[('deleted', '=', False)]),
        'create_uid': fields.many2one('res.users', 'Author', select=True),
        'write_date': fields.datetime('Modification date', select=True),
        'write_uid': fields.many2one('res.users', 'Last Contributor', select=True),
        'source': fields.char("Message Source", size=128),
        'name_for_display': fields.function(_get_name_display, type="char", size=64, string="Name"),
        'sms_receiver_ids': fields.many2many("hr.employee", "message_hr_employee_rel", "message_id", "hr_employee_id",
                                             "SMS Receiver"),
        'sms': fields.text('SMS', size=140),
        'is_allow_send_sms': fields.related('category_id', 'is_allow_send_sms', type="boolean",
                                            string="Allow send SMS?"),
        'is_allow_sms_receiver': fields.related('category_id', 'is_allow_send_sms', type="boolean",
                                                string="Allow specify sms receiver?"),
        'category_id_name': fields.related('category_id', 'name', type="char",
                                           string="category name"),
        'category_id_is_anonymous_allowed': fields.related('category_id', 'is_anonymous_allowed', type="boolean",
                                                           string="category is anonymous allowed"),
        'category_id_is_allowed_edit_sms_text': fields.related('category_id', 'is_allowed_edit_sms_text',
                                                               type="boolean",
                                                               string="category is allowed edit sms text"),
        'create_date_display': fields.function(_get_create_date_display, type="datetime", string="Create Date Display",
                                               readonly=True),
        'write_date_display': fields.function(_get_write_date_display, type="datetime", string="Write Date Display",
                                              readonly=True),
    }
    _defaults = {
        'fbbm': _default_fbbm,
        'department_id': _default_department,
        'is_display_name': True,
    }

    def onchange_category(self, cr, uid, ids, category_id, context=None):
        ret = {'value': {}}
        if category_id:
            message_category = self.pool.get('message.category').browse(cr, uid, category_id)
            sms_vals = {
                'is_allow_send_sms': message_category.is_allow_send_sms,
                'is_allow_sms_receiver': message_category.is_allow_sms_receiver,
                'sms_receiver_ids': [x.id for x in message_category.default_sms_receiver_ids],
                'category_id_name': message_category.name,
                'category_id_is_anonymous_allowed': message_category.is_anonymous_allowed,
                'category_id_is_allowed_edit_sms_text': message_category.is_allowed_edit_sms_text,
            }
            ret['value'].update(sms_vals)
        return ret

    def onchange_name(self, cr, uid, ids, name, context=None):
        ret = {'value': {}}
        name_vals = {
            'sms': name,
        }
        if not len(ids):
            ret['value'].update(name_vals)
        return ret

    def create(self, cr, uid, vals, context=None):
        context.update({'mail_create_nolog': True})
        if not vals['category_id_is_allowed_edit_sms_text']:
            vals['sms'] = vals['name']
        mid = super(Message, self).create(cr, uid, vals, context)
        sms = self.pool.get('sms.sms')
        message = self.pool.get('message.message').browse(cr, uid, mid, context=context)
        if message.is_allow_send_sms:
            to = ','.join([rid.mobile_phone for rid in message.sms_receiver_ids if rid.mobile_phone])
            if to:
                content = message.sms and message.category_id.name + ':' + message.sms or message.category_id.name + ':' + message.name
                sid = sms.create(cr, uid, {'to': to, 'content': content, 'model': 'message.message', 'res_id': mid},
                                 context=context)
        return mid


