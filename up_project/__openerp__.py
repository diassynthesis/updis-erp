# -*- coding: utf-8 -*-
{
    'name': 'UPDIS Project Module',
    'version': '0.2',
    'category': 'up_project_management',
    'complexity': "easy",
    'description': """
UPDIS Project Module.""",
    'author': 'Shrek Zhou',
    'website': 'http://openerp.com',
    'depends': ['base', 'project', 'oecn_base_fonts'],
    'init_xml': [],
    'update_xml': [
        'security/updis_security.xml',
        'security/ir.model.access.csv',
        'project_view.xml',

        'data/updis_data.xml',

        'wizard/suozhangshenpi.xml',
        # 'wizard/suozhangshenpi_server_actions.xml',
        # 'wizard/suozhangshenpi_workflow.xml',
        'wizard/jingyingshi.xml',
        # 'wizard/jingyingshi_server_actions.xml',
        # 'wizard/jingyingshi_workflow.xml',
        'wizard/zongshishi.xml',
        # 'wizard/zongshishi_server_actions.xml',
        # 'wizard/zongshishi_workflow.xml',
        'wizard/suozhangqianzi.xml',
        # 'wizard/suozhangqianzi_server_actions.xml',
        # 'wizard/suozhangqianzi_workflow.xml',
        # 'wizard/fuzerenqidong.xml',
        # 'wizard/fuzerenqidong_server_actions.xml',
        # 'wizard/fuzerenqidong_workflow.xml',
        'project_workflow_active.xml',
        'project_workflow.xml',
        # 'report/renwuxiada.xml',

    ],
    'css': [
        'static/css/up_project.css'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
