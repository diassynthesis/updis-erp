from osv import fields,osv

class updis_department(osv.osv):
	_description = "UPDIS Department"
	_inherit="hr.department"
	_columns={
		"deleted":fields.boolean("Removed"),
		'sequence':fields.integer("Display Sequence"),
		'display_in_front':fields.boolean("Display in Front Page"),
	}
	_defaults = {
		"deleted": 0,
		'sequence': 10,
		'display_in_front':True,
	}
	_order = 'sequence,id'
