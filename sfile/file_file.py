# -*- encoding: utf-8 -*-
__author__ = 'cysnake4713'

import datetime
from openerp.osv import osv
from openerp.osv import fields
from up_tools import tools as ctools


class FileDirectory(osv.osv):
    _name = 'sfile.file.directory'
    _description = 'File Directory'

    def _get_full_name(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            full_name = ctools.get_parent_name(obj)
            result[obj.id] = full_name
        return result

    _columns = {
        'name': fields.char(size=512, string='File Directory Name'),
        'full_name': fields.function(_get_full_name, type='char', readonly=True, string="Full Name"),
        'child_ids': fields.one2many('sfile.file.directory', 'parent_id', "Child File Directory Name"),
        'parent_id': fields.many2one('sfile.file.directory', 'Parent File Directory Name'),
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        ids = [ids] if isinstance(ids, int) else ids
        while len(ids):
            cr.execute('select distinct parent_id from sfile.file.directory where id IN %s', (tuple(ids), ))
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