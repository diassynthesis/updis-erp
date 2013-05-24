{
    'name': 'Message management',
    'category': 'Message Management',
    'depends': ['hr', 'base'],
    'description': '''
This is a complete message management system.
=============================================
	* User authentication
	''',
    'author': 'Shrek',
    'data': [
        'message_view.xml',
        'security/message_security.xml',
        'security/ir.model.access.csv',
        'message_view_publish.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
