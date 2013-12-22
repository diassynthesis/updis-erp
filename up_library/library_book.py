# -*- encoding:utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.osv import fields
from up_tools import tools

__author__ = 'cysnake4713'


class LibraryRecord(osv.osv):
    _name = 'library.book.record'
    _description = 'Book Record'
    _order = 'borrow_date desc'

    _columns = {
        'borrower': fields.many2one('res.users', string='Book Borrower', required=True),
        'borrow_date': fields.date(string='Borrow Date', required=True),
        #TODO:use function or Date???
        #TODO:onchange method
        'due_to_return_date': fields.date(string='Due To Return Date'),
        #TODO:is_returned onchange to return date set today
        'is_returned': fields.boolean(string='Is Book Returned'),
        'return_date': fields.date(string='Return Date'),
        #TODO:relation between books is not limited
        'book_id': fields.many2one('library.book.book', string='Book', required=True, ondelete="cascade"),
    }

    _defaults = {
        'borrow_date': lambda *a: str(datetime.date.today()),
        'is_returned': False,
    }


class LibraryBookWish(osv.osv):
    _name = 'library.book.wish'
    _description = 'Wish Book'
    _log_access = True

    _columns = {
        'name': fields.char(size=256, string='Book Name', required=True),
        'author': fields.char(size=32, string='Book Author'),
        'publisher': fields.char(size=128, string='Publisher'),
        'price': fields.float(digits=(16, 2), string='Price'),
        'comment': fields.text(string='Comment'),
        'state': fields.selection(selection=[('apply', 'Apply'), ('fail', 'Fail'), ('bought', 'Bought')],
                                  string='State', required=True),
    }

    _defaults = {
        'state': 'apply',
    }
    #TODO: need do the success wizard
    def reject_wish_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'fail'}, context=context)
        return True


class LibraryBook(osv.osv):
    _name = 'library.book.book'
    _inherit = 'log.log'
    _description = 'Book Info'
    _log_access = True
    _log_osv = 'library.book.log'
    _log_fields = {
        #TODO:Need Finish the auto log system
        # 'name': None,
        #            'author': [None, lambda o, n: u"作者变更:%s --> %s" % (o, n)],
        #            'category': [lambda o, n: o.id if o else 0 != n, lambda o, n: "分项变成: %s --> %s" % (o.full_name if o else "", n)],
    }

    _columns = {
        #TODO:State set miss
        'code': fields.char(size=64, string='Code', required=True),
        'name': fields.char(size=256, string='Book Name', required=True),
        'category': fields.many2one('library.book.category', string='Category'),
        'type': fields.many2one('library.book.type', string='Type'),
        'author': fields.char(size=32, string='Book Author'),
        'publisher': fields.char(size=128, string='Publisher'),
        'price': fields.float(digits=(16, 2), string='Price'),
        'quantity': fields.integer(string='Quantity'),
        'purchase_date': fields.date(string='Purchase Date'),
        'comment': fields.text(string='Comment'),
        'state': fields.selection(string='State',
                                  selection=[('in_store', 'In Store'), ('borrowed', 'Borrowed'), ('scrap', 'Scrap'),
                                             ('lost', 'Lost')]),
        'log_ids': fields.one2many('library.book.log', 'log_id', string='Logs'),
        'record_ids': fields.one2many('library.book.record', 'book_id', string='Records'),
    }

    _defaults = {
        'quantity': 1,
        'state': 'in_store',
        'purchase_date': lambda *a: str(datetime.date.today()),
    }

    #TODO:state button haven't done
    def mark_as_scrap(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'scrap'}, context=context)
        return True


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
        'log_id': fields.many2one('library.book.book', string='Related Book', ondelete="cascade"),
    }
