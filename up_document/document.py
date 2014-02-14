# -*- encoding: utf-8 -*-
__author__ = 'cysnake4713'

from openerp.osv import osv
from openerp.osv import fields
from openerp import SUPERUSER_ID


class DocumentDirectoryAccess(osv.osv):
    _name = 'document.directory.access'
    _columns = {
        'group_id': fields.many2one('res.groups', 'Group', ondelete='cascade', select=True, required=True),
        'perm_read': fields.boolean('Read Access'),
        'perm_write': fields.boolean('Write Access'),
        'perm_create': fields.boolean('Create Access'),
        'perm_unlink': fields.boolean('Delete Access'),
        'directory_id': fields.many2one('document.directory', string='Related Directory ID', ondelete='cascade'),
    }


class DocumentDirectoryAction(osv.osv_memory):
    _name = 'document.directory.action.wizard'
    _columns = {
        'name': fields.char(size=512, string='Action Name'),
    }

    def create_related_action(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        self_record = self.browse(cr, uid, ids[0], context)
        action_obj = self.pool.get("ir.actions.act_window")
        action_id = action_obj.create(cr, 1, {'name': self_record.name,
                                              'res_model': 'ir.attachment',
                                              'view_type': 'form',
                                              'view_mode': 'tree',
                                              'domain': [('parent_id', 'child_of', record_id)],
                                              'context': {
                                                  'tree_view_ref': 'up_document.view_document_file_public_tree',
                                                  'group_by': 'parent_id'},
        }, context=context)

        return self.pool.get("document.directory").write(cr, uid, [record_id], {'related_action_id': action_id},
                                                         context=context)


class DocumentDirectoryInherit(osv.osv):
    _inherit = 'document.directory'
    _columns = {
        'group_ids': fields.one2many('document.directory.access', 'directory_id', string='Access'),
        'related_action_id': fields.many2one('ir.actions.act_window', string='Related Menu Action', ondelete='cascade'),
    }

    def get_public_directory(self, cr, uid, context=None):
        directory_id = self.pool.get('ir.model.data').get_object_reference(cr, SUPERUSER_ID, 'up_document',
                                                                           'doc_direct_000001')
        domain = [('id', 'child_of', directory_id[1]), ('id', '!=', directory_id[1])]
        # view_form = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'ir.ui.view'),
        #                                                           ('name', '=',
        #                                                            'project_contract_invoice_form_menu')],
        #                                                   context=context)
        # view_form_id = self.pool.get('ir.model.data').read(cr, 1, view_form[0], ['res_id'])
        #
        # view_tree = self.pool.get('ir.model.data').search(cr, 1, [('model', '=', 'ir.ui.view'),
        #                                                           ('name', '=',
        #                                                            'project_contract_invoice_tree_menu')],
        #                                                   context=context)
        # view_tree_id = self.pool.get('ir.model.data').read(cr, 1, view_tree[0], ['res_id'])

        return {
            'name': u'公共目录管理',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'document.directory',
            'target': 'current',
            'domain': domain,
            'context': context,
            # 'views': [(view_tree_id['res_id'], 'tree'), (view_form_id['res_id'], 'form')],
        }

    def delete_related_action(self, cr, uid, ids, context):
        directory_records = self.browse(cr, uid, ids, context)
        for directory_record in directory_records:
            action_id = directory_record.related_action_id.id
            self.write(cr, uid, ids, {'related_action_id': False})
            self.pool.get("ir.actions.act_window").unlink(cr, 1, action_id, context)
        return True


# class FileConfig(osv.osv):
#     _name = 'sfile.file.config'
#     _description = 'File Config'
#
#     _columns = {
#         'name': fields.char(size=256, string='Name'),
#         'value': fields.char(size=512, string='Value'),
#     }
#
#
# class FileTag(osv.osv):
#     _name = 'sfile.file.tag'
#     _description = 'File Tag'
#
#     _columns = {
#         'name': fields.char(size=256, string='Tag Name'),
#     }
