# -*- coding: utf-8 -*-
{
    'name': 'up_pro_manchange',
    'version': '1.0',
    'category': 'up_pro_manchange',
    'complexity': "easy",
    'description': """
""",
    'author': 'cysnake4713',
    'website': 'http://openerp.com',
    'depends': ['base', 'up_project', 'oecn_base_fonts', 'report_webkit'],
    'init_xml': [

    ],
    'update_xml': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/manager_change_view.xml',
    ],
    'css': [
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
