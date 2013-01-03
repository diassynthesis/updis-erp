#-*- encoding:UTF-8
from osv import osv,fields
import tools


class document_page(osv.osv):
	_log_access=False
	_inherit = ['document.page','mail.thread', 'ir.needaction_mixin']
	_name="document.page"
	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image)
		return result
	
	def _set_image(self, cr, uid, id, field_name, value, args, context=None):
		return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

	def _default_department(self,cr,uid,context=None):
		user_ids = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		if user_ids:
			return self.pool.get('hr.employee').browse(cr,uid,user_ids[0]).department_id.id
	def _default_fbbm(self,cr,uid,context=None):
		user_ids = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		if user_ids:
			return self.pool.get('hr.employee').browse(cr,uid,user_ids[0]).department_id.name
	def _category_allow_send_sms(self, cr, uid, ids, field_name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = obj.parent_id.allow_send_sms
		return result
	def _hide_sms_receivers(self,cr,uid,ids,field_name,args,context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			if obj.type=='content' and not obj.parent_id:
				result[obj.id]=True
			elif obj.type=='content' and obj.category_allow_send_sms:
				result[obj.id]=False
			elif obj.type=="category" and obj.allow_send_sms:
				result[obj.id]=False
			else:
				result[obj.id]=True			
		return result
	def _name_display(self,cr,uid,ids,field_name,args,context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = obj.display_name and obj.write_uid.name or u'匿名用户'
		return result	

	_columns = {
		# 'content': fields.html("Content"),
		'photo_news':fields.boolean("Photo News?"),
		'image':fields.binary("Photo",
			help="This field holds the image used as photo for the news."),
		'image_medium': fields.function(_get_image, fnct_inv=_set_image,
			string="Medium-sized photo", type="binary", multi="_get_image",
			store = {
				'document.page': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Medium-sized photo of the page. It is automatically "\
				 "resized as a 128x128px image, with aspect ratio preserved. "\
				 "Use this field in form views or some kanban views."),
		'image_small': fields.function(_get_image, fnct_inv=_set_image,
			string="Smal-sized photo", type="binary", multi="_get_image",
			store = {
				'document.page': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
			},
			help="Small-sized photo of the page. It is automatically "\
				 "resized as a 64x64px image, with aspect ratio preserved. "\
				 "Use this field anywhere a small image is required."),
		'anonymous':fields.boolean("Anonymous",help="Check this if you want to do anonymous publishing"),
		'description':fields.text("Description",help="Description of the category",size=128),
		'read_times': fields.integer("Read Times"),
		'department_id':fields.many2one("hr.department","Department",domain=[('deleted','=',False)]),
		'display_position':fields.selection(
			[("shortcut","Shortcuts"),("content_left","Content Left"),("content_right","Content Right")]
			,"Display Position"),
		'display_in_departments':fields.many2many("hr.department",string="Display in Departments"),
		'sequence':fields.integer("Display Sequence"),
		'fbbm':fields.char("Publisher",size=128,help="Pubsher, by default it's user's department."),
		'display_source':fields.boolean("Display Publisher?",help="If checked, fbbm will be display in internal home page"),
		'display_name':fields.boolean("Display Name?",help="If checked, author name will be display in internal home page"),
		'name_display':fields.function(_name_display,type="char",size=64,string="Name"),
		'allow_send_sms':fields.boolean("Allow Send SMS?",help="If checked, user can choose to send sms for a page"),
		'sms_receivers':fields.many2many("hr.employee","document_page_user_rel","page_id","user_id","SMS Receiver"),
		'category_allow_send_sms':fields.function(_category_allow_send_sms,type='boolean',string="Category Allow Send SMS?"),
		'hide_sms_receivers':fields.function(_hide_sms_receivers,type="boolean"),
		'sms_content':fields.text("SMS Content",size=256),
	}
	_defaults={
		'sequence':10,	
		'department_id':_default_department,
		'display_source':True,
		'fbbm':_default_fbbm,
		'read_times':0,
		'anonymous':False,
		'hide_sms_receivers':True
	}
	_order='sequence,write_date desc,id'

	def onchange_photo_news(self,cr,uid,ids,photo_news):
		res = {}		
		return res
	def onchange_image(self,cr,uid,ids,image_medium):
		res = {}
		if image_medium:
			res['value']={'photo_news':True}
		return res
	def onchange_department_id(self,cr,uid,ids,department_id,fbbm,context=None):
		res = {}
		if department_id and not fbbm:
			department = self.pool.get("hr.department").browse(cr, uid, department_id, context=context)
			res['value'] = {
				'fbbm': department.name,
			}
		return res
	def onchange_parent_id(self, cr, uid, ids, parent_id, content, p_type, context=None):
		res = super(document_page,self).onchange_parent_id(cr,uid,ids,parent_id,content,context)
		category = self.pool.get('document.page').browse(cr,uid,parent_id)		
		if p_type=='content':
			value = res.setdefault('value',{})
			value['hide_sms_receivers'] = not category.allow_send_sms
			value['sms_receivers'] = [u.id for u in category.sms_receivers]
		return res
	def onchange_allow_send_sms(self,cr,uid,ids,allow_send_sms,context=None):
		return {
			'value':{
				'hide_sms_receivers':not allow_send_sms,
			}
		}
