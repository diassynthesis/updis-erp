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
        'is_need_approval': fields.boolean('Is Need Approval',),
        'code': fields.text('Domain'),
    }

    _defaults = {
        'perm_read': True,
        'is_downloadable': True,
        'code': '',
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
        'index': fields.integer('Sequence'),
    }
    _order = 'index asc'

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
            new_group_ids += [(0, 0, {
                'group_id': g.group_id.id,
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

    def check_directory_privilege(self, cr, uid, directory_id, method, res_model=None, res_id=None, context=None):
        if not self.user_has_groups(cr, uid, 'base.group_document_user', context=context):
            if context is None:
                context = {}
            user = self.pool.get('res.users').browse(cr, uid, uid)
            user_group = [u.id for u in user.groups_id]
            flag = False
            for directory in self.browse(cr, uid, directory_id, context):
                for group in directory.group_ids:
                    if group.group_id.id in user_group:
                        if method in ['perm_write', 'is_downloadable'] and group[method] is True:
                            if group.code.strip():
                                cxt = {
                                    'self': self,
                                    'object': directory,
                                    'obj': directory,
                                    'pool': self.pool,
                                    'time': time,
                                    'cr': cr,
                                    'context': dict(context),  # copy context to prevent side-effects of eval
                                    'uid': uid,
                                    'user': user,
                                    'res_model': res_model,
                                    'res_id': res_id,
                                    'result': None,
                                }
                                eval(group.code.strip(), cxt, mode="exec", nocopy=True)  # nocopy allows to return 'action'
                                if cxt.get('result', None) is True:
                                    flag = True
                                    break
                            else:
                                flag = True
                                break
                        elif group[method] is True:
                            flag = True
                            break
            return flag
        else:
            return True

    def _check_group_unlink_privilege(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            if not directory.check_directory_privilege('perm_create_unlink', context=context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Unlink some of the directories.'))

    def _check_group_create_privilege(self, cr, uid, vals, context=None):
        parent_id = vals['parent_id']
        if parent_id:
            directory = self.browse(cr, uid, parent_id, context=context)
            if not directory.check_directory_privilege('perm_create_unlink', context=context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Create the directory.'))

    def _check_group_write_privilege(self, cr, uid, ids, context=None):
        for directory in self.browse(cr, uid, ids, context):
            if not directory.check_directory_privilege('perm_create_unlink', context=context):
                raise osv.except_osv(_('Warning!'), _('You have no privilege to Write some of the directories.'))

    def create(self, cr, uid, vals, context=None):
        self._check_group_create_privilege(cr, uid, vals, context)
        return super(DocumentDirectoryInherit, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        self._check_group_unlink_privilege(cr, uid, ids, context)
        return super(DocumentDirectoryInherit, self).unlink(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context=None):
        self._check_group_write_privilege(cr, uid, ids, context)
        return super(DocumentDirectoryInherit, self).write(cr, uid, ids, vals, context)
