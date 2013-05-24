#encoding:utf-8
import logging
from openerp.osv import osv, fields


class mail_message(osv.Model):
    """Add anoanymouse comment."""
    _inherit = "mail.message"
    _order = "date desc"

    _columns = {
    "is_anonymous": fields.boolean(u"Anonymous"),
    }
    _defaults = {
    "is_anonymous": False,
    }

    def _message_read_dict_postprocess(self, cr, uid, messages, message_tree, context=None):
        ret = super(mail_message, self)._message_read_dict_postprocess(cr, uid, messages, message_tree, context=context)
        # import pdb;pdb.set_trace()
        for message_dict in messages:
            message_id = message_dict.get('id')
            message = message_tree[message_id]
            if message.is_anonymous:
                author_id = message_dict['author_id']
                message_dict.update({
                'author_id': (author_id[0], u'匿名用户'), })
        return ret

    def _message_read_dict(self, cr, uid, message, parent_id=False, context=None):
        ret = super(mail_message, self)._message_read_dict(cr, uid, message, parent_id=parent_id, context=context)
        ret.update({
        'is_anonymous': message.is_anonymous,
        })
        return ret
