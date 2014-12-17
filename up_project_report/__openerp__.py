# -*- coding: utf-8 -*-
{
    'name': 'UPDIS Project Report Module',
    'version': '0.2',
    'category': 'updis',
    'complexity': "easy",
    'description': """
UPDIS Project Report """,
    'author': 'Matt Cai',
    'website': 'http://odoosoft.com',
    'depends': ['base', 'up_project'],
    'data': [
        'views/project_report_view.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'application': True
}
