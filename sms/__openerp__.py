# -*- coding: utf-8 -*-

{
    'name': 'UPDIS SMS Gateway',
    'version': '1.0',
    'description': """UPDIS SMS Gateway""",
    'author': 'Shrek ()',
    'license': 'AGPL-3',
    'depends': ['base','hr'],
    'auto_install': False,
    'data':[
        'security/ir.model.access.csv',
        'sms_view.xml',
        # 'sms_workflow.xml',
    ]
}
