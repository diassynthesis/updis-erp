# -*- coding: utf-8 -*-
{
    'name': 'UPDIS IMG Module',
    'version': '0.2',
    'category': 'UPDIS Implementation  Guide',
    'complexity': "easy",
    'description': """
UPDIS Implementation Guide.""",
    'author': 'Shrek Zhou',
    'website': 'http://openerp.com',
    'depends': ['base','hr','account_voucher','project','document_page'],
    # 'depends': ['base',],
    'data': [
        'internal_home_menu_view.xml',
        'document_page_view.xml',
        'hr_department_view.xml',
        'hr_view.xml',
        'project_view.xml',        
        'project_workflow.xml',
        'security/updis_security.xml',
        'data/updis_data.xml',        
    ],
    'js': [
        'static/src/js/updis.js',
        # 'static/src/js/banner.js',
        # 'static/src/js/tab.js',
        # 'static/src/js/DD_belatedPNG.js', //we abandoned IE support.
    ],
    'css': [
        'static/src/css/updis.css',
        # 'static/src/css/common.css',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'post_load': 'wsgi_postload',
    'installable': True,
    'application': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
