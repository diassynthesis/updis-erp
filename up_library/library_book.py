# -*- encoding:utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.osv import fields
from up_tools import tools as ctools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.tools as tools

__author__ = 'cysnake4713'


class LibraryRecord(osv.osv):
    _name = 'library.book.record'
    _description = 'Book Record'
    _order = 'borrow_date desc'
    _rec_name = 'borrower'

    #0 is returned
    #1 is over time
    #2 need return
    #3 good
    def _need_return(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if not obj.is_returned:
                due_to_return_date = datetime.datetime.strptime(obj.due_to_return_date, DEFAULT_SERVER_DATE_FORMAT)
                borrow_date = datetime.datetime.strptime(obj.borrow_date, DEFAULT_SERVER_DATE_FORMAT)
                between_date = (due_to_return_date - borrow_date).days
                if between_date < 0:
                    result[obj.id] = 1
                elif 0 <= between_date < 10:
                    result[obj.id] = 2
                else:
                    result[obj.id] = 3
            else:
                result[obj.id] = 0
        return result

    _columns = {
        'borrower': fields.many2one('res.users', string='Book Borrower', required=True),
        'borrow_date': fields.date(string='Borrow Date', required=True),
        'due_to_return_date': fields.date(string='Due To Return Date'),
        'is_returned': fields.boolean(string='Is Book Returned'),
        'return_date': fields.date(string='Return Date'),
        'book_id': fields.many2one('library.book.book', string='Book', required=True, ondelete="cascade"),
        'need_return': fields.function(_need_return, type='integer', string='Need Return'),
    }

    _defaults = {
        'borrow_date': lambda *a: str(datetime.date.today()),
        'due_to_return_date': lambda self, cr, uid, context: str(
            datetime.date.today() + datetime.timedelta(
                days=self.pool.get('library.book.config').get_return_period(cr, uid, 1, context))),
        'is_returned': False,
    }

    def on_change_borrow_date(self, cr, uid, ids, borrow_date, context=None):
        ret = {'value': {}}
        if borrow_date:
            borrow_date_format = datetime.datetime.strptime(borrow_date, DEFAULT_SERVER_DATE_FORMAT)
            period = self.pool.get('library.book.config').get_return_period(cr, uid, 1, context)
            due_to_return_date = borrow_date_format + datetime.timedelta(days=period)
            values = {
                'due_to_return_date': due_to_return_date.strftime(format=DEFAULT_SERVER_DATE_FORMAT),
            }
            ret['value'].update(values)
        else:
            values = {
                'due_to_return_date': None,
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
                'return_date': None,
            }
            ret['value'].update(values)
        return ret

    def _sync_related_book(self, cr, uid, ids, context=None):
        ids = ids if isinstance(ids, list) else [ids]
        book_ids = []
        for record in self.read(cr, uid, ids, ['book_id'], context=context):
            book_ids += [record['book_id'][0]]
        book_ids = list(set(book_ids))
        self.pool.get('library.book.book').sync_book_status(cr, uid, book_ids, context=context)
        return True

    def create(self, cr, uid, vals, context=None):
        mid = super(LibraryRecord, self).create(cr, uid, vals, context)
        self._sync_related_book(cr, uid, mid, context)
        return mid

    def write(self, cr, uid, ids, vals, context=None):
        super(LibraryRecord, self).write(cr, uid, ids, vals, context)
        self._sync_related_book(cr, uid, ids, context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        book_ids = []
        for record in self.read(cr, uid, ids, ['book_id'], context=context):
            book_ids += [record['book_id'][0]]
        book_ids = list(set(book_ids))
        super(LibraryRecord, self).unlink(cr, uid, ids, context)
        self.pool.get('library.book.book').sync_book_status(cr, uid, book_ids, context=context)
        return True


class LibraryRecordWizard(osv.osv_memory):
    _name = 'library.book.record.wizard'
    _inherit = 'library.book.record'
    _description = 'Book Record Wizard'

    _columns = {
        'record_id': fields.many2one('library.book.record', string='Book Record'),
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(LibraryRecordWizard, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        book_obj = self.pool.get('library.book.book')
        book = book_obj.browse(cr, uid, record_id, context=context)

        if context.get('to_borrowed', False):
            if 'book_id' in fields:
                res['book_id'] = book.id
            return res
        if context.get('to_return', False):
            record_ids = book.get_current_borrow_record()
            record_id = self.pool.get('library.book.record').browse(cr, uid, record_ids, context=context)[0]
            if 'book_id' in fields:
                res['book_id'] = book.id
            if 'record_id' in fields:
                res['record_id'] = record_id.id
            if 'borrower' in fields:
                res['borrower'] = record_id.borrower.id if record_id.borrower else None
            if 'borrow_date' in fields:
                res['borrow_date'] = record_id.borrow_date if record_id.borrow_date else ''
            if 'due_to_return_date' in fields:
                if record_id.due_to_return_date:
                    res['due_to_return_date'] = record_id.due_to_return_date
                else:
                    del (res['due_to_return_date'])
            if 'return_date' in fields:
                res['return_date'] = record_id.return_date if record_id.return_date else ''
            if 'is_returned' in fields:
                res['is_returned'] = record_id.is_returned
        return res

    def save(self, cr, uid, ids, context):
        self_record = self.browse(cr, uid, ids[0], context)
        record_obj = self.pool.get('library.book.record')
        values = {
            'borrower': self_record.borrower.id if self_record.borrower else None,
            'borrow_date': self_record.borrow_date if self_record.borrow_date else None,
            'due_to_return_date': self_record.due_to_return_date if self_record.due_to_return_date else None,
            'return_date': self_record.return_date if self_record.return_date else None,
            'is_returned': self_record.is_returned,
        }
        if self_record['record_id']:
            record_obj.write(cr, uid, self_record.record_id.id, values, context=context)
        else:
            values.update({'book_id': self_record.book_id.id})
            record_obj.create(cr, uid, values, context=context)

        return True


class LibraryBookWish(osv.osv):
    _name = 'library.book.wish'
    _description = 'Wish Book'
    _log_access = True

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        return self.write(cr, uid, [ids], {'image': tools.image_resize_image_big(value)},
                          context=context)

    def _has_image(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image != False
        return result

    _columns = {
        'name': fields.char(size=256, string='Book Name', required=True),
        'author': fields.char(size=32, string='Book Author'),
        'publisher': fields.char(size=128, string='Publisher'),
        'price': fields.float(digits=(16, 2), string='Price'),
        'comment': fields.text(string='Comment'),
        'state': fields.selection(selection=[('apply', 'Apply'), ('fail', 'Fail'), ('bought', 'Bought')],
                                  string='State', required=True),
        'image': fields.binary("Image",
                               help="This field holds the image used as avatar for this book, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        store={
                                            'library.book.wish': (
                                                lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        }),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Small-sized image", type="binary", multi="_get_image",
                                       store={
                                           'library.book.wish': (
                                               lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       }),
        'has_image': fields.function(_has_image, type="boolean", string='Have Image'),
        'link_book_id': fields.many2one('library.book.book', string='Link Book'),
    }

    _defaults = {
        'state': 'apply',
    }

    def reject_wish_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'fail'}, context=context)
        return True


class LibraryBook(osv.osv):
    _name = 'library.book.book'
    _description = 'Book Info'
    _log_access = True

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

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        return self.write(cr, uid, [ids], {'image': tools.image_resize_image_big(value)},
                          context=context)

    def _has_image(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image != False
        return result

    def _is_borrowable(self, cr, uid, ids, name, args, context=None):
        result = {}
        for id in ids:
            record_ids = self.get_current_borrow_record(cr, uid, id, context)
            if len(record_ids):
                result[id] = False
            else:
                result[id] = True
        return result

    def get_current_borrow_record(self, cr, uid, ids, context=None):
        ids = [ids] if isinstance(ids, int) else ids
        return self.pool.get('library.book.record').search(cr, uid, [('book_id', 'in', ids),
                                                                     ('is_returned', '=', False)])

    _columns = {
        'code': fields.char(size=64, string='Code', required=True),
        'name': fields.char(size=256, string='Book Name', required=True),
        'image': fields.binary("Image",
                               help="This field holds the image used as avatar for this book, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        store={
                                            'library.book.book': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        }),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Small-sized image", type="binary", multi="_get_image",
                                       store={
                                           'library.book.book': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       }),
        'has_image': fields.function(_has_image, type="boolean", string='Have Image'),
        'category': fields.many2one('library.book.category', required=True, string='Category'),
        'type': fields.many2one('library.book.type', required=True, string='Type'),
        'author': fields.char(size=256, string='Book Author'),
        'publisher': fields.char(size=256, string='Publisher'),
        'price': fields.float(digits=(16, 2), string='Price'),
        'purchase_date': fields.date(string='Purchase Date'),
        'comment': fields.text(string='Comment'),
        'state': fields.selection(string='State',
                                  selection=[('in_store', 'In Store'), ('borrowed', 'Borrowed'), ('scrap', 'Scrap'),
                                             ('lost', 'Lost')]),
        'record_ids': fields.one2many('library.book.record', 'book_id', string='Records'),
        'is_borrowable': fields.function(_is_borrowable, type='boolean', string='Is Borrowable'),
    }

    _defaults = {
        'state': 'in_store',
        'purchase_date': lambda *a: str(datetime.date.today()),
    }

    _sql_constraints = [
        ('book_code_unique', 'unique (code)', 'The code of the book must be unique!')
    ]

    def mark_as_scrap(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'scrap'}, context=context)
        return True

    def mark_as_lost(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'lost'}, context=context)
        return True

    def sync_book_status(self, cr, uid, ids, recover=False, context=None):
        ids = [ids] if isinstance(ids, int) else ids
        for book in self.browse(cr, uid, ids, context=context):
            record_ids = self.get_current_borrow_record(cr, uid, book.id, context=context)
            if recover or book.state not in ['scrap', 'lost']:
                if len(record_ids):
                    self.write(cr, uid, book.id, {'state': 'borrowed'}, context=context)
                else:
                    self.write(cr, uid, book.id, {'state': 'in_store'}, context=context)
            else:
                return False
        return True

    def recover(self, cr, uid, ids, context=None):
        return self.sync_book_status(cr, uid, ids, recover=True, context=context)


