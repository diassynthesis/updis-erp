{
    'name': 'Vote management',
    'category': 'Vote Management',
    'depends': ['hr', 'base'],
    'description': '''
This is a complete vote management system.
=============================================
	* User authentication
	''',
    'author': 'matt.cai',
    'data': [
        'vote_view.xml',
        # 'security/message_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
