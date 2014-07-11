# -*- encoding: utf-8 -*-
{
    'name': 'Document Upload Plugin Directory Support',
    'version': '1.0',
    'author': ['cysnake4713', ],
    'maintainer': 'cysnake4713',
    'website': 'http://www.cysnake.com',
    'category': 'Document',
    'description': """
Document Upload Plugin Directory Support
""",
    'depends': ['web', 'base'],
    'data': [
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'js': [
        'static/src/js/dir.js',
    ],
    'auto_install': False,
    'installable': True,
}
