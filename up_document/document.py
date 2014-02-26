# -*- encoding: utf-8 -*-
__author__ = 'cysnake4713'

from openerp.osv import osv
from openerp.osv import fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _


class DocumentDirectoryAccess(osv.osv):
    _name = 'document.directory.access'

    _columns = {
        'group_id': fields.many2one('res.groups', 'Group', ondelete='cascade', select=True, required=True),
        'perm_read': fields.boolean('Directory & File Read Access', readonly=True),
        'perm_write': fields.boolean('Directory Write & File Modify Access'),
        'perm_create': fields.boolean('Sub Directory Create Access'),
        'perm_unlink': fields.boolean('Sub Directory Delete Access'),
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


    def delete_related_action(self, cr, uid, ids, context):
        directory_records = self.browse(cr, uid, ids, context)
        for directory_record in directory_records:
            action_id = directory_record.related_action_id.id
            self.write(cr, uid, ids, {'related_action_id': False})
            self.pool.get("ir.actions.act_window").unlink(cr, 1, action_id, context)
        return True

    def onchange_parent_id(self, cr, uid, ids, parent_id, context=None):
        ret = {'value': {}}
        if parent_id:
            parent_directory = self.browse(cr, uid, parent_id, context)
            new_group_ids = [(5,)]
            new_group_ids += [(0, 0, {'group_id': g.group_id.id,
                                      'perm_read': g.perm_read,
                                      'perm_write': g.perm_write,
                                      'perm_create': g.perm_create,
                                      'perm_unlink': g.perm_unlink, }) for g in parent_directory.group_ids]
            # directory = self.browse(cr, uid, ids[0], context=context)
            # directory.write({'group_ids': (5), }, context=context)
            # self.write(cr, uid, ids[0], {'group_ids': (2, [g.id for g in directory.group_ids])}, context=context)
            sms_vals = {
                'group_ids': new_group_ids,
            }
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

    def _check_group_unlink_privilege(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            if not self.check_directory_privilege(cr, uid, directory, 'perm_unlink', context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Unlink some of the directories.'))

    def _check_group_write_privilege(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            if not self.check_directory_privilege(cr, uid, directory, 'perm_write', context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Write some of the directories.'))

    def _check_group_create_privilege(self, cr, uid, vals, context=None):
        parent_id = vals['parent_id']
        if parent_id:
            directory = self.browse(cr, uid, parent_id, context=context)
            if not self.check_directory_privilege(cr, uid, directory, 'perm_create', context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Create the directory.'))

    def create(self, cr, uid, vals, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            self._check_group_create_privilege(cr, uid, vals, context)
        return super(DocumentDirectoryInherit, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            self._check_group_unlink_privilege(cr, uid, ids, context)
        return super(DocumentDirectoryInherit, self).unlink(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            self._check_group_write_privilege(cr, uid, ids, context)
        return super(DocumentDirectoryInherit, self).write(cr, uid, ids, vals, context)


class IrAttachmentInherit(osv.osv):
    _inherit = 'ir.attachment'

    def _check_group_unlink_privilege(self, cr, uid, ids, context=None):
        directory_obj = self.pool.get('document.directory')
        for attachment in self.browse(cr, uid, ids, context):
            if attachment.parent_id:
                if not directory_obj.check_directory_privilege(cr, uid, attachment.parent_id, 'perm_write', context):
                    raise osv.except_osv(_('Warning!'), _('You have no privilege to Unlink some of the attachments.'))

    def _check_group_write_privilege(self, cr, uid, ids, context=None):
        directory_obj = self.pool.get('document.directory')
        for attachment in self.browse(cr, uid, ids, context):
            if attachment.parent_id:
                if not directory_obj.check_directory_privilege(cr, uid, attachment.parent_id, 'perm_write', context):
                    raise osv.except_osv(_('Warning!'), _('You have no privilege to Write some of the attachments.'))

    def _check_group_create_privilege(self, cr, uid, vals, context=None):
        directory_obj = self.pool.get('document.directory')
        parent_id = vals['parent_id'] if 'parent_id' in vals else (context['parent_id'] if 'parent_id' in context else None)
        if parent_id:
            directory = directory_obj.browse(cr, uid, parent_id, context=context)
            if not directory_obj.check_directory_privilege(cr, uid, directory, 'perm_write', context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to create attachments in this directory.'))

    def create(self, cr, uid, vals, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            self._check_group_create_privilege(cr, uid, vals, context)
        return super(IrAttachmentInherit, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            self._check_group_unlink_privilege(cr, uid, ids, context)
        return super(IrAttachmentInherit, self).unlink(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            self._check_group_write_privilege(cr, uid, ids, context)
        return super(IrAttachmentInherit, self).write(cr, uid, ids, vals, context)


    def _get_file_size(self, cr, uid, ids, field_name, arg, context):
        """
            Either way, it must return a dictionary of values of the form
            {'id_1_': 'value_1_', 'id_2_': 'value_2_',...}.

            If multi is set, then field_name is replaced by field_names:
            a list of the field names that should be calculated.
            Each value in the returned dictionary is also a dictionary from field name to value.
            For example, if the fields 'name', and 'age' are both based on the vital_statistics function,
            then the return value of vital_statistics might look like this when ids is [1, 2, 5]:
            {
                1: {'name': 'Bob', 'age': 23},
                2: {'name': 'Sally', 'age', 19},
                5: {'name': 'Ed', 'age': 62}
            }
        """
        result = dict.fromkeys(ids, False)
        for attachment in self.browse(cr, uid, ids, context=context):
            result[attachment.id] = attachment.file_size / (1024.0 * 1024.0)
        return result

    _columns = {
        'file_size_human': fields.function(_get_file_size, type='float', digits=[10, 3], method=True, string='File Size Human (MB)'),
    }


class IrAttachmentDownloadWizard(osv.osv_memory):
    _name = "ir.attachment.download.wizard"

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(IrAttachmentDownloadWizard, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_ids = context and context.get('active_ids', False) or False
        if not record_ids:
            return res
        attachment_obj = self.pool.get('ir.attachment')
        attachments = attachment_obj.browse(cr, uid, record_ids, context=context)
        if 'attachment_ids' in fields:
            res['attachment_ids'] = [a.id for a in attachments]
        return res


    _columns = {
        'name': fields.char('File Name', readonly=True),
        # 'format': fields.selection([('csv', 'CSV File'),
        #                             ('po', 'PO File'),
        #                             ('tgz', 'TGZ Archive')], 'File Format', required=True),
        'attachment_ids': fields.many2many('ir.attachment', 'rel_attachment_download_wizard', 'wizard_id', 'attachment_id', string='Attachments'),
        'data': fields.binary('File', readonly=True),
        'state': fields.selection([('choose', 'choose'),  # choose language
                                   ('get', 'get')])  # get the file
    }

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
