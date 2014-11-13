# -*- coding: utf-8 -*-
{
    'name': 'Reject Inherit Model',
    'version': '0.2',
    'category': 'UPDIS Implementation  Guide',
    'complexity': "easy",
    'description': """
UPDIS Implementation Guide.""",
    'author': 'matt.cai',
    'website': 'http://openerp.com',
    'depends': ['base', 'web'],
    # 'depends': ['base',],
    'js': [
        'static/src/js/reject.js',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
}