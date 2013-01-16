#encoding:UTF-8
import time
from osv import osv,fields
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
	_name="message.category"
	_order="name"
	_columns={
			'name':fields.char("Title",size=128),
			'default_message_count':fields.integer('Default message count',help="How many messages should be displayed in front door for this category?"),
			'message_meta':fields.char('Meta',help="this meta is used to show the message meta info for a categor, all message fields are available", size=1024),
			'category_message_title_size':fields.integer('Message title length',help='-1 means no shorten at all'),
			'category_message_title_meta':fields.char('Category meta',help="This meta is used to display the message title in internal home page for a category,all message fields are available.", size=1024),
			'sequence':fields.integer("Display Sequence"),
			'is_anonymous_allowed':fields.boolean('Allow publish messages anonymously?'),
			#'is_display_fbbm':fields.boolean('Display fbbm?'),
			#'is_display_read_times':fields.boolean('Display read times?'),
			'display_position':fields.selection(
				[("shortcut","Shortcuts"),("content_left","Content Left"),("content_right","Content Right")]
				,"Display Position"),
			'display_in_departments':fields.many2many("hr.department",string="Display in Departments",domain="[('deleted','=',False)]"),
			'is_allow_send_sms':fields.boolean('Allow send SMS?'),
			'is_allow_sms_receiver':fields.boolean('Allow specify sms receiver?'),
			'default_sms_receiver_ids':fields.many2many('res.users',string='Default SMS Receivers'),
			}
	_defaults={
			#'is_display_fbbm':True,
			'is_anonymous_allowed':False,
			'category_message_title_size':10,
			#'is_display_read_times':True,
			}
	def onchange_is_allow_send_sms(self,cr,uid,ids,is_allow_send_sms,context=None):
		return {}

class Message(osv.Model):
	#TODO: turn off for data import only
	#_log_access=False
	_name="message.message"
	_order="sequence,write_date desc"
	_inherit=['mail.thread', 'ir.needaction_mixin']
	def _default_fbbm(self,cr,uid,context=None):
		employee_ids = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		if employee_ids:
			return self.pool.get('hr.employee').browse(cr,uid,employee_ids[0]).department_id.name
	def _default_department(self,cr,uid,context=None):
		employee_ids = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		if employee_ids:
			return self.pool.get('hr.employee').browse(cr,uid,employee_ids[0]).department_id
	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image)
		return result
	
	def _set_image(self, cr, uid, id, field_name, value, args, context=None):
		return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
	
	def _get_name_display(self,cr,uid,ids,field_name,args,context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = obj.is_display_name and obj.write_uid.name or u'匿名用户'
		return result	
	def _get_message_meta_display(self,cr,uid,ids,field_name,args,context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			message_meta = ''
			if obj.category_id.message_meta:
				env = Env(cr, uid, 'message.message', [obj.id])
				message_meta = eval(obj.category_id.message_meta,env,nocopy=True)
			result[obj.id] = message_meta
		return result	
	def _get_category_message_title_meta_display(self,cr,uid,ids,field_name,args,context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			category_message_title_meta = ''
			if obj.category_id.category_message_title_meta:
				env = Env(cr, uid, 'message.message', [obj.id])
				category_message_title_meta = eval(obj.category_id.category_message_title_meta,env,nocopy=True)
			result[obj.id] = category_message_title_meta
		return result	
	def _get_shorten_name(self,cr,uid,ids,field_name,args,context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			size = obj.category_id.category_message_title_size
			title = len(obj.name)>size and obj.name[:size]+'...' or obj.name
			result[obj.id] = title
		return result	

	_columns={
			'name':fields.char("Title",size=128,required=True),
			'shorten_name':fields.function(_get_shorten_name,type="char", size=256,string="Shorten title"),
			'message_meta_display':fields.function(_get_message_meta_display,type="char", size=256,string="Meta"),
			'category_message_title_meta_display':fields.function(_get_category_message_title_meta_display,type="char", size=256,string="Category meta"),
			'category_id':fields.many2one('message.category','Category',required=True),
			'content':fields.text("Content"),
			'sequence':fields.integer("Display Sequence"),
			'is_display_name':fields.boolean('Display name?'),
			'image':fields.binary('Photo'), 
			'image_medium': fields.function(_get_image, fnct_inv=_set_image, string="Medium-sized photo", type="binary", multi="_get_image", store = {
				'document.page': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
				},
				help="Medium-sized photo of the page. It is automatically "\
						"resized as a 128x128px image, with aspect ratio preserved. "\
						"Use this field in form views or some kanban views."),
			'image_small': fields.function(_get_image, fnct_inv=_set_image,
				string="Small-sized photo", type="binary", multi="_get_image",
				store = {
					'document.page': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
					},
				help="Small-sized photo of the page. It is automatically "\
						"resized as a 64x64px image, with aspect ratio preserved. "\
						"Use this field anywhere a small image is required."),
			'fbbm':fields.char('Publisher',size=128),
			'read_times': fields.integer("Read Times"),
			'expire_date':fields.date('Expire Date'),
			'create_date':fields.datetime('Created on',select=True),
			'department_id':fields.many2one("hr.department","Department",domain=[('deleted','=',False)]),
			'create_uid':fields.many2one('res.users','Author',select=True),
			'write_date':fields.datetime('Modification date',select=True),
			'write_uid':fields.many2one('res.users','Last Contributor',select=True),
			'name_for_display':fields.function(_get_name_display,type="char",size=64,string="Name"),
			'sms_receiver_ids':fields.many2many('res.users',string='Default SMS Receivers'),
			'sms':fields.text('SMS',size=140),
			'is_allow_send_sms':fields.related('category_id','is_allow_send_sms',type="boolean",string="Allow send SMS?"),
			'is_allow_sms_receiver':fields.related('category_id','is_allow_send_sms',type="boolean",string="Allow specify sms receiver?"),
			}
	_defaults={
			'fbbm':_default_fbbm,
			'department_id':_default_department,
			'is_display_name':False
			}
	def onchange_category(self,cr,uid,ids,category_id,context=None):
		ret = {'value':{}}
		if category_id:
			message_category = self.pool.get('message.category').browse(cr,uid,category_id)
			sms_vals = {
					'is_allow_send_sms':message_category.is_allow_send_sms,
					'is_allow_sms_receiver':message_category.is_allow_sms_receiver,
					'sms_receiver_ids':[x.id for x in message_category.default_sms_receiver_ids],
					}
			ret['value'].update(sms_vals)
		return ret
	def create(self,cr,uid,vals,context=None):
		mid = super(Message,self).create(cr,uid,vals,context)
		sms = self.pool.get('sms.sms')
		message = self.pool.get('message.message').browse(cr,uid,mid,context=context)
		if message.is_allow_send_sms:
			to = ','.join([rid.mobile for rid in message.sms_receiver_ids if rid.mobile])
			if to:
				content = message.sms and message.sms or message.name
				sid = sms.create(cr,uid,{'to':to,'content':content,'model':'message.message','res_id':mid},context=context)
		return mid


