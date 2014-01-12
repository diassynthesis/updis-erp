# -*- encoding: utf-8 -*-
__author__ = 'cysnake4713'

import datetime
from openerp.osv import osv
from openerp.osv import fields
from up_tools import tools as ctools


class FileFile(osv.osv):
    _inherit = 'log.log'
    _log_access = True
    _name = 'sfile.file.file'
    _description = 'File Rocord'

    _log_fields = {
        # 'name': None,
        # 'name': [None, 'info']
        # 'name': [lambda x:x, None]
        # 'name': [lambda x:x, 'info']
    }
    _log_osv = 'sfile.file.log'

    # noinspection PyUnusedLocal
    def _get_full_name(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            full_name = ctools.get_parent_name(obj)
            result[obj.id] = full_name
        return result

    _columns = {
        'name': fields.char(size=512, string='Name', required=True),
        'full_name': fields.function(_get_full_name, type='char', readonly=True, string="Full Name"),
        'child_ids': fields.one2many('sfile.file.file', 'parent_id', "Child Name"),
        'parent_id': fields.many2one('sfile.file.file', 'Parent Name'),
        'group_ids': fields.many2many('res.groups', 'sfile_file_res_group_rel', 'file_id', 'group_id',
                                      string='Groups'),
        'tag_ids': fields.many2many('sfile.file.tag', 'sfile_file_tag_rel', 'file_id', 'tag_id', string='Tags'),
        'priority': fields.integer('Sequence', required=True),

        'is_vc': fields.boolean(string='Is Under Version Control'),
        'is_directory': fields.boolean(string='Is Directory'),
        'is_deleted': fields.boolean(string='Is Deleted'),

        'log_ids': fields.one2many('sfile.file.log', 'log_id', string='Logs'),
    }

    _defaults = {
        'is_vc': False,
        'priority': 16,
        'is_directory': False,
    }

    # noinspection PyUnusedLocal
    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        ids = [ids] if isinstance(ids, int) else ids
        while len(ids):
            cr.execute('select distinct parent_id from sfile_file_file where id IN %s', (tuple(ids), ))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive Directory.', ['parent_id'])
    ]


class FileConfig(osv.osv):
    _name = 'sfile.file.config'
    _description = 'File Config'

    _columns = {
        'name': fields.char(size=256, string='Name'),
        'value': fields.char(size=512, string='Value'),
    }


class FileTag(osv.osv):
    _name = 'sfile.file.tag'
    _description = 'File Tag'

    _columns = {
        'name': fields.char(size=256, string='Tag Name'),
    }


class SFileLog(osv.osv):
    _name = 'sfile.file.log'
    _inherit = 'log.record'

    _columns = {
        'log_id': fields.many2one('sfile.file.file', string='Related File', ondelete="cascade"),
    }