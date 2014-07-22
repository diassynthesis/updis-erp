from openerp.osv import osv, fields
from lxml import etree
__author__ = 'cysnake4713'


class IrUiViewInherit(osv.osv):
    _inherit = 'ir.ui.view'

    def _type_field(self, cr, uid, ids, name, args, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context):
            # Get the type from the inherited view if any.
            if record.inherit_id:
                result[record.id] = record.inherit_id.type
            else:
                result[record.id] = etree.fromstring(record.arch.encode('utf8')).tag
        return result

    _columns = {
        'type': fields.function(_type_field, type='selection', selection=[
            ('tree', 'Tree'),
            ('form', 'Form'),
            ('mdx', 'mdx'),
            ('graph', 'Graph'),
            ('calendar', 'Calendar'),
            ('diagram', 'Diagram'),
            ('gantt', 'Gantt'),
            ('kanban', 'Kanban'),
            ('search', 'Search'),
            ('dir', 'Dir')], string='View Type', required=True, select=True, store=True),
    }