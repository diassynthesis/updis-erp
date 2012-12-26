from openerp.osv import osv,fields

class mail_message(osv.Model):
	"""Add anoanymouse comment."""
	_inherit="mail.message"
	_columns={
			"is_anonymous":fields.boolean(u"Anonymous"),
		}
	_defaults={
			"is_anonymous":False,
		}

