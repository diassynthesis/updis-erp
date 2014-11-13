# -*- encoding: utf-8 -*-
__author__ = 'cysnake4713'

import time
from openerp.tools.safe_eval import safe_eval as eval
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _


class DocumentDirectoryAccess(osv.osv):
    _name = 'document.directory.access'

    _columns = {
        'group_id': fields.many2one('res.groups', 'Group', ondelete='cascade', select=True, required=True),
        'perm_read': fields.boolean('Directory / Sub File Read Access', readonly=True),
        'perm_write': fields.boolean('Sub File Write / Modify Access'),
        'perm_create_unlink': fields.boolean('Sub Directory Create / Write / Unlink Access'),
        'directory_id': fields.many2one('document.directory', string='Related Directory ID', ondelete='cascade'),
        'is_downloadable': fields.boolean('Is Downloadable'),
        'is_need_approval': fields.boolean('Is Need Approval'),
        'code': fields.text('Domain'),
    }

    _defaults = {
        'perm_read': True,
        'is_downloadable': True,
        'code': '',
    }

    def calc_privilege(self, cr, uid, ids, method, context):
        if isinstance(ids, (int, long)):
            ids = [ids]
        access = self.browse(cr, 1, ids[0], context)
        # If method need eval
        if method in ['perm_write', 'is_downloadable']:
            if access[method] is False:
                return False
            if access.code and access.code.strip():
                ctx = {
                    'self': self,
                    'object': access,
                    'obj': access,
                    'pool': self.pool,
                    'time': time,
                    'cr': cr,
                    'context': dict(context),  # copy context to prevent side-effects of eval
                    'uid': uid,
                    'user': self.pool.get('res.users').browse(cr, uid, uid),
                    'result': None,
                }
                ctx.update(context.get('ctx', {}))
                eval(access.code.strip(), ctx, mode="exec", nocopy=True)  # nocopy allows to return 'action'
                return True if ctx.get('result', None) else False
            else:
                return True
        else:
            return access[method]


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
        'index': fields.integer('Sequence'),
        'is_encrypt': fields.boolean('Is Encrypt'),
    }
    _order = 'index asc'

    _defaults = {
        'user_id': None,
    }

    def delete_related_action(self, cr, uid, ids, context):
        directory_records = self.browse(cr, uid, ids, context)
        for directory_record in directory_records:
            action_id = directory_record.related_action_id.id
            self.write(cr, uid, ids, {'related_action_id': False})
            self.pool.get("ir.actions.act_window").unlink(cr, 1, action_id, context)
        return True

    def _get_child_ids(self, cr, uid, documents, context=None):
        result_ids = [d.id for d in documents]
        for document in documents:
            if document.child_ids:
                result_ids += self._get_child_ids(cr, uid, document.child_ids, context)
        return set(result_ids)

    def convert_child_privilege(self, cr, uid, ids, context):
        for document in self.browse(cr, uid, ids, context):
            vals = self._copy_accesses(cr, 1, document.id, context)
            child_ids = self._get_child_ids(cr, 1, document.child_ids, context)
            for child_id in child_ids:
                self.write(cr, 1, [child_id], vals, context=context)
        return True

    def _copy_accesses(self, cr, uid, document_id, context):
        parent_directory = self.browse(cr, uid, document_id, context)
        new_group_ids = [(5,)]
        new_group_ids += [(0, 0, {
            'group_id': g.group_id.id,
            'perm_read': g.perm_read,
            'perm_write': g.perm_write,
            'perm_create_unlink': g.perm_create_unlink,
            'is_downloadable': g.is_downloadable,
            'is_need_approval': g.is_need_approval,
            'code': g.code,
        }) for g in parent_directory.group_ids]
        sms_vals = {
            'group_ids': new_group_ids,
        }
        return sms_vals

    def onchange_parent_id(self, cr, uid, ids, parent_id, context=None):
        ret = {'value': {}}
        if parent_id:
            vals = self._copy_accesses(cr, uid, parent_id, context)
            # noinspection PyTypeChecker
            ret['value'].update(vals)
        return ret

    def check_directory_privilege(self, cr, uid, ids, method, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        # if user is document admin
        if self.user_has_groups(cr, uid, 'base.group_document_user', context=context) or uid == 1:
            if method == 'is_need_approval':
                return False
            else:
                return True
        # init values
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, 1, uid)
        user_group = [u.id for u in user.groups_id]
        # each directory
        for directory in self.browse(cr, uid, ids, context):
            for group in directory.group_ids:
                if group.group_id.id in user_group:
                    if group.calc_privilege(method, context=context):
                        return True
        return False

    def _check_group_unlink_privilege(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            if not directory.check_directory_privilege('perm_create_unlink', context=context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Unlink some of the directories.'))

    def _check_group_create_privilege(self, cr, uid, vals, context=None):
        if 'parent_id' in vals and vals['parent_id']:
            parent_id = vals['parent_id']
            directory = self.browse(cr, uid, parent_id, context=context)
            if not directory.check_directory_privilege('perm_create_unlink', context=context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Create the directory.'))

    def _check_group_write_privilege(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            if not directory.check_directory_privilege('perm_create_unlink', context=context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Write some of the directories.'))

    def button_update_sub_encript(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            sub_ids = self.search(cr, uid, [('id', 'child_of', directory.id)], context=context)
            sub_ids.remove(directory.id)
            self.write(cr, uid, sub_ids, {'is_encrypt': directory.is_encrypt}, context=context)
        return True

    def create(self, cr, uid, vals, context=None):
        self._check_group_create_privilege(cr, uid, vals, context)
        return super(DocumentDirectoryInherit, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        self._check_group_unlink_privilege(cr, uid, ids, context)
        return super(DocumentDirectoryInherit, self).unlink(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context=None):
        self._check_group_write_privilege(cr, uid, ids, context)
        return super(osv.osv, self).write(cr, uid, ids, vals, context)

    def get_directory_info(self, cr, uid, directory_id, res_id=None, res_model=None, context=None):
        if not context: context = {}
        context['ctx'] = {
            'res_id': res_id,
            'res_model': res_model,
        }

        directory = self.browse(cr, uid, directory_id, context)
        domain = [('parent_id', 'child_of', directory_id)]
        if res_id and res_model:
            domain += [('res_id', '=', res_id), ('res_model', '=', res_model)]
        attachments = self.pool['ir.attachment'].search(cr, uid, domain, context=context)

        result = {
            'id': directory.id,
            'name': directory.name,
            'is_writable': directory.check_directory_privilege('perm_write', context=context),
            'is_downloadable': directory.check_directory_privilege('is_downloadable', context=context),
            'is_need_approval': directory.check_directory_privilege('is_need_approval', context=context),
            'file_total': len(attachments),
        }
        return result

    def get_directory_child_info(self, cr, uid, id, res_id, res_model, context=None):
        if not context: context = {}
        context['ctx'] = {
            'res_id': res_id,
            'res_model': res_model,
        }

        ids = self.search(cr, uid, [('parent_id', '=', id)], context=context)
        directorys = self.browse(cr, uid, ids, context)
        result = []
        domain = []
        if res_id and res_model:
            domain = [('res_id', '=', res_id), ('res_model', '=', res_model)]
        for directory in directorys:
            attachments = self.pool['ir.attachment'].search(cr, uid, [('parent_id', 'child_of', directory.id)] + domain, context=context)
            result += [
                {
                    'id': directory.id,
                    'name': directory.name,
                    'is_writable': directory.check_directory_privilege('perm_write', context=context),
                    'is_downloadable': directory.check_directory_privilege('is_downloadable', context=context),
                    'is_need_approval': directory.check_directory_privilege('is_need_approval', context=context),
                    'file_total': len(attachments),
                }
            ]
        return result