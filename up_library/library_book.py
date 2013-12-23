# -*- encoding:utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.osv import fields
from up_tools import tools as ctools
from tools import DEFAULT_SERVER_DATE_FORMAT
import tools

__author__ = 'cysnake4713'


class LibraryRecord(osv.osv):
    _name = 'library.book.record'
    _description = 'Book Record'
    _order = 'borrow_date desc'
    _return_period = 30

    _columns = {
        'borrower': fields.many2one('res.users', string='Book Borrower', required=True),
        'borrow_date': fields.date(string='Borrow Date', required=True),
        'due_to_return_date': fields.date(string='Due To Return Date'),
        'is_returned': fields.boolean(string='Is Book Returned'),
        'return_date': fields.date(string='Return Date'),
        #TODO:relation between books is not limited
        'book_id': fields.many2one('library.book.book', string='Book', required=True, ondelete="cascade"),
    }

    _defaults = {
        'borrow_date': lambda *a: str(datetime.date.today()),
        'due_to_return_date': lambda *a: str(
            datetime.date.today() + datetime.timedelta(days=LibraryRecord._return_period)),
        'is_returned': False,
    }

    def on_change_borrow_date(self, cr, uid, ids, borrow_date, context=None):
        ret = {'value': {}}
        if borrow_date:
            due_to_return_date = datetime.datetime.strptime(borrow_date, DEFAULT_SERVER_DATE_FORMAT) + \
                                 datetime.timedelta(days=self._return_period)
            values = {
                'due_to_return_date': due_to_return_date.strftime(format=DEFAULT_SERVER_DATE_FORMAT),
            }
            ret['value'].update(values)
        else:
            values = {
                'due_to_return_date': '',
            }
            ret['value'].update(values)
        return ret

    def on_change_is_returned(self, cr, uid, ids, is_returned, context=None):
        ret = {'value': {}}
        if is_returned:
            values = {
                'return_date': datetime.datetime.today().strftime(format=DEFAULT_SERVER_DATE_FORMAT),
            }
            ret['value'].update(values)
        else:
            values = {
                'return_date': '',
            }
            ret['value'].update(values)
        return ret


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

    def _image_resize_image_medium(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            return_dict = dict()
            return_dict['image_medium'] = tools.image_resize_image_medium(obj.image, size=(275, 145))
            result[obj.id] = return_dict

        return result

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value), 'have_image': True},
                          context=context)

    def _has_image(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image != False
        return result

    _columns = {
        #TODO:State set miss
        'code': fields.char(size=64, string='Code', required=True),
        'name': fields.char(size=256, string='Book Name', required=True),
        'image': fields.binary("Image",
                               help="This field holds the image used as avatar for this book, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        store={
                                            'library.book.book': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        },
                                        help="Medium-sized image of this book. It is automatically " \
                                             "resized as a 128x128px image, with aspect ratio preserved. " \
                                             "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Small-sized image", type="binary", multi="_get_image",
                                       store={
                                           'library.book.book': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       },
                                       help="Small-sized image of this contact. It is automatically " \
                                            "resized as a 64x64px image, with aspect ratio preserved. " \
                                            "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),
        'category': fields.many2one('library.book.category', required=True, string='Category'),
        'type': fields.many2one('library.book.type', required=True, string='Type'),
        'author': fields.char(size=32, string='Book Author'),
        'publisher': fields.char(size=128, string='Publisher'),
        'price': fields.float(digits=(16, 2), string='Price'),
        'purchase_date': fields.date(string='Purchase Date'),
        'comment': fields.text(string='Comment'),
        'state': fields.selection(string='State',
                                  selection=[('in_store', 'In Store'), ('borrowed', 'Borrowed'), ('scrap', 'Scrap'),
                                             ('lost', 'Lost')]),
        'log_ids': fields.one2many('library.book.log', 'log_id', string='Logs'),
        'record_ids': fields.one2many('library.book.record', 'book_id', string='Records'),
    }

    _defaults = {
        'state': 'in_store',
        'purchase_date': lambda *a: str(datetime.date.today()),
    }

    def mark_as_scrap(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'scrap'}, context=context)
        return True

    def mark_as_lost(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'lost'}, context=context)
        return True


# noinspection PyUnusedLocal
class LibraryCategory(osv.osv):
    _name = 'library.book.category'
    _description = 'Book Category'
    _rec_name = 'full_name'

    def _get_full_name(self, cr, uid, ids, field_name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            full_name = ctools.get_parent_name(obj)
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
