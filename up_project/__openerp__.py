# -*- coding: utf-8 -*-
{
    'name': 'UPDIS Project Module',
    'version': '0.2',
    'category': 'Project Management',
    'complexity': "easy",
    'description': """
UPDIS Project Module.""",
    'author': 'Shrek Zhou',
    'website': 'http://openerp.com',
    'depends': ['base','mail','resource'],
    'init_xml': [],
    'update_xml': [
        'up_project_view.xml',
        'workflow/up_project_workflow_shenqingdan.xml',
    ],
    'demo_xml': [],
    'test':[],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
