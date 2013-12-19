# -*- coding: utf-8 -*-
{
    'name': 'Book Library Module',
    'version': '1.0',
    'category': 'up_library',
    'complexity': "easy",
    'description': """
Book Library Management Module.""",
    'author': 'Matt Cai',
    'website': 'http://cysnake.com',
    'depends': ['base', 'hr', 'up_tools'],
    'data': [
        'security/up_library_security.xml',
        'security/ir.model.access.csv',

        'library_book_view.xml',
        'library_config_view.xml',
        'library_menu_view.xml',

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}