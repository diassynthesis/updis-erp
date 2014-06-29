# -*- coding: utf-8 -*-
{
    'name': 'UPDIS Recuitment Module',
    'version': '0.1',
    'category': 'UPDIS Recuitment',
    'description': """
UPDIS Recuitment Module.""",
    'author': 'cysnake4713',
    'website': 'http://openerp.com',
    'depends': ['base', 'hr', 'up_document'],
    'data': [
        'data/document.directory.csv',
        'views/recuitment_menu_view.xml',
        'views/recuitment_view.xml',
    ],
    'js': [
    ],
    'css': [
    ],
    'qweb': [
    ],
    'demo': [],
    'installable': True,
}