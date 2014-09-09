# -*- encoding: utf-8 -*-
import datetime
import hashlib
import os
import random
from openerp import tools
import shutil
from osv.orm import Model

__author__ = 'cysnake4713'

import zipfile

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _, _logger
from openerp.addons.document.document import document_file
from openerp.tools import config


def monkey_create(self, cr, uid, vals, context=None):
    def get_partner_id(cri, uidi, res_model, res_id, contexts=None):
        """ A helper to retrieve the associated partner from any res_model+id
            It is a hack that will try to discover if the mentioned record is
            clearly associated with a partner record.
        """
        obj_model = self.pool.get(res_model)
        if obj_model._name == 'res.partner':
            return res_id
        elif 'partner_id' in obj_model._columns and obj_model._columns['partner_id']._obj == 'res.partner':
            bro = obj_model.browse(cri, uidi, res_id, context=contexts)
            return bro.partner_id.id
        return False

    if context is None:
        context = {}
    vals['parent_id'] = context.get('parent_id', False) or vals.get('parent_id', False)
    # take partner from uid
    if vals.get('res_id', False) and vals.get('res_model', False) and not vals.get('partner_id', False):
        vals['partner_id'] = get_partner_id(cr, uid, vals['res_model'], vals['res_id'], context)
    return super(document_file, self).create(cr, uid, vals, context)


def monkey_write(self, cr, uid, ids, vals, context=None):
    if context is None:
        context = {}
    return super(document_file, self).write(cr, uid, ids, vals, context)


document_file.create = monkey_create
document_file.write = monkey_write


