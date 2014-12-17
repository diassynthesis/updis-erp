__author__ = 'cysnake4713'
# coding=utf-8
import hashlib
import os
import re
import shutil

from openerp import tools
from openerp.osv.orm import Model

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _logger


class DocumentDirectoryInherit(osv.osv):
    _inherit = 'document.directory'
    _columns = {
        'is_encrypt': fields.boolean('Is Encrypt'),
    }

    def button_update_sub_encrypt(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            sub_ids = self.search(cr, uid, [('id', 'child_of', directory.id)], context=context)
            attachment_ids = self.pool['ir.attachment'].search(cr, uid, [('parent_id', 'in', sub_ids)], context=context)
            if directory.is_encrypt:
                self.pool['ir.attachment'].convert_encrypt_state(cr, uid, attachment_ids, is_encrypt=True, context=context)
            else:
                self.pool['ir.attachment'].convert_encrypt_state(cr, uid, attachment_ids, is_decrypt=True, context=context)
            sub_ids.remove(directory.id)
            self.write(cr, uid, sub_ids, {'is_encrypt': directory.is_encrypt}, context=context)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        self._check_group_write_privilege(cr, uid, ids, context)
        return super(osv.osv, self).write(cr, uid, ids, vals, context)


class IrAttachmentInherit(osv.osv):
    _inherit = 'ir.attachment'

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                is_encrypted = attach.parent_id.is_encrypt
                if is_encrypted:
                    result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size, is_encrypted)
                else:
                    result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _data_set(self, cr, uid, id, name, qqfile, arg, context=None):
        # We dont handle setting data to null
        if not qqfile:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        file_size = 0
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            file_name, file_size = self._file_write(cr, uid, location, qqfile, attach.parent_id.is_encrypt)
            super(Model, self).write(cr, uid, [id], {'store_fname': file_name, 'file_size': file_size}, context=context)
        else:
            super(Model, self).write(cr, uid, [id], {'db_datas': qqfile.read(), 'file_size': file_size}, context=context)
        return True


    _columns = {
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    }

    def convert_encrypt_state(self, cr, uid, ids, is_encrypt=False, is_decrypt=False, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        attachments = self.browse(cr, uid, ids, context)
        for attachment in attachments:
            if is_encrypt:
                old_path = self._full_path(cr, uid, location, attachment.store_fname)
                new_path = self._full_path(cr, uid, location, attachment.store_fname, is_encrypted=True)
            if is_decrypt:
                old_path = self._full_path(cr, uid, location, attachment.store_fname, is_encrypted=True)
                new_path = self._full_path(cr, uid, location, attachment.store_fname)
            if os.path.exists(old_path):
                dirname = os.path.dirname(new_path)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                shutil.move(old_path, new_path)

    def _full_path(self, cr, uid, location, path, is_encrypted=False):
        # location = 'file:filestore'
        assert location.startswith('file:'), "Unhandled filestore location %s" % location
        location = location[5:]

        # sanitize location name and path
        location = re.sub('[.]', '', location)
        location = location.strip('/\\')

        path = re.sub('[.]', '', path)
        path = path.strip('/\\')

        return os.path.join(tools.config['root_path'], location, cr.dbname, 'encrypted' if is_encrypted else '', path)

    def _file_write(self, cr, uid, location, qqfile, is_encrypted=False):
        sha1 = hashlib.sha1()
        while True:
            # read 16MB
            block = qqfile.read(16 * 1024 * 1024)
            if block:
                sha1.update(block)
            else:
                break
        fname = sha1.hexdigest()
        # scatter files across 1024 dirs
        # we use '/' in the db (even on windows)
        fname = fname[:3] + '/' + fname
        full_path = self._full_path(cr, uid, location, fname, is_encrypted)
        file_size = 0
        try:
            qqfile.seek(0, 0)
            dirname = os.path.dirname(full_path)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            qqfile.save(full_path)
            file_size = os.path.getsize(full_path)
        except IOError:
            _logger.error("_file_write writing %s", full_path)
        return fname, file_size

    def _update_encrypted_state(self, cr, uid, ids, new_parent, context=None):
        directory_obj = self.pool['document.directory']
        new_dir = directory_obj.browse(cr, uid, new_parent, context)
        if new_dir.is_encrypt:
            self.convert_encrypt_state(cr, uid, ids, is_encrypt=True, context=context)
        else:
            self.convert_encrypt_state(cr, uid, ids, is_decrypt=True, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        result = super(IrAttachmentInherit, self).write(cr, uid, ids, vals, context)
        if 'parent_id' in vals:
            self._update_encrypted_state(cr, uid, ids, vals['parent_id'], context=None)
        return result