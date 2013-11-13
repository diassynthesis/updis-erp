# -*- coding: utf-8 -*-
{
    'name': 'UPDIS Asset Module',
    'version': '1.0',
    'category': 'up_asset',
    'complexity': "easy",
    'description': """
UPDIS Asset Management Module.""",
    'author': 'Matt Cai',
    'website': 'http://cysnake.com',
    'depends': ['base','hr'],
    'data': [
        'security/up_asset_security.xml',
        'security/ir.model.access.csv',

        'up_asset_category_view.xml',
        'up_asset_asset_view.xml',
        'up_asset_menu_view.xml',

        'data/updis.asset.category.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}