# noinspection PyUnusedLocal
class IrAttachmentInherit(osv.osv):
    _inherit = 'ir.attachment'

    def _file_write(self, cr, uid, location, qqfile):
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
        full_path = self._full_path(cr, uid, location, fname)
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

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _file_read(self, cr, uid, location, fname, bin_size=False):
        full_path = self._full_path(cr, uid, location, fname)
        r = ''
        try:
            if bin_size:
                r = os.path.getsize(full_path)
            else:
                r = file(full_path, 'rb')
        except IOError:
            _logger.error("_read_file reading %s", full_path)
        return r

    # noinspection PySuperArguments
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
            file_name, file_size = self._file_write(cr, uid, location, qqfile)
            super(Model, self).write(cr, uid, [id], {'store_fname': file_name, 'file_size': file_size}, context=context)
        else:
            super(Model, self).write(cr, uid, [id], {'db_datas': qqfile.read(), 'file_size': file_size}, context=context)
        return True

    def _check_group_unlink_privilege(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        for attachment in self.browse(cr, uid, ids, context):
            context['ctx'] = {
                'res_model': attachment.res_model,
                'res_id': attachment.res_id,
            }
            if attachment.parent_id and not attachment.parent_id.check_directory_privilege('perm_write',
                                                                                           context=context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Unlink some of the attachments.'))

    def _check_group_write_privilege(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        for attachment in self.browse(cr, uid, ids, context):
            context['ctx'] = {
                'res_model': attachment.res_model,
                'res_id': attachment.res_id,
            }
            if attachment.parent_id and not attachment.parent_id.check_directory_privilege('perm_write',
                                                                                           context=context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Write some of the attachments.'))

    def _check_group_create_privilege(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        directory_obj = self.pool.get('document.directory')
        parent_id = vals['parent_id'] if 'parent_id' in vals else (
            context['parent_id'] if 'parent_id' in context else None)
        if parent_id:
            directory = directory_obj.browse(cr, uid, parent_id, context=context)
            context['ctx'] = {
                'res_model': vals.get('res_model', None),
                'res_id': vals.get('res_id', 0),
            }
            if not directory.check_directory_privilege('perm_write', context=context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to create attachments in this directory.'))

    def create(self, cr, uid, vals, context=None):
        self._check_group_create_privilege(cr, uid, vals, context)
        attachment_id = super(IrAttachmentInherit, self).create(cr, uid, vals, context)
        self.log_info(cr, uid, attachment_id, _('create this file'), context=context)
        return attachment_id

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        self._check_group_unlink_privilege(cr, uid, ids, context)
        self.log_info(cr, uid, ids, _('unlink this file'), context=context)
        junk_dir_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'up_document', 'doc_direct_100001')[1]
        for attachment in self.browse(cr, uid, ids, context):
            return super(IrAttachmentInherit, self).write(cr, uid, attachment.id, {'is_deleted': True,
                                                                                   'parent_id': junk_dir_id,
                                                                                   'name': fields.datetime.now() + attachment.name},
                                                          context=context)

    def write(self, cr, uid, ids, vals, context=None):
        self._check_group_write_privilege(cr, uid, ids, context)
        if not ('is_deleted' in vals and vals['is_deleted'] is True):
            self.log_info(cr, uid, ids, _('update this file'), context=context)
        return super(IrAttachmentInherit, self).write(cr, uid, ids, vals, context)

    def log_info(self, cr, uid, ids, message, context):
        for attachment_id in ids if isinstance(ids, list) else [ids]:
            self.pool.get('ir.attachment.log').create(cr, uid, {
                'message': message,
                'attachment_id': attachment_id,
            }, context=context)
        return True

    # noinspection PyUnusedLocal
    def _get_file_size(self, cr, uid, ids, field_name, arg, context):
        result = dict.fromkeys(ids, False)
        for attachment in self.browse(cr, uid, ids, context=context):
            result[attachment.id] = attachment.file_size / (1024.0 * 1024.0)
        return result

    # noinspection PyUnusedLocal
    def _is_download_able(self, cr, uid, ids, field_name, arg, context):
        result = dict.fromkeys(ids, False)
        for attachment in self.browse(cr, uid, ids, context=context):
            result[attachment.id] = attachment.check_downloadable()
        return result

    _columns = {
        'file_size_human': fields.function(_get_file_size, type='float', digits=[10, 3], method=True,
                                           string='File Size Human (MB)'),
        'is_downloadable': fields.function(_is_download_able, type='integer', string='Is Downloadable'),
        'application_ids': fields.one2many('ir.attachment.application', 'attachment_id', 'Applications'),
        'log_ids': fields.one2many('ir.attachment.log', 'attachment_id', 'Logs'),
        'is_deleted': fields.boolean('Is Deleted'),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="file", nodrop=True),
    }

    # _sql_constraints = [
    # ('filename_unique', 'unique (name,parent_id,res_model,res_id)', 'The file name in directory must be unique !'),
    # ]

    def on_change_name(self, cr, uid, ids, context=None):
        attachment = self.browse(cr, uid, ids, context)[0]
        self.write(cr, uid, attachment.id, {'name': attachment.datas_fname}, context)
        return True

    def check_downloadable(self, cr, uid, attachment_id, context=None):
        """
        return {
            0: can't be download
            1: can't be download but can apply
            TODO:  2: can't be download but already apply
            3: can be download
        }
        """
        # Superuser can download anyway
        if self.user_has_groups(cr, uid, 'base.group_document_user', context=context) or uid == 1:
            return 3
            # #init values
        if context is None:
            context = {}
        attachment = self.browse(cr, uid, attachment_id[0], context)
        context['ctx'] = {
            'res_id': attachment.res_id,
            'res_model': attachment.res_model,
        }
        is_pass_approval = attachment.is_pass_approval(context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        user_group = [u.id for u in user.groups_id]
        # if attachment have no directory
        if not attachment.parent_id:
            return 3
        else:
            result = [0]
            for group_id in attachment.parent_id.group_ids:
                if group_id.group_id.id in user_group:
                    # calc current group status
                    is_download_able = group_id.calc_privilege('is_downloadable', context=context)
                    # no download privilege means can't be download
                    if not is_download_able:
                        result += [0]
                        continue
                    is_need_approval = group_id.calc_privilege('is_need_approval', context=context)
                    # can be download status:
                    if (is_download_able and not is_need_approval) or \
                            (is_download_able and is_need_approval and is_pass_approval):
                        return 3
                        # can't be download but can apply
                    if is_download_able and is_need_approval and not is_pass_approval:
                        result += [1]
                        # can't download do nothing
            return max(result)

    def is_pass_approval(self, cr, uid, attachment_id, context):
        application_obj = self.pool.get('ir.attachment.application')
        application_ids = application_obj.search(cr, uid,
                                                 [('attachment_id', '=', attachment_id[0]), ('apply_user_id', '=', uid),
                                                  ('state', '=', 'approve'),
                                                  ('expire_date', '>=', fields.datetime.now())],
                                                 context=context)
        if application_ids:
            return True
        else:
            return False

    def download_apply(self, cr, uid, ids, context):
        application_obj = self.pool.get('ir.attachment.application')
        for attachment in self.browse(cr, uid, ids, context):
            application_ids = application_obj.search(cr, uid,
                                                     [('attachment_id', '=', attachment.id),
                                                      ('apply_user_id', '=', uid),
                                                      ('state', '=', None)],
                                                     context=context)
            if not application_ids:
                application_obj.create(cr, 1, {'attachment_id': attachment.id,
                                               'apply_date': fields.datetime.now(),
                                               'apply_user_id': uid}, context=context)
                from_rec = uid
                subject = u"有新的文件下载请求需要处理"
                content = u"有用户请求下载文件：%s, 请登陆系统处理" % attachment.name
                model = 'ir.attachment'
                res_id = attachment.id
                group_id = 'up_document.group_attachment_download_manager'
                self.pool.get('sms.sms').send_big_ant_to_group(cr, 1, from_rec, subject, content, model, res_id,
                                                               group_id, context=None)
        return True

    def get_directory_documents(self, cr, uid, directory_id, res_id, res_model, context):
        domain = [('parent_id', '=', directory_id), ('is_deleted', '=', False)]
        if res_id:
            domain += [('res_id', '=', res_id)]
        if res_model:
            domain += [('res_model', '=', res_model)]
        ids = self.search(cr, uid, domain, context=context)
        return self.read(cr, uid, ids, ['name'], context=context)

    def delete_temp_attachments(self, cr, uid, context=None):
        location = config.get('zip_temp_file', '')
        if location:
            shutil.rmtree(location)
            os.mkdir(location)


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
            if attach.file_size > 500 * 1024 * 1024:
                raise osv.except_osv(_('Warning!'), _('Some of the selected file is large than 500MB! Download alone!'))
            if attach.check_downloadable() != 3:
                raise osv.except_osv(_('Warning!'), _('You have no privilege to download some of the attachments'))
            # TODO: need some much useful limit
        if total_size > 2048 * 1024 * 1024:
            raise osv.except_osv(_('Warning!'), _('Generate File is large than 2GB!'))
        if 'attachment_ids' in field_list:
            res['attachment_ids'] = [a.id for a in attachments]
        return res

    _columns = {
        'name': fields.char('File Name', readonly=True),
        'attachment_ids': fields.many2many('ir.attachment', 'rel_attachment_download_wizard', 'wizard_id',
                                           'attachment_id', string='Attachments'),
        'data': fields.char('File', readonly=True),
        'state': fields.selection([('choose', 'choose'), # choose language
                                   ('get', 'get')])  # get the file
    }

    _defaults = {
        'state': 'choose',
    }

    def button_download_files(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_ids = context.get('active_ids', False)
        if record_ids:
            record_ids = record_ids if isinstance(record_ids, list) else [record_ids]
            attachments = self.pool.get('ir.attachment').browse(cr, uid, record_ids, context)
            location = config.get('zip_temp_file', '$HOME')
            temp_file_name = hashlib.md5(str(datetime.datetime.now()) + str(random.random())).hexdigest() + '.zip'
            zip_obj = zipfile.ZipFile(location + '/' + temp_file_name, 'w', zipfile.ZIP_STORED)
            i = 0
            for attachment in attachments:
                if attachment.datas is not False:
                    file_name = attachment.name
                    file_data = attachment.datas
                    i += 1
                    if isinstance(file_data, str):
                        zip_obj.writestr(str(i) + '.' + file_name.encode('GBK'), file_data)
                    else:
                        zip_obj.write(file_data.name, str(i) + '.' + file_name.encode('GBK'))

            filename = u"附件.zip"
            self.write(cr, uid, ids, {'state': 'get',
                                      'data': temp_file_name,
                                      'name': filename}, context=context)
            zip_obj.close()
            self.pool.get('ir.attachment').log_info(cr, uid, record_ids, _('have been zipped and download'),
                                                    context=context)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ir.attachment.download.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': ids[0],
                'views': [(False, 'form')],
                'target': 'new',
            }


class IrAttachmentApplication(osv.osv):
    _name = 'ir.attachment.application'
    _rec_name = 'attachment_id'
    _order = 'apply_date desc'

    # noinspection PyUnusedLocal
    def _is_expired(self, cr, uid, ids, name, arg, context=None):
        result = dict.fromkeys(ids, False)
        for attachment in self.browse(cr, uid, ids, context=context):
            if attachment.expire_date and datetime.datetime.strptime(attachment.expire_date,
                                                                     tools.DEFAULT_SERVER_DATETIME_FORMAT) < datetime.datetime.now():
                result[attachment.id] = True
        return result

    # noinspection PyUnusedLocal
    def _is_download_able(self, cr, uid, ids, field_name, arg, context):
        result = dict.fromkeys(ids, False)
        for application in self.browse(cr, uid, ids, context=context):
            result[application.id] = application.attachment_id.check_downloadable()
        return result

    _columns = {
        'attachment_id': fields.many2one('ir.attachment', 'Attachment', required=True, ondelete='cascade'),
        'apply_user_id': fields.many2one('res.users', 'Apply User'),
        'apply_date': fields.datetime('Apply Date'),
        'approve_user_id': fields.many2one('res.users', 'Approver User'),
        'approve_date': fields.datetime('Approve Date'),
        'expire_date': fields.datetime('Expire Date'),
        'is_expired': fields.function(_is_expired, type='boolean', string='Is expired'),
        'state': fields.selection(selection=[('approve', 'Approve'), ('disapprove', 'Disapprove')], string='State'),
        'attachment_name': fields.related('attachment_id', 'name', type='char', string='Attachment Name'),
        'attachment_datas': fields.related('attachment_id', 'datas', type='binary', string='Datas'),
        'is_downloadable': fields.function(_is_download_able, type='integer', string='Is Downloadable'),
    }

    def approve(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {
            'approve_user_id': uid,
            'approve_date': fields.datetime.now(),
            'expire_date': (datetime.datetime.now() + datetime.timedelta(days=7)).strftime(
                tools.DEFAULT_SERVER_DATETIME_FORMAT),
            'state': 'approve',
        }, context=context)
        return True

    def disapprove(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {
            'approve_user_id': uid,
            'approve_date': fields.datetime.now(),
            'expire_date': (datetime.datetime.now() + datetime.timedelta(days=7)).strftime(
                tools.DEFAULT_SERVER_DATETIME_FORMAT),
            'state': 'disapprove',
        }, context=context)
        return True


class IrAttachmentLog(osv.osv):
    _name = 'ir.attachment.log'
    _order = 'create_date desc'
    _columns = {
        'create_date': fields.datetime('Log Date'),
        'create_uid': fields.many2one('res.users', 'Log User'),
        'message': fields.char('Message', 1024),
        'filed_period': fields.integer('Filed Period'),
        'attachment_id': fields.many2one('ir.attachment', ondelete='cascade', string='Attachment'),
    }
    _defaults = {
        'filed_period': 1,
    }