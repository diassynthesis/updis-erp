{
    'name': 'Vote management',
    'category': 'vote_management',
    'depends': ['hr', 'base'],
    'description': '''
This is a complete vote management system.
=============================================
	* User authentication
	''',
    'author': 'matt.cai',
    'data': [
        'security/vote_security.xml',
        'vote_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
