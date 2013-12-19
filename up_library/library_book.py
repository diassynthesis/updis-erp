# -*- encoding:utf-8 -*-
from openerp.osv import osv
from openerp.osv import fields
from up_tools import tools

__author__ = 'cysnake4713'


class LibraryRecord(osv.osv):
    _name = 'library.book.record'
    _description = 'Book Record'

    _columns = {
        'borrower': fields.many2one('res.users', string='Book Borrower'),
        'borrow_date': fields.date(string='Borrow Date'),
        #TODO:use function or Date??? 'due_to_return_date': fields.date(string='Due To Return Date'),
        'return_date': fields.date(string='Return Date'),
        'rel_book':fields.many2one('library.book.book',string='Book'),
    }


class LibraryBook(osv.osv):
    _name = 'library.book.book'
    _inherit = 'log.log'
    _description = 'Book Info'
    _log_access = True
    _log_osv = 'library.book.log'
    _log_fields = ['name']

    _columns = {
        'code': fields.char(size=64, string='Code', states=""), #TODO:State set miss
        'name': fields.char(size=256, string='Book Name', required=True),
        'category': fields.many2one('library.book.category', string='Category'),
        'type': fields.many2one('library.book.type', string='Type'),
        'author': fields.char(size=32, string='Book Author'),
        'publisher': fields.char(size=128, string='Publisher'),
        'price': fields.float(digits=(16, 2), string='Price'),
        'quantity': fields.integer(string='Quantity'),
        'comment': fields.text(string='Comment'),
        'create_date': fields.datetime('Created on', select=True),
        'create_uid': fields.many2one('res.users', 'Author', select=True),
        'state': fields.selection(selection=[('wish', 'in_store', 'borrowed', 'scrap', 'lost')]),
        'log_ids': fields.one2many('library.book.log', 'log_id', string="Logs"),
    }

    _defaults = {
        'quantity': 1,
        'state': 'in_store',
    }

    def _write_log(self, cr, uid, ids, vals, context=None):
        pass


# noinspection PyUnusedLocal
class LibraryCategory(osv.osv):
    _name = 'library.book.category'
    _description = 'Book Category'
    _rec_name = 'full_name'

    def _get_full_name(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            full_name = tools.get_parent_name(obj)
            result[obj.id] = full_name
        return result

    _columns = {
        'name': fields.char(size=50, string='Book Category Name'),
        'full_name': fields.function(_get_full_name, type='char', readonly=True, string="Full Name"),
        'child_ids': fields.one2many('library.book.category', 'parent_id', "Child Category Name"),
        'parent_id': fields.many2one('library.book.category', 'Parent Category Name'),
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        ids = [ids] if isinstance(ids, int) else ids
        while len(ids):
            cr.execute('select distinct parent_id from library_book_category where id IN %s', (tuple(ids), ))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive Categories.', ['parent_id'])
    ]


class LibraryType(osv.osv):
    _name = 'library.book.type'
    _description = 'Book Type'

    _columns = {
        'name': fields.char(size=50, string='Book Type Name'),
    }


class LibraryLog(osv.osv):
    _name = 'library.book.log'
    _inherit = 'log.record'

    _columns = {
        'log_id': fields.many2one('library.book.book', string='Related Book'),
    }
