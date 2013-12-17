__author__ = 'cysnake4713'


def get_id_by_external_id(cr, pool, model, extends_id, context=None):
    record = pool.get('ir.model.data').search(cr, 1, [('model', '=', model), ('name', '=', extends_id)],
                                              context=context)
    record_id = pool.get('ir.model.data').read(cr, 1, record[0], ['res_id'], context=context)
    return record_id['res_id']


def get_parent_name(obj, rec_name='name'):
    if obj.parent_id:
        return get_parent_name(obj.parent_id) + '/' + obj.get(rec_name)
    else:
        return obj.get(rec_name)
