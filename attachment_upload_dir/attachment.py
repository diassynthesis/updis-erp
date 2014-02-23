__author__ = 'cysnake4713'
from openerp.osv import osv
from openerp.osv import fields


class IrAttachmentInherit(osv.osv):
    _inherit = 'ir.attachment'
    _columns = {
        'index_id': fields.integer('Index Id'),
        'index_model': fields.char('Index Model', 256),
    }
