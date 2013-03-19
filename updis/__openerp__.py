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
        'data/updis_data.xml',   
        'security/updis_security.xml',
        'security/ir.model.access.csv',
        'internal_home_menu_view.xml',
        'document_page_view.xml',
        'hr_department_view.xml',
        'hr_view.xml',
        'wizard/suozhangshenpi.xml',  
        'wizard/suozhangshenpi_server_actions.xml',  
        'wizard/suozhangshenpi_workflow.xml',    
        'wizard/jingyingshi.xml',  
        'wizard/jingyingshi_server_actions.xml',  
        'wizard/jingyingshi_workflow.xml',    
        'wizard/zongshishi.xml',  
        'wizard/zongshishi_server_actions.xml',  
        'wizard/zongshishi_workflow.xml',   
        'wizard/suozhangqianzi.xml',  
        'wizard/suozhangqianzi_server_actions.xml',  
        'wizard/suozhangqianzi_workflow.xml',   
        'wizard/fuzerenqidong.xml',  
        'wizard/fuzerenqidong_server_actions.xml',  
        'wizard/fuzerenqidong_workflow.xml',   
        'project_view.xml',      
        'project_workflow.xml',    
        'report/renwuxiada.xml',
        'res_users.xml',
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
