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
        'data/up_document_data.xml',

        'attachment_view.xml',
        'document_wizard_view.xml',
        'document_view.xml',
        'document_menu_view.xml',
    ],
    'js': [
        'static/src/js/document.js',
    ],
    'css': [
        'static/src/css/up_document.css',
    ],
    'qweb': [
        'static/src/xml/up_document.xml',
    ],
    'auto_install': False,
    'installable': True,
}
