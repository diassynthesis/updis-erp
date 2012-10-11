# -*- coding: utf-8 -*-
from osv import osv,fields

class RoleType(osv.osv):
	"""docstring for Role"""
	_name="tm.roletype"
	_columns={
		"name":fields.char("Role Name",required=True, size=64),
		"attendance_ids":fields.many2many("res.users","attendance_role_type_rel","roletype_id","uid","Members taking this role"),
	}
RoleType()

class Attendance(osv.osv):
	"""docstring for Attendee"""
	_name="tm.attendance"
	_description="Attendance"
	_columns = {
		"member_id":fields.many2one("res.users","TM Member"),
		"role_id":fields.many2one("tm.roletype","TM Role"),
		'agenda_id':fields.many2one("tm.agenda","TM Agenda"),
		"theme":fields.char("Theme",required=False,size=128),
		"cc_title":fields.char("CC Speech Title",required=False,size=256)
	}
Attendance()

class Agenda(osv.osv):
	"""docstring for Agenda"""
	_name="tm.agenda"
	_order="sequence"
    _log_create = True
    _date_name = "date_start"
	_columns={
		'tom':fields.many2one("res.users", 'TOM'),
		'attendees':fields.many2many("tm.attendance","agenda_id","attendance_id","Attendees"),
		'date_start': fields.datetime('Starting Time',select=True),
        'date_end': fields.datetime('Ending Time',select=True),
        "sequence": fields.integer("Sequence",select=True,help=""),
        "state":fields.selection([("draft","Draft"),("in progress","In Progress"),("done","Done"),("outdated","Outdated")],'State', readonly=True, required=True)
	}	
	_default={
		"sequence":1,
	}
Agenda()