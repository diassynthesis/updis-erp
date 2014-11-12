__author__ = 'cysnake4713'

# coding=utf-8
from openerp.osv import osv, fields


class ResUsersInherti(osv.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    _columns = {
        'sign_image': fields.binary("Sign Image",
                                    help="This field holds the image used as siganture for this contact"),
    }

    def get_user_image(self, cr, uid, user_id, context=None):
        user = self.browse(cr, 1, user_id, context)
        if user.sign_image:
            return user.sign_image
        else:
            return None