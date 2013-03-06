from math import ceil
from flask import Blueprint, render_template, request, url_for
from flask.views import View
import operator
from werkzeug.contrib.cache import SimpleCache

__author__ = 'Zhou Guangwen'
blueprint_messages = Blueprint("messages", __name__, template_folder='templates', static_folder='static')
# TODO:Use memcached instead
cache = SimpleCache()


@blueprint_messages.context_processor
def url_for_page_wrapper():
    def url_for_page(page):
        args = request.view_args.copy()
        args['page'] = page
        return url_for(request.endpoint, **args)

    return dict(url_for_page=url_for_page)


class Pagination(object):
    def __init__(self, per_page, total_count, page):
        self.per_page = per_page
        self.total_count = total_count
        self.page = page

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                    (num > self.page - left_current - 1 and \
                             num < self.page + right_current) or \
                            num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


@blueprint_messages.route("/")
def index():
    return render_template("messages/index.html", message_categories=load_home_page_categories())


@blueprint_messages.route('/message/<message_id>')
def message_view(message_id):
    return render_template('messages/view.html')


@blueprint_messages.route('/category_messages/<int:cat_id>/<int:page>')
def category_messages(cat_id, page=1):
    per_page = 8
    msg_condition = [('category_id', '=', cat_id)]
    Category = request.erpsession.model("message.category")
    Message = request.erpsession.model("message.message")
    category = Category.read([cat_id], ['name', 'is_display_fbbm'])[0]
    messages = Message.search_read(msg_condition,
                                   ['name', 'write_date', 'write_uid', 'sequence', 'department_id', 'fbbm', 'content',
                                    'message_ids',
                                    'category_id', 'category_message_title_meta_display'], limit=per_page,
                                   offset=page * per_page)
    count = Message.search_count(msg_condition)
    pagination = Pagination(per_page, count, page)
    return render_template('messages/by_category.html', category=category, messages=messages, pagination=pagination)


def load_home_page_categories():
    ret = {}
    Category = request.erpsession.model("message.category")
    Message = request.erpsession.model("message.message")

    # All categories to display on internal home page
    categories_ids = Category.search([('display_position', '!=', False)])
    categories = Category.read(categories_ids, ['name', 'display_position', 'sequence', 'is_display_fbbm'])
    categories_map = dict((category['id'], category) for category in categories)

    # import pdb;pdb.set_trace()
    for cat in categories:
        ret.setdefault(cat['display_position'], []).append(cat)
        cat_id = cat['id']
        messages_id = Message.search([('category_id', '=', cat_id)], limit=6)
        messages = Message.read(messages_id,
                                ['name', 'write_date', 'write_uid', 'sequence', 'department_id', 'fbbm',
                                 'category_message_title_meta_display'])
        categories_map[cat_id]['children'] = messages
        categories_map[cat_id]['photo_news'] = do_load_first_photo_page(cat_id)
    for k, v in ret.items():
        v.sort(key=operator.itemgetter('sequence'))
        for cat in v:
            cat.setdefault('children', []).sort(key=operator.itemgetter('sequence'))
    ret.update(do_load_department_pagies())
    return ret


@blueprint_messages.context_processor
def load_menu():
    key = 'internal_menus'
    menus = cache.get(key)
    if menus is None:
        menus = do_load_menu()
        cache.set(key, menus)
    ret = {}
    for menu in menus.get('children'):
        name = menu['name']
        children = menu.get('children')
        if name == 'Top menu':
            ret['top_menu'] = menu
        elif name == 'Shortcut menu':
            ret['shortcut_menu'] = children
        elif name == 'Footer Menu':
            ret['footer_menu'] = children
    return ret


def do_get_roots():
    s = request.erpsession
    Menus = s.model("internal.home.menu")
    return Menus.search([('parent_id', '=', False)], 0, False, False, {})


def do_load_menu():
    """"Loads all internal home menus and their sub menus"""
    context = {}
    Menus = request.erpsession.model("internal.home.menu")
    menu_ids = Menus.search([], 0, False, False, context)
    menu_items = Menus.read(menu_ids,
                            ['name', 'sequence', 'parent_id', 'action', 'needaction_enabled', 'needaction_counter'],
                            context)
    menu_roots = Menus.read(do_get_roots(),
                            ['name', 'sequence', 'parent_id', 'action', 'needaction_enabled', 'needaction_counter'],
                            context)
    menu_root = {'id': False, 'name': 'root', 'parent_id': [-1, ''], 'children': menu_roots}

    menu_items.extend(menu_roots)
    menu_items_map = dict((menu_item['id'], menu_item) for menu_item in menu_items)
    for menu_item in menu_items:
        if menu_item['parent_id']:
            parent = menu_item['parent_id'][0]
        else:
            parent = False
        if parent in menu_items_map:
            menu_items_map[parent].setdefault('children', []).append(menu_item)
    for menu_item in menu_items:
        menu_item.setdefault('children', []).sort(key=operator.itemgetter('sequence'))
    return menu_root


def do_load_department_pagies():
    '''
    return {
        departments:[
            'name':XXX,
            'sequence':X,
            'categories':[
                {
                    'name':XXX,
                    'sequence':X,
                    'pagies':[
                        {
                            'name':XXX,
                            'id':XX,
                            'fbbm',
                            'department_id'
                        }
                    ]
                }
            ]
        ]
    }
    '''
    ret = {}
    Department = request.erpsession.model("hr.department")
    Message = request.erpsession.model("message.message")
    Category = request.erpsession.model("message.category")
    departments_ids = Department.search(
        [('is_in_use', '=', True), ('deleted', '=', False), ('display_in_front', '=', True)])
    departments = Department.read(departments_ids, ['name', 'sequence'])
    ret['departments'] = departments
    # import pdb;pdb.set_trace()
    for dep in departments:
        categories_ids = Category.search([('display_in_departments', '=', dep['id'])])
        categories = Category.read(categories_ids, ['name', 'sequence', 'display_fbbm'])
        dep['categories'] = categories
        for cat in categories:
            messages_id = Message.search([('category_id', '=', cat['id']), ('department_id', '=', dep['id'])],
                                         limit=6)
            messages = Message.read(messages_id,
                                    ['name', 'write_date', 'write_uid', 'sequence', 'department_id', 'fbbm',
                                     'category_message_title_meta_display'])
            cat['messages'] = messages
            cat['photo_news'] = do_load_first_photo_page(cat['id'], dep['id'])
    return ret


def do_load_first_photo_page(cat_id, department_id=False):
    Message = request.erpsession.model("message.message")
    options = [
        ('category_id', '=', cat_id),
        ('image_medium', '!=', False),
    ]
    if department_id:
        options.append(('department_id', '=', department_id))
    pagies_id = Message.search(options, limit=1)
    if pagies_id:
        return Message.read(pagies_id, ['name', 'write_date', 'write_uid', 'image_medium'])[0]
