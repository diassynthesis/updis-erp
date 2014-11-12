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
    'depends': ['base', 'hr', 'account_voucher', 'updis_auth_crypt', 'knowledge', 'signature'],
    # 'depends': ['base',],
    'data': [
        'security/res_user_security.xml',
        # 'security/hr_security.xml',
        'security/train_security.xml',
        'security/ir.model.access.csv',
        'internal_home_menu_view.xml',
        'hr_department_view.xml',
        'hr_view.xml',
        'res_users.xml',
        'training.xml',
        'hr_wish_view.xml',
        'mail_view.xml',
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
    'installable': True,
    'application': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
