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
    'depends': ['base','hr','account_voucher','project'],
    'init_xml': [],
    'update_xml': [
        'hr_department_view.xml',
        'hr_view.xml',
        'project_view.xml',
        'security/updis_security.xml',
        'data/updis_data.xml',
    ],
    'demo_xml': [],
    'test':[],
    'installable': True,
    'auto_install': False,
    'application': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
