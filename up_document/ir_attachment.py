# -*- encoding: utf-8 -*-
import hashlib
import os
import random
import time

__author__ = 'cysnake4713'
import base64
import cStringIO
from zipfile import ZipFile

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _


class IrAttachmentInherit(osv.osv):
    _inherit = 'ir.attachment'

    def _check_group_unlink_privilege(self, cr, uid, ids, context=None):
        directory_obj = self.pool.get('document.directory')
        for attachment in self.browse(cr, uid, ids, context):
            if attachment.parent_id:
                if not directory_obj.check_directory_privilege(cr, uid, attachment.parent_id, 'perm_write', context,
                                                               res_model=attachment.res_model,
                                                               res_id=attachment.res_id):
                    raise osv.except_osv(_('Warning!'), _('You have no privilege to Unlink some of the attachments.'))

    def _check_group_write_privilege(self, cr, uid, ids, context=None):
        directory_obj = self.pool.get('document.directory')
        for attachment in self.browse(cr, uid, ids, context):
            if attachment.parent_id:
                if not directory_obj.check_directory_privilege(cr, uid, attachment.parent_id, 'perm_write', context,
                                                               res_model=attachment.res_model,
                                                               res_id=attachment.res_id):
                    raise osv.except_osv(_('Warning!'), _('You have no privilege to Write some of the attachments.'))

    def _check_group_create_privilege(self, cr, uid, vals, context=None):
        directory_obj = self.pool.get('document.directory')
        parent_id = vals['parent_id'] if 'parent_id' in vals else (context['parent_id'] if 'parent_id' in context else None)
        if parent_id:
            directory = directory_obj.browse(cr, uid, parent_id, context=context)
            if not directory_obj.check_directory_privilege(cr, uid, directory, 'perm_write', context, res_model=vals.get('res_model', None),
                                                           res_id=vals.get('res_id', None)):
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
        ('filename_unique', 'unique (name,parent_id,res_model,res_id)', 'The file name in directory must be unique !'),
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
        for attach in attachments:
            if attach.file_size > 10 * 1024 * 1024:
                raise osv.except_osv(_('Warning!'), _('Some of the selected file is large than 10MB!'))
        # TODO: need some much useful limit
        if total_size > 50 * 1024 * 1024:
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
                    zip_obj.writestr(file_name.encode('gbk'), base64.decodestring(file_data))
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
