from osv import osv,fields

class res_users(osv.osv):
	_inherit = "res.users"
	_columns = {
		'sign_image':fields.binary("Sign Image",
            help="This field holds the image used as siganture for this contact"),
	}