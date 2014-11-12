# -*- coding: utf-8 -*-

{
    'name': 'show user signature plugin',
    'version': '1.0',
    'description': """user signature plugin""",
    'author': 'Cysnake',
    'license': 'AGPL-3',
    'depends': ['base', 'web'],
    'auto_install': False,
    'data': [
        'views/res_user_view.xml',
    ],
    'js': [
        'static/src/js/signature.js',
    ],
    'qweb': [
        'static/src/xml/data.xml',
    ],
}
