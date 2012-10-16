# -*- coding: utf-8 -*-

{
    'name': 'Web CMS View',
    'version': '1.0',
    'category': '',
    'description': """CMS Views""",
    'author': 'Shrek ()',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['web'],
    'init_xml': [],
    'update_xml': [],
    'demo_xml': [],
    'active': False,
    'installable': True,
    'web':True,
    'css': [
        'static/css/web_cms.css',
    ],
    'js': [
        'static/js/web_cms.js',
    ],
    'qweb': [
        'static/xml/*.xml',
    ],
}