class LibraryBookWizard(osv.osv_memory):
    _name = 'library.book.book.wizard'
    _inherit = 'library.book.book'
    _description = 'Book Info Wizard'

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        return self.write(cr, uid, [ids], {'image': tools.image_resize_image_big(value)},
                          context=context)

    def _has_image(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image != False
        return result

    _columns = {
        'image': fields.binary("Image",
                               help="This field holds the image used as avatar for this book, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        store={
                                            'library.book.book.wizard': (
                                                lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        }),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Small-sized image", type="binary", multi="_get_image",
                                       store={
                                           'library.book.book.wizard': (
                                               lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       }),
        'has_image': fields.function(_has_image, type="boolean", string='Have Image'),
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(LibraryBookWizard, self).default_get(cr, uid, fields, context=context)
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        if not record_id:
            return res
        elif context['to_bought']:
            wish_book = self.pool.get('library.book.wish').browse(cr, uid, record_id, context=context)
            if 'name' in fields:
                res['name'] = wish_book.name
            if 'author' in fields:
                res['author'] = wish_book.author
            if 'publisher' in fields:
                res['publisher'] = wish_book.publisher
            if 'price' in fields:
                res['price'] = wish_book.price
            if 'comment' in fields:
                res['comment'] = wish_book.comment
            res['image'] = wish_book.image
            return res
        else:
            return res

    def save(self, cr, uid, ids, context):
        self_record = self.browse(cr, uid, ids[0], context)
        book_obj = self.pool.get('library.book.book')
        image = self_record.image
        values = {
            'code': self_record.code,
            'name': self_record.name,
            'category': self_record.category.id if self_record.category else None,
            'type': self_record.type.id if self_record.type else None,
            'author': self_record.author,
            'publisher': self_record.publisher,
            'price': self_record.price,
            'purchase_date': self_record.purchase_date,
            'comment': self_record.comment,
            'image': self_record.image,
        }
        book_id = book_obj.create(cr, uid, values, context=context)
        self.pool.get('library.book.wish').write(cr, uid, context['active_id'],
                                                 {'state': 'bought', 'link_book_id': book_id}, context=context)

        return True


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


class LibraryConfig(osv.osv):
    _name = 'library.book.config'
    _columns = {
        'name': fields.char(size=256, string='Name'),
        'value': fields.char(size=512, string='Value'),
    }

    # noinspection PyUnusedLocal
    def get_return_period(self, cr, uid, ids, context):
        dataobj = self.pool.get('ir.model.data')
        dummy, value = dataobj.get_object_reference(cr, 1, 'up_library', 'config_period_date_value')
        period = self.browse(cr, uid, value, context=context).value
        return int(period)