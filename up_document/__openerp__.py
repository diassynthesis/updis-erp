# -*- encoding: utf-8 -*-
{
    'name': 'Updis Document',
    'version': '1.0',
    'author': ['cysnake4713', ],
    'maintainer': 'cysnake4713',
    'website': 'http://www.cysnake.com',
    'category': 'Document',
    'description': """
Independent Super File Version control System
""",
    'depends': ['base', 'attachment_size_limit'],
    'data': [
        'security/document_security.xml',
        'security/ir.model.access.csv',

        'data/document.directory.csv',

        'views/attachment_view.xml',
        'views/document_wizard_view.xml',
        'views/document_view.xml',
        'views/document_menu_view.xml',
    ],
    'js': [
        'static/src/js/document.js',
        'static/src/js/lib/bootstrap.min.js',
        'static/src/js/dir.js',
        'static/src/js/lib/jquery.fileupload.js',
    ],
    'css': [
        'static/src/css/up_document.css',
        'static/src/css/directory.css',
        'static/src/css/progress.css',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'auto_install': False,
    'installable': True,
}
