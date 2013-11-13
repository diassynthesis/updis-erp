# -*- encoding:utf-8 -*-
__author__ = 'cysnake4713'

import datetime
from openerp.osv import fields
from openerp.osv import osv


class up_asset_category(osv.osv):
    _name = 'updis.asset.category'
    _description = 'Asset Category'

    _columns = {
        'name': fields.char(size=50, string='Asset Category Name'),
    }


class up_asset_asset(osv.osv):
    _name = 'updis.asset.asset'
    _description = 'Asset Asset'
    _log_access = True

    _columns = {
        'category_id': fields.many2one('updis.asset.category', string="Category", required=True),
        'code': fields.char(size=30, string='Code', required=True),
        'department_id': fields.many2one('hr.department', string="Department"),
        'financial_code': fields.char(size=30, string='financial Code'),
        'name': fields.char(size=512, string='Name', required=True),
        'life_cycle': fields.integer(string='Life Cycle'),
        'model_and_type': fields.char(size=256, string='Model & Type'),
        'usage': fields.selection(selection=[('in_use', 'In Use'), ('damage', 'Damage'), ('scrap', 'Scrap')],
                                  string='Usage'),
        'scrap_result': fields.selection(
            selection=[('origin', 'In Origin Place'), ('warehouse', 'In Warehouse'), ('else', 'Else')],
            string='Scrap Result'),
        "scrap_note": fields.char(size=512, string='Scrap Note'),
        'note': fields.text(string='Maintenance Note'),
        'location': fields.char(size=512, string='Location'),
        'purchase_date': fields.date(string='Purchase Date'),
        'quantity': fields.integer(string='Quantity'),
        'unit_price': fields.float(digits=(16, 2), string='Unit Price'),
        'cost': fields.float(digits=(16, 2), string='Cost'),
        'retention': fields.selection(selection=[('permanent', 'Permanent')],
                                      string='Retention'),
        'create_date': fields.datetime('Created on', select=True),
        'create_uid': fields.many2one('res.users', 'Author', select=True),

        #for Computer
        'user': fields.char(size=256, string="User"),

        #for Software
        'supplier': fields.many2one('res.partner', string='Developer'),

        #for import
        'is_import': fields.boolean(string='Is Import'),


    }
    _defaults = {
        'is_import': False,
        'quantity': 1,
        'purchase_date': lambda *a: str(datetime.date.today()),
        'retention': 'permanent',
    }