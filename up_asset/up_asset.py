__author__ = 'cysnake4713'

# -*- encoding:utf-8 -*-
from openerp.osv import fields
from openerp.osv import osv


class up_asset(osv.osv):
    _name = 'updis.asset.category'
    _order = 'id desc'

    _columns = {
        'name': fields.char(size=50, string="Asset Category Name"),
    }