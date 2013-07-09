# -*- coding: utf-8 -*-
{
    'name': 'UPDIS Project Module',
    'version': '0.2',
    'category': 'up_project_management',
    'complexity': "easy",
    'description': """
UPDIS Project Module.""",
    'author': 'cysnake4713',
    'website': 'http://openerp.com',
    'depends': ['base', 'project', 'oecn_base_fonts'],
    'init_xml': [

    ],
    'update_xml': [

        'security/updis_security.xml',
        'security/ir.model.access.csv',
        'project_view.xml',
        'wizard/active/project_active_view.xml',

        'wizard/active/tasking/project_active_tasking_action.xml',
        'wizard/active/tasking/project_active_tasking_view.xml',
        'wizard/active/tasking/project_active_tasking_workflow.xml',


        'wizard/active/project_active_workflow.xml',

        'project_workflow.xml',

        'report/active/renwuxiada.xml',
        'data/updis_data.xml',
    ],
    'css': [
        'static/css/up_project.css'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
