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
    'depends': ['base', 'project', 'oecn_base_fonts', 'report_webkit'],
    'init_xml': [

    ],
    'update_xml': [
        'report/header.xml',
        'security/updis_security.xml',
        'security/ir.model.access.csv',
        'data/updis_data.xml',
        'data/document.directory.csv',
        'data/project.project.filed.type.csv',
        'data/project.project.filed.tag.csv',
        'data/project.project.filed.filling.secondcategory.csv',
        'project_view.xml',
        'project_form_view.xml',

        'wizard/active/project_active_view.xml',
        'wizard/active/tasking/project_active_tasking_action.xml',
        'wizard/active/tasking/project_active_tasking_wizard_view.xml',
        'wizard/active/tasking/project_active_tasking_view.xml',
        'wizard/active/tasking/project_active_tasking_workflow.xml',
        'wizard/active/project_active_workflow.xml',

        'wizard/process/project_process_view.xml',
        'wizard/process/project_process_workflow.xml',

        'wizard/filed/project_filed_view.xml',
        'wizard/filed/project_filed_workflow.xml',
        'wizard/filed/filing/project_filing.xml',


        'project_workflow.xml',

        'report/active/renwuxiada.xml',
        'report/filed/report.xml',

        'hr_view.xml',
        'res_partner.xml',
        'config/project_config.xml',
    ],
    'css': [
        'static/src/css/up_project.css'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
