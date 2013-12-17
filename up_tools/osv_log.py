__author__ = 'cysnake4713'
import datetime
from openerp.osv import fields
from openerp.osv import osv


class OsvLog(osv.osv):
    _name = 'tools.log.log'
    _description = 'Log Item'
    _columns = {
    }


    def write(self, cr, uid, ids, vals, context=None):
        if self._log_access is True:
            self._write_log(cr, uid, ids, vals, context)
        return super(OsvLog, self).write(cr, uid, ids, vals, context=context)

    def _write_log(self, cr, uid, ids, vals, context=None):
        pass


class LogRecord(osv.osv):
    _name = 'tools.log.record'
    _description = 'Log Record'
    _log_access = True
    _order = 'date desc'

    _columns = {
        'user_id': fields.many2one('res.users', 'User', required=True),
        'date': fields.datetime('Datetime', required=True),
        'log_info': fields.text(string='Info'),
    }

    _defaults = {
        'date': lambda *args: datetime.datetime.now(),
        'user_id': lambda self, cr, uid, ctx: uid
    }