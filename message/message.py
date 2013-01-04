from osv import osv,fields
class Message(osv.Model):
	#TODO: turn off for data import only
	_log_access=False
	_name="message.message"
	_order="name"
	def _default_fbbm(self,cr,uid,context=None):
		user_ids = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		if user_ids:
			return self.pool.get('hr.employee').browse(cr,uid,user_ids[0]).department_id.name
	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image)
		return result

	def _get_name_display(self,cr,uid,ids,field_name,args,context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = obj.is_anonymous and u'匿名用户' or obj.write_uid.name 
		return result	
	_columns={
			'name':fields.char("Title",size=128,required=True),
			'category_id':fields.many2one('message.category','Category',required=True),
			'content':fields.html("Content"),
			'sequence':fields.integer("Display Sequence"),
			'is_anonymous':fields.boolean('Publish anonymously'),
			'image':fields.binary('Photo'),
			'fbbm':fields.char('Publisher',size=128),
			'read_times': fields.integer("Read Times",readonly=True),
			'expire_date':fields.datetime('Expire Date'),
			'create_date':fields.datetime('Created on',select=True,readonly=True),
			#'department_id':fields.many2one("hr.department","Department",domain=[('deleted','=',False)]),
			'create_uid':fields.many2one('res.users','Author',select=True,readonly=True),
			'write_date':fields.datetime('Modification date',select=True,readonly=True),
			'write_uid':fields.many2one('res.users','Last Contributor',select=True),
			'name_for_display':fields.function(_get_name_display,type="char",size=64,string="Name"),
			}
	_defaults={
			'fbbm':_default_fbbm,
			'is_anonymous':False
			}

class MessageCategory(osv.Model):
	_name="message.category"
	_order="name"
	_column={
			'name':fields.char("Title",size=128),
			'is_anonymous_allowed':fields.boolean('Allow publish messages anonymously?'),
			'is_display_fbbm':fields.boolean('Display source?')
			'is_display_read_times':fields.boolean('Display read times?')
			'display_position':fields.selection(
				[("shortcut","Shortcuts"),("content_left","Content Left"),("content_right","Content Right")]
				,"Display Position"),
			'display_in_departments':fields.many2many("hr.department",string="Display in Departments"),
			}
	_defaults={
			'is_display_source':True,
			'is_anonymous_allowed':False
			}

