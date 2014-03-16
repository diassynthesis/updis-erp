# -*- encoding: utf-8 -*-
__author__ = 'cysnake4713'

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _


class DocumentDirectoryAccess(osv.osv):
    _name = 'document.directory.access'

    _columns = {
        'group_id': fields.many2one('res.groups', 'Group', ondelete='cascade', select=True, required=True),
        'perm_read': fields.boolean('Directory / Sub File Read Access', readonly=True),
        'perm_write': fields.boolean('Sub File Write / Modify Access'),
        'perm_create_unlink': fields.boolean('Sub Directory Create / Unlink Access'),
        'directory_id': fields.many2one('document.directory', string='Related Directory ID', ondelete='cascade'),
    }

    _defaults = {
        'perm_read': True,
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
        action_id = action_obj.create(cr, 1, {
            'name': self_record.name,
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

    def delete_related_action(self, cr, uid, ids, context):
        directory_records = self.browse(cr, uid, ids, context)
        for directory_record in directory_records:
            action_id = directory_record.related_action_id.id
            self.write(cr, uid, ids, {'related_action_id': False})
            self.pool.get("ir.actions.act_window").unlink(cr, 1, action_id, context)
        return True

    # noinspection PyUnusedLocal
    def onchange_parent_id(self, cr, uid, ids, parent_id, context=None):
        ret = {'value': {}}
        if parent_id:
            parent_directory = self.browse(cr, uid, parent_id, context)
            new_group_ids = [(5,)]
            new_group_ids += [(0, 0, {'group_id': g.group_id.id,
                                      'perm_read': g.perm_read,
                                      'perm_write': g.perm_write,
                                      'perm_create_unlink': g.perm_create_unlink,
            }) for g in parent_directory.group_ids]
            # directory = self.browse(cr, uid, ids[0], context=context)
            # directory.write({'group_ids': (5), }, context=context)
            # self.write(cr, uid, ids[0], {'group_ids': (2, [g.id for g in directory.group_ids])}, context=context)
            sms_vals = {
                'group_ids': new_group_ids,
            }
            # noinspection PyTypeChecker
            ret['value'].update(sms_vals)
        return ret

    def check_directory_privilege(self, cr, uid, obj, method, context):
        user = self.pool.get('res.users').read(cr, 1, uid, ['groups_id'], context)
        user_group = user['groups_id']
        flag = False
        for group in obj.group_ids:
            if group.group_id.id in user_group and group[method] is True:
                flag = True
                break
        return flag

    def _check_group_create_unlink_privilege(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            if not self.check_directory_privilege(cr, uid, directory, 'perm_unlink', context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Create / Unlink some of the directories.'))

    def _check_group_write_privilege(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            if not self.check_directory_privilege(cr, uid, directory, 'perm_write', context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Write some of the directories.'))

    def create(self, cr, uid, vals, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            self._check_group_create_unlink_privilege(cr, uid, vals, context)
        return super(DocumentDirectoryInherit, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            self._check_group_create_unlink_privilege(cr, uid, ids, context)
        return super(DocumentDirectoryInherit, self).unlink(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            self._check_group_write_privilege(cr, uid, ids, context)
        return super(DocumentDirectoryInherit, self).write(cr, uid, ids, vals, context)


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
