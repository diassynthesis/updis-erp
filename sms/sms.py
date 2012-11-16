from osv import osv,fields

class sms(osv.Model):
	_name="sms.sms"
	_columns={
		'content':fields.text("Content",size=128),
		'from':fields.char("From",size=64),
		'to':fields.char('To',size=64),
		'sent_date':fields.datetime("Send date"),	
		'model':fields.char("Related Document Model",size=128,select=1),
		'res_id':fields.integer('Related Document ID',select=1),		
	}