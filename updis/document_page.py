from osv import osv,fields

class document_page(osv.osv):
	_inherit="document.page"
	_columns = {
		'display_name':fields.boolean("Dsplay Name?",help="Check this if you don't want to display your name"),
		'read_times': fields.integer("Read times"),
	}