# -*- coding: utf-8 -*-
{
    'name': 'UPDIS Project Contract Module',
    'version': '0.1',
    'category': 'up_contract_management',
    'complexity': "easy",
    'description': """
UPDIS Project Contract Module.""",
    'author': 'Matt Cai',
    'website': 'http://openerp.com',
    'depends': ['up_project'],
    'init_xml': [],
    'update_xml': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'contract_view.xml',
        'project_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
