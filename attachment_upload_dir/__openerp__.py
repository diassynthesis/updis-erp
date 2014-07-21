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
        'static/src/js/lib/bootstrap.min.js',
        'static/src/js/dir.js',
        'static/src/js/lib/jquery.fileupload.js',
    ],
    'css': [
        'static/src/css/progress.css',
        'static/src/css/directory.css',
    ],
    'auto_install': False,
    'installable': True,
}
