from osv import osv,fields

class internal_home_menu(osv.osv):
	_name = "internal.home.menu"
	_inherit = "ir.ui.menu"
	_columns = {	
        'child_id' : fields.one2many('internal.home.menu', 'parent_id','Child IDs'),
        'parent_id': fields.many2one('internal.home.menu', 'Parent Menu', select=True),
	}