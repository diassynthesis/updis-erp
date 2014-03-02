# -*- encoding: utf-8 -*-
import base64
import cStringIO
from zipfile import ZipFile

__author__ = 'cysnake4713'

from openerp.osv import osv
from openerp.osv import fields
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
                                      'perm_create': g.perm_create,
                                      'perm_unlink': g.perm_unlink, }) for g in parent_directory.group_ids]
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

    # noinspection PyUnusedLocal
    def _get_file_size(self, cr, uid, ids, field_name, arg, context):
        result = dict.fromkeys(ids, False)
        for attachment in self.browse(cr, uid, ids, context=context):
            result[attachment.id] = attachment.file_size / (1024.0 * 1024.0)
        return result

    _columns = {
        'file_size_human': fields.function(_get_file_size, type='float', digits=[10, 3], method=True, string='File Size Human (MB)'),
    }

    _sql_constraints = [
        ('dirname_uniq', 'unique (name,parent_id,res_model,res_id)', 'The directory name must be unique !'),
    ]

    def on_change_name(self, cr, uid, ids, context=None):
        attachment = self.browse(cr, uid, ids, context)[0]
        self.write(cr, uid, attachment.id, {'name': attachment.datas_fname}, context)
        return True


class IrAttachmentDownloadWizard(osv.osv_memory):
    _name = "ir.attachment.download.wizard"

    def default_get(self, cr, uid, field_list, context=None):
        """
        This function gets default values
        """
        res = super(IrAttachmentDownloadWizard, self).default_get(cr, uid, field_list, context=context)
        if context is None:
            context = {}
        record_ids = context and context.get('active_ids', False) or False
        if not record_ids:
            return res
        attachment_obj = self.pool.get('ir.attachment')
        attachments = attachment_obj.browse(cr, uid, record_ids, context=context)
        total_size = reduce(lambda x, y: y.file_size + x, attachments, 0)
        # total_size = reduce(self.test, attachments)
        # TODO: need some much useful limit
        if total_size > 200 * 1024 * 1024:
            raise osv.except_osv(_('Warning!'), _('Too Large the file will be generate!'))
        if len(record_ids) > 20:
            raise osv.except_osv(_('Warning!'), _('Too Many Attachments you choose!'))
        if 'attachment_ids' in field_list:
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

    _defaults = {
        'state': 'choose',
    }

    def button_download_files(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_ids = context and context.get('active_ids', False) or False
        attachments = self.pool.get('ir.attachment').browse(cr, uid, record_ids, context)
        buf = cStringIO.StringIO()
        with ZipFile(buf, 'w') as zip_obj:
            for attachment in attachments:
                if attachment.datas is not False:
                    file_name = attachment.name
                    file_data = attachment.datas
                    zip_obj.writestr(file_name, file_data)
        # tools.trans_export(lang, mods, buf, this.format, cr)
        filename = u"附件.zip"
        out = base64.encodestring(buf.getvalue())
        buf.close()
        self.write(cr, uid, ids, {'state': 'get',
                                  'data': out,
                                  'name': filename}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment.download.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
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
