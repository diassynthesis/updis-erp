__author__ = 'cysnake4713'

import openerp.osv.orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


def _get_selection_translated(self, cr, uid, field_name, lang, selections, context=None):
    trans_obj = self.pool.get('ir.translation')
    name = '%s,%s' % (self._name, field_name)
    trans_ids = trans_obj.search(cr, uid, [
        ('name', '=', name),
        ('lang', '=', lang),
        ('type', '=', 'selection')
    ])
    trans_result = trans_obj.read(cr, uid, trans_ids, fields=['src', 'value'], context=context)
    trans = reduce(lambda x, y: dict(x, **{y['src']: y['value']}), trans_result, {})
    if not isinstance(selections, list):
        selections = selections(self, cr, uid, context)
    return map(lambda x: (x[0], trans[x[1]]) if x[1] in trans else x, selections)


def _get_field_type(self, cr, uid, column_info, context):
    column = column_info.column
    if column._type is 'boolean':
        return [column._type]
    elif column._type is 'integer':
        return [column._type]
    elif column._type is 'char':
        return [column._type]
    elif column._type is 'text':
        return [column._type]
    elif column._type is 'html':
        return [column._type]
    elif column._type is 'float':
        return [column._type]
    #TODO: date type return ??
    elif column._type is 'date':
        return [column._type, DEFAULT_SERVER_DATE_FORMAT]
    elif column._type is 'datetime':
        return [column._type, DEFAULT_SERVER_DATETIME_FORMAT]
    elif column._type is 'many2one':
        rec_name = self.pool.get(column._obj)._rec_name
        return [column._type, column._obj, rec_name]
    elif column._type is 'one2many':
        rec_name = self.pool.get(column._obj)._rec_name
        return [column._type, column._obj, rec_name]
    elif column._type is 'many2many':
        rec_name = self.pool.get(column._obj)._rec_name
        return [column._type, column._obj, rec_name]
    elif column._type is 'selection':
        selection = _get_selection_translated(self, cr, 1, column_info.name, 'zh_CN', column.selection,
                                              context)
        return [column._type, selection]
    else:
        return ['unknown']


def monkey_get_fields_type(self, cr, uid, request_fields, context=None):
    """
        used for phone get field type
        return format looks like:
                {
                    'field_name':['boolean'],
                    'field_name':['integer'],
                    'field_name':['char'],
                    'field_name':['text'],
                    'field_name':['html'],
                    'field_name':['float'],
                    'field_name':['date','Y m d'],
                    'field_name':['datetime','y m d hh:mm:ss],
                    'field_name':['many2one','related_obj','rec_name'],
                    'field_name':['one2many','related_obj','rec_name'],
                    'field_name':['many2many','related_obj','rec_name'],
                    'field_name':['selection',[('selection1','Value'),('selection2','Value')]],
                    'field_name':['unknown'],#else type all return unknown
                    ##related, function type will auto convert,
                }
    """
    #TODO:  1.Selection Type, when selection is function,not fully functional
    #TODO:  2.binary,reference,property Type is not impl

    result = {}
    for field_name in request_fields:
        if field_name in self._all_columns:
            result[field_name] = _get_field_type(self, cr, uid, self._all_columns[field_name], context)
        else:
            return False
    return result


openerp.osv.orm.BaseModel.get_fields_type = monkey_get_fields_type