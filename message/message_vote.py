__author__ = 'cysnake4713'
from openerp.osv import fields, osv


class message_vote(osv.osv):

    _name = 'message.vote'
    _description = 'Message Vote'
    _columns = {
        'message_id': fields.many2one('message.message', 'Message', select=1,
                                      ondelete='cascade', required=True),
        'user_id': fields.many2one('res.users', 'User', select=1,
                                   ondelete='cascade', required=True),
        'up': fields.boolean('Is Up?'),
    }

    _defaults = {
        'up': True,
    }
