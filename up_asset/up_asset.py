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
        'usage': fields.selection(
            selection=[('idle', 'Idle'), ('in_use', 'In Use'), ('damage', 'Damage'), ('scrap', 'Scrap')],
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
        'create_date': fields.datetime('Created on', select=True),
        'create_uid': fields.many2one('res.users', 'Author', select=True),

        #for Computer
        'user': fields.char(size=256, string="User"),

        #for Software
        'supplier': fields.many2one('res.partner', string='Developer'),

        #for import
        'is_import': fields.boolean(string='Is Import'),

        'log_ids': fields.one2many('updis.asset.log', 'asset_id', string='Logs'),

    }
    _defaults = {
        'is_import': False,
        'quantity': 1,
        'purchase_date': lambda *a: str(datetime.date.today()),
        'usage': 'in_use',
    }

    def write(self, cr, uid, ids, vals, context=None):
        if self._log_access is True:
            self._write_log(cr, uid, ids, vals, context)
        return super(up_asset_asset, self).write(cr, uid, ids, vals, context=context)

    def _write_log(self, cr, uid, ids, vals, context=None):
        old_assets = self.browse(cr, uid, ids, context)
        log_obj = self.pool.get('updis.asset.log')
        for old_asset in old_assets:
            info = ""
            if 'department_id' in vals and vals['department_id'] != (
                old_asset.department_id.id if old_asset.department_id else 0 ):
                department_name = self.pool.get('hr.department').browse(cr, uid, vals['department_id'], context).name if \
                    vals['department_id'] != 0 else ""
                info += u"改变资产部门:%s -> %s\n" % (old_asset.department_id.name if old_asset.department_id else "",
                                                department_name)
            if 'location' in vals and vals['location'] != old_asset.location:
                info += u"改变资产位置:%s -> %s\n" % (
                    old_asset.location if old_asset.location else "", vals['location'] if vals['location'] else "")
            if 'user' in vals and vals['user'] != old_asset.user:
                info += u"改变用户:%s -> %s\n" % (
                    old_asset.user if old_asset.user else "", vals['user'] if vals['user'] else "")

            if info:
                log_obj.create(cr, uid, {'asset_id': old_asset.id, 'log_info': info})


class up_asset_log(osv.osv):
    _name = 'updis.asset.log'
    _description = 'Asset Log'
    _log_access = True
    _order = 'date desc'

    _columns = {
        'asset_id': fields.many2one('updis.asset.asset', string='Related Asset'),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'date': fields.datetime('Datetime', required=True),
        'log_info': fields.text(string='Info'),
    }

    _defaults = {
        'date': lambda *args: datetime.datetime.now(),
        'user_id': lambda self, cr, uid, ctx: uid
    }