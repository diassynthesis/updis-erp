#encoding:utf-8
import logging
from openerp.osv import osv,fields

class mail_message(osv.Model):
	"""Add anoanymouse comment."""
	_inherit="mail.message"
	_columns={
			"is_anonymous":fields.boolean(u"Anonymous"),
			'legacy_message_id':fields.char("Legacy message id",size=128),
			}
	_defaults={
			"is_anonymous":False,
			}
	def process_legacy_comment(self,cr,uid,context=None):
		comment = self.pool.get('mail.message')
		message = self.pool.get('message.message')
		model_data = self.pool.get('ir.model.data')
		comment_ids = comment.search(cr,uid,[('legacy_message_id','!=',False)],context=context)
		for comment_obj in self.browse(cr,uid,comment_ids,context=context):	
			md_ids = model_data.search(cr,uid,[('model','=','message.message'),('name','=',comment_obj.legacy_message_id)])
			for model_data_obj in model_data.browse(cr,uid,md_ids,context=context):
				self.write(cr,uid,[comment_obj.id],{
					'res_id':model_data_obj.res_id,
					'legacy_message_id':False
					})
				logging.getLogger('mail.message').warning("Updated Comment! for %s"%comment_obj.res_id)
	def _message_read_dict_postprocess(self, cr, uid, messages, message_tree, context=None):
		ret = super(mail_message,self)._message_read_dict_postprocess(cr, uid, messages, message_tree, context=context)
		for message_dict in messages:
			message_id = message_dict.get('id')
			message = message_tree[message_id]
			if message.is_anonymous:
				author_id = message_dict['author_id']
				message_dict.update({
					'author_id':(author_id[0],u'匿名用户'),																		})
		return ret
	def _message_read_dict(self, cr, uid, message, parent_id=False, context=None):		
		ret = super(mail_message,self)._message_read_dict(cr, uid, message, parent_id=parent_id, context=context)
		ret.update({
			'is_anonymous':message.is_anonymous,
			})
		return ret
