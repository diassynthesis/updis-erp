__author__ = 'cysnake4713'
import datetime
from openerp.osv import fields
from openerp.osv import osv


class OsvLog(osv.osv_abstract):
    _name = 'log.log'
    _description = 'Log Item'
    _columns = {}
    _log_fields = {
        # 'name': None,
        # 'name': [None, 'info']
        # 'name': [lambda x:x, None]
        # 'name': [lambda x:x, 'info']
    }
    _log_osv = ''

    def write(self, cr, uid, ids, vals, context=None):
        if self._log_access is True and self._log_osv:
            self._write_log(cr, uid, ids, vals, context)
        return super(OsvLog, self).write(cr, uid, ids, vals, context=context)

    def _get_need_log_fields(self, vals):
        result = []
        for key in vals.keys():
            if key in self._log_fields:
                result += [key]
        return result

    def _get_translated_field_name(self, cr, uid, src_field_name, lang, context=None):
        #TODO:
        return src_field_name

    def _default_is_not_equal(self, old, new, need_log_field):
        return new[need_log_field] != old.__getitem__(need_log_field)

    def _default_log_info(self, cr, uid, old, new, need_log_field, lang='zh_CN', context=None):
        return self._get_translated_field_name(cr, uid, need_log_field, lang=lang, context=context) + ": %s --> %s" % (
            old.__getitem__(need_log_field), new[need_log_field])

    def _write_log(self, cr, uid, ids, new_record, context=None):
        need_log_fields = self._get_need_log_fields(new_record)
        if need_log_fields:
            old_records = self.browse(cr, uid, ids, context)
            #get all need log records
            for old_record in old_records:
                log_info = ""
                #get need log field name
                for need_log_field in need_log_fields:
                    #if field don't have custom condition
                    if self._log_fields[need_log_field] is None:
                        if self._default_is_not_equal(old_record, new_record, need_log_field):
                            log_info += self._default_log_info(cr, uid, old_record, new_record, need_log_field,
                                                               context=context)
                    elif len(self._log_fields[need_log_field]) == 2:
                        (condition, custom_info) = self._log_fields[need_log_field]
                        #if field have no condition but have log_info
                        if condition is None and custom_info is not None:
                            if self._default_is_not_equal(old_record, new_record, need_log_field):
                                log_info += custom_info(old_record.__getitem__(need_log_field),
                                                        new_record[need_log_field])
                        #if field have condition but have no log_info
                        elif condition is not None and custom_info is None:
                            if condition(old_record.__getitem__(need_log_field), new_record[need_log_field]):
                                log_info += self._default_log_info(cr, uid, old_record, new_record, need_log_field,
                                                                   context=context)
                        #if field have condition and log_info
                        elif condition is not None and custom_info is not None:
                            if condition(old_record.__getitem__(need_log_field), new_record[need_log_field]):
                                log_info += custom_info(old_record.__getitem__(need_log_field),
                                                            new_record[need_log_field])#TODO: Still Not Right
                        else:
                            raise FieldFormatException(need_log_field, self._log_fields[need_log_field])
                    else:
                        raise FieldFormatException(need_log_field, self._log_fields[need_log_field])

                log_obj = self.pool.get(self._log_osv)
                if log_info:
                    log_obj.create(cr, uid, {'log_id': old_record.id, 'log_info': log_info})


class LogRecord(osv.osv_abstract):
    _name = 'log.record'
    _description = 'Log Record'
    _log_access = True
    _order = 'date desc'

    _columns = {
        'log_id': fields.many2one('log.log', string='Related Log', ondelete="cascade"),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'date': fields.datetime('Datetime', required=True),
        'log_info': fields.text(string='Info'),
    }

    _defaults = {
        'date': lambda *args: datetime.datetime.now(),
        'user_id': lambda self, cr, uid, ctx: uid
    }


class FieldFormatException(Exception):
    def __init__(self, field_name, log_field_format):
        self._field_name = field_name
        self._log_field_format = log_field_format

    def __str__(self):
        return self._field_name + ":" + self._log_field_format
