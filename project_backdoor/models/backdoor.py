__author__ = 'cysnake4713'
# coding=utf-8
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _


class BackDoor(osv.AbstractModel):
    _name = 'backdoor.wizard'

    def default_get(self, cr, uid, fields, context=None):
        result = super(BackDoor, self).default_get(cr, uid, fields, context=context)
        if context and 'active_model' in context and 'active_id' in context:
            origin_obj = self.pool.get(context['active_model'])
            origin_data = origin_obj.copy_data(cr, uid, context['active_id'], context=context)
            result.update(origin_data)
        return result

    def button_change(self, cr, uid, ids, context=None):
        pass
