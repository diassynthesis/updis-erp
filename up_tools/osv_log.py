__author__ = 'cysnake4713'
import datetime
from openerp.osv import fields
from openerp.osv import osv


class OsvLog(osv.osv_abstract):
    _name = 'log.log'
    _description = 'Log Item'
    _columns = {
    }
    _log_fields = []
    _log_osv = ''

    def write(self, cr, uid, ids, vals, context=None):
        if self._log_access is True:
            self._write_log(cr, uid, ids, vals, context)
        return super(OsvLog, self).write(cr, uid, ids, vals, context=context)

    def _write_log(self, cr, uid, ids, vals, context=None):
        if not self._log_osv:
            old_records = self.read(cr, uid, ids, context)
            log_obj = self.pool.get(self._log_osv)
            for old_record in old_records:
                info = ""
                for log_field_name in self._log_fields:
                    if log_field_name in vals[log_field_name] != old_record[log_field_name]:
                        info += "Change %s: %s --> %s" % (log_field_name, old_record[log_field_name],
                                                          vals[log_field_name] if vals[log_field_name] else "")
                if info:
                    log_obj.create(cr, uid, {'log_id': old_record.id, 'log_info': info})


class LogRecord(osv.osv_abstract):
    _name = 'log.record'
    _description = 'Log Record'
    _log_access = True
    _order = 'date desc'

    _columns = {
        'log_id': fields.many2one('log.log', string='Related Log'),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'date': fields.datetime('Datetime', required=True),
        'log_info': fields.text(string='Info'),
    }

    _defaults = {
        'date': lambda *args: datetime.datetime.now(),
        'user_id': lambda self, cr, uid, ctx: uid
    }