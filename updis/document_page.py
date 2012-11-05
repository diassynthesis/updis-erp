from osv import osv,fields

class document_page(osv.osv):
	_inherit="document.page"
	_columns = {
		# 'content': fields.html("Content"),
		'display_name':fields.boolean("Display Name?",help="Check this if you don't want to display your name"),
		'description':fields.text("Description",help="Description of the category",size=128),
		'read_times': fields.integer("Read Times"),
		'department_id':fields.many2one("hr.department","Department"),
		'display_position':fields.selection(
			[('top','Top'),('top','Top'),("menu","Top menu"),("shortcut","Shortcuts"),("content_left","Content Left"),("content_right","Content Right")]
			,"Display Position"),
		'sequence':fields.integer("Display Sequence"),
	}
	_defaults={
		'sequence':10,		
	}