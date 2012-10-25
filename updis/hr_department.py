from osv import fields,osv

class updis_department(osv.osv):
	_description = "UPDIS Department"
	_inherit="hr.department"
	_columns={
		"deleted":fields.boolean("Removed Department"),		
	}
	_defaults = {
		"deleted": 0,
	}